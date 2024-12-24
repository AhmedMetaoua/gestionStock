from db_manager import get_connection
import datetime

def ajouter_matiere_premiere(nom, reference, quantite):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM matieres_premieres WHERE nom = ? and reference = ?", (nom, reference,))
    matiere_premiere_id = cursor.fetchone()
    if matiere_premiere_id:
        conn.close()
        raise ValueError(f"Matière première '{nom}' existe déja.")
    cursor.execute("INSERT INTO matieres_premieres (nom, reference, quantite) VALUES (?, ?, ?)", (nom, reference, quantite))
    conn.commit()
    conn.close()

def modifier_quantite_matiere_premiere(identifiant, quantite):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Essayer de mettre à jour par référence
    cursor.execute("UPDATE matieres_premieres SET quantite = quantite + ? WHERE reference = ?", (quantite, identifiant))
    if cursor.rowcount == 0:
        # Si aucune correspondance, essayer par nom
        cursor.execute("UPDATE matieres_premieres SET quantite = quantite + ? WHERE nom = ?", (quantite, identifiant))
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Matière première avec identifiant '{identifiant}' introuvable.")

    conn.commit()
    conn.close()

def ajouter_dosage(nom_matiere_produite, dosages):
    """
    Ajoute des dosages pour une matière produite avec plusieurs matières premières.

    :param nom_matiere_produite: Nom de la matière produite
    :param dosages: Liste de tuples (nom_matiere_premiere, proportion)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Référence de la matière produite
    matiere_produite_reference = f"REF-{nom_matiere_produite.upper()}"

    for nom_matiere_premiere, proportion in dosages:
        # Récupérer l'ID de la matière première
        cursor.execute("SELECT id FROM matieres_premieres WHERE nom = ?", (nom_matiere_premiere,))
        matiere_premiere_id = cursor.fetchone()
        if not matiere_premiere_id:
            conn.close()
            raise ValueError(f"Matière première '{nom_matiere_premiere}' introuvable.")
        matiere_premiere_id = matiere_premiere_id[0]

        # Vérifier si ce dosage existe déjà
        cursor.execute("""SELECT id FROM dosages WHERE matiere_produite_reference = ? AND matiere_premiere_id = ?""", 
                       (matiere_produite_reference, matiere_premiere_id))
        if cursor.fetchone():
            cursor.execute("UPDATE dosages SET proportion = ? WHERE matiere_produite_reference = ? and matiere_premiere_id = ?", 
                           (proportion, matiere_produite_reference, matiere_premiere_id))
        else:
            # Ajouter le dosage
            cursor.execute("INSERT INTO dosages (matiere_produite_reference, matiere_premiere_id, proportion) VALUES (?, ?, ?)",
                           (matiere_produite_reference, matiere_premiere_id, proportion))

    conn.commit()
    conn.close()


def creer_bon_de_commande(nom, quantite, prix):
    conn = get_connection()
    cursor = conn.cursor()

    # Récupérer les dosages pour cette matière produite
    cursor.execute("SELECT reference FROM matieres_produites WHERE nom = ?", (nom,))
    result = cursor.fetchone()
    matiere_produite_reference = result[0] if result else None

    if not matiere_produite_reference:
        cursor.execute("INSERT INTO matieres_produites (nom, reference, quantite, prix_unitaire) VALUES (?, ?, ?, ?)",
                    (nom, f"REF-{nom.upper()}", 0, prix))  # Initialise avec quantité = 0
        matiere_produite_reference = f"REF-{nom.upper()}"

    cursor.execute("SELECT matiere_premiere_id, proportion FROM dosages WHERE matiere_produite_reference = ?", (matiere_produite_reference,))
    dosages = cursor.fetchall()
    if not dosages:
        raise ValueError(f"Erreur : Aucun dosage trouvé pour la matière produite : {nom}")

    # Liste pour garder trace des modifications déjà effectuées
    modifications = []

    # Vérifier et réduire les quantités
    for matiere_premiere_id, proportion in dosages:
        cursor.execute("SELECT quantite FROM matieres_premieres WHERE id = ?", (matiere_premiere_id,))
        quantite_disponible = cursor.fetchone()[0]
        quantite_necessaire = quantite * proportion

        if quantite_disponible < quantite_necessaire:
            # Annuler toutes les modifications précédentes
            for ancien_id, ancienne_quantite in modifications:
                cursor.execute("UPDATE matieres_premieres SET quantite = quantite + ? WHERE id = ?", 
                            (ancienne_quantite, ancien_id))
            raise ValueError(f"Quantité insuffisante pour la matière première ID {matiere_premiere_id}. Les modifications ont été annulées.")

        # Effectuer la réduction et enregistrer la modification
        cursor.execute("UPDATE matieres_premieres SET quantite = quantite - ? WHERE id = ?", 
                    (quantite_necessaire, matiere_premiere_id))
        modifications.append((matiere_premiere_id, quantite_necessaire))

    # Ajouter la quantité produite
    cursor.execute("UPDATE matieres_produites SET quantite = quantite + ?, prix_unitaire = ? WHERE reference = ?", 
                (quantite, prix, matiere_produite_reference))
    # Ajouter l'entrée dans l'historique
    cursor.execute("INSERT INTO historique_matiere_produite (nom, quantite) VALUES (?, ?)", 
                (nom, quantite))
    
    conn.commit()
    conn.close()


def creer_bon_livraison(matiere_produite_nom, quantite, clien):
    conn = get_connection()
    cursor = conn.cursor()

    # Vérifier la disponibilité de la matière produite
    cursor.execute("SELECT id, quantite FROM matieres_produites WHERE nom = ?", (matiere_produite_nom,))
    result = cursor.fetchone()
    if not result:
        raise ValueError("Matière produite non trouvée")
    
    matiere_produite_id, quantite_disponible = result

    if quantite_disponible < quantite:
        raise ValueError("Quantité insuffisante pour le bon de livraison")

    # Réduire la quantité de la matière produite
    cursor.execute("UPDATE matieres_produites SET quantite = quantite - ? WHERE id = ?", (quantite, matiere_produite_id))

    # Créer un bon de livraison
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO bons_livraison (matiere_produite_id, quantite, date, client) VALUES (?, ?, ?, ?)",
                   (matiere_produite_id, quantite, date, clien))

    # Générer un ID pour la facture
    bon_id = cursor.lastrowid
    facture = generer_facture(bon_id, matiere_produite_nom, quantite, clien)

    conn.commit()
    conn.close()
    return facture

def generer_facture(bon_id, matiere_produite_nom, quantite, clien):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT prix_unitaire FROM matieres_produites WHERE nom = ?", (matiere_produite_nom,))
    result = cursor.fetchone()[0]
    # Exemple simple de génération de facture
    facture = f"""
    BON DE LIVRAISON N° {bon_id}
    ---------------------------
    Clien : {clien}
    Date : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    Produit : {matiere_produite_nom}
    Quantité : {quantite}
    Prix/Unité : {result}
    Total : {float(result) * quantite}

    Merci pour votre collaboration.
    """
    # Optionnel : Sauvegarder la facture dans un fichier texte
    with open(f"facture_{bon_id}.txt", "w", encoding="utf-8") as file:
        file.write(facture)

    conn.commit()
    conn.close()
    return facture
