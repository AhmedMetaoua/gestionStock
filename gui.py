import json
import tkinter as tk
from tkinter import END, messagebox, ttk
from PIL import Image, ImageTk
import csv
from tkinter import filedialog

from business_logic import (
    ajouter_matiere_premiere,
    modifier_quantite_matiere_premiere,
    ajouter_dosage,
    creer_bon_de_commande,
    creer_bon_livraison,
)
from db_manager import get_connection


def get_suggestions(table, column):
    """
    Récupère les suggestions depuis la base de données.
    
    Args:
        table (str): Nom de la table.
        column (str): Nom de la colonne.
    
    Returns:
        list: Liste des valeurs uniques de la colonne.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT {column} FROM {table}")
    suggestions = [row[0] for row in cursor.fetchall()]
    conn.close()
    return suggestions


def get_table_data(table):
    """
    Récupère toutes les données d'une table pour l'afficher dans un tableau.
    
    Args:
        table (str): Nom de la table.
    
    Returns:
        list: Liste des lignes de la table.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_historique_matiere_produite():
    """
    Récupère l'historique des matières produites depuis la base de données.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM historique_matiere_produite ORDER BY date_creation DESC")
        historique = cursor.fetchall()
        conn.close()
        return historique
    except Exception as e:
        raise Exception(f"Erreur lors de la récupération de l'historique : {e}")

def get_historique_bon_livraison():
    """
    Récupère l'historique des bons de livraison.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Récupérer l'historique des bons avec leurs détails
    cursor.execute("""
        SELECT bon_id, articles, total, client, date_creation
        FROM historique_bon_livraison
    """)
    historique = cursor.fetchall()
    conn.close()
    return historique

def lancer_interface():
    # Couleurs du thème (rendu un peu plus clair pour simuler la transparence)
    BG_COLOR = "#f8e1b3"  # Jaune clair avec un ton plus doux
    BTN_COLOR = "#ff4500"  # Rouge orangé
    BTN_TEXT_COLOR = "#ffffff"
    ENTRY_BG = "#ffffff"
    ENTRY_FG = "#000000"
    TABLE_BG = "#f5f5f5"  # Gris clair

    # Créer la fenêtre principale
    root = tk.Tk()
    root.title("Gestion de Stock")
    root.geometry("900x650")
    root.resizable(False, False)
    root.config(bg=BG_COLOR)

    # Charger l'image d'arrière-plan
    bg_image = Image.open("background.jpg")  # Placez une image d'agriculture nommée 'background.jpg'
    bg_image = bg_image.resize((1000, 700), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Canvas pour l'arrière-plan
    canvas = tk.Canvas(root, width=1000, height=700)
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Frame principale
    frame_principale = tk.Frame(root, bg=BG_COLOR)
    frame_principale.place(relx=0.5, rely=0.5, anchor="center", width=800, height=600)

    # Fonction pour afficher une section
    def afficher_section(section):
        for widget in frame_principale.winfo_children():
            widget.destroy()
        section()
    


    def exporter_donnees_csv():
        """
        Exporte toutes les données des tables dans des fichiers CSV distincts.
        """
        try:
            # Demander à l'utilisateur où sauvegarder les fichiers CSV
            dossier = filedialog.askdirectory(title="Sélectionnez le dossier pour l'exportation")
            if not dossier:
                return
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # Récupérer les noms des tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                # Récupérer les données et les colonnes de chaque table
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                column_names = [description[0] for description in cursor.description]
                
                # Définir le chemin du fichier CSV
                fichier_csv = f"{dossier}/{table}.csv"
                
                # Écrire dans le fichier CSV
                with open(fichier_csv, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(column_names)  # En-têtes
                    writer.writerows(rows)  # Données
                
                print(f"Table {table} exportée vers {fichier_csv}")
            
            conn.close()
            messagebox.showinfo("Succès", f"Exportation terminée dans le dossier : {dossier}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")


    # Menu principal
    menu = tk.Menu(root)
    root.config(menu=menu)

    # Sous-menu Gestion des Matières
    menu_gestion = tk.Menu(menu, tearoff=0)
    menu_gestion.add_command(label="Ajouter Matière Première", command=lambda: afficher_section(ajouter_matiere_premiere_ui))
    menu_gestion.add_command(label="Modifier Quantité", command=lambda: afficher_section(modifier_quantite_ui))
    menu_gestion.add_command(label="Ajouter Dosage", command=lambda: afficher_section(ajouter_dosage_ui))
    menu.add_cascade(label="Gestion des Matières Première", menu=menu_gestion)

    # Sous-menu Affichage
    menu_affichage = tk.Menu(menu, tearoff=0)
    menu_affichage.add_command(label="Afficher Tableau Matières", command=lambda: afficher_section(afficher_tableau_ui))
    menu_affichage.add_command(label="Historique Bon Des Commandes", command=lambda: afficher_section(afficher_historique_ui))
    menu_affichage.add_command(label="Historique des Bons de Livraison", command=lambda: afficher_section(afficher_historique_bon_livraison_ui))
    menu.add_cascade(label="Affichage", menu=menu_affichage)

    # Commandes supplémentaires
    menu.add_command(label="Créer Bon De Commande", command=lambda: afficher_section(bon_de_commande_ui))
    menu.add_command(label="Créer Bon de Livraison", command=lambda: afficher_section(creer_bon_livraison_ui))
    menu.add_command(label="Exporter en CSV", command=exporter_donnees_csv)


    # Section : Ajouter une matière première
    def ajouter_matiere_premiere_ui():
        tk.Label(frame_principale, text="Ajouter une Matière Première", font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=20)
        tk.Label(frame_principale, text="Nom :", bg=BG_COLOR, font=("Arial", 16)).pack()
        nom_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        nom_entry.pack(ipadx=10, ipady=5, pady=5)

        tk.Label(frame_principale, text="Référence :", bg=BG_COLOR, font=("Arial", 16)).pack()
        ref_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        ref_entry.pack(ipadx=10, ipady=5, pady=5)

        tk.Label(frame_principale, text="Quantité (Kg ou Litre):", bg=BG_COLOR, font=("Arial", 16)).pack()
        quantite_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        quantite_entry.pack(ipadx=10, ipady=5, pady=5)

        def ajouter():
            nom = nom_entry.get()
            ref = ref_entry.get()
            quantite = quantite_entry.get()
            try:
                ajouter_matiere_premiere(nom, ref, float(quantite))
                messagebox.showinfo("Succès", "Matière première ajoutée avec succès.")
                nom_entry.delete(0, END)
                ref_entry.delete(0, END)
                quantite_entry.delete(0, END)
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        tk.Button(frame_principale, text="Ajouter", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 18, "bold"), command=ajouter).pack(pady=20, ipadx=20, ipady=10)

    # Section : Modifier la quantité d'une matière première
    def modifier_quantite_ui():
        tk.Label(frame_principale, text="Ajout De Matière Première", font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=20)

        suggestions = get_suggestions("matieres_premieres", "nom") + get_suggestions("matieres_premieres", "reference")
        tk.Label(frame_principale, text="Nom ou Référence :", bg=BG_COLOR, font=("Arial", 16)).pack()
        identifiant_combobox = ttk.Combobox(frame_principale, values=suggestions, font=("Arial", 16))
        identifiant_combobox.pack()

        tk.Label(frame_principale, text="Quantité à Ajouter (Kg ou Litre) :", bg=BG_COLOR, font=("Arial", 16)).pack()
        quantite_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        quantite_entry.pack(ipadx=10, ipady=5, pady=5)

        def modifier():
            identifiant = identifiant_combobox.get()
            quantite = quantite_entry.get()
            try:
                modifier_quantite_matiere_premiere(identifiant, float(quantite))
                messagebox.showinfo("Succès", "Quantité modifiée avec succès.")
                identifiant_combobox.set('')
                quantite_entry.delete(0, END)
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        tk.Button(frame_principale, text="Ajouter", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 14, "bold"), command=modifier).pack(pady=16, ipadx=16, ipady=6)

    # Section : Ajouter un dosage
    def ajouter_dosage_ui():
        tk.Label(frame_principale, text="Ajouter un Dosage", font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=20)

        # Combobox pour les noms des matières produites
        matieres_produites = get_suggestions("matieres_produites", "nom")
        tk.Label(frame_principale, text="Produit Fini (Nom):", bg=BG_COLOR, font=("Arial", 16)).pack()
        matiere_produite_combobox = ttk.Combobox(frame_principale, values=matieres_produites, font=("Arial", 16))
        matiere_produite_combobox.pack(ipadx=10, ipady=5, pady=5)

        # Section pour les matières premières et quantités
        tk.Label(frame_principale, text="Matière Première (Nom)         Quantité (Kg/Litre)", bg=BG_COLOR, font=("Arial", 16)).pack()
        matieres_frame = tk.Frame(frame_principale, bg=BG_COLOR)
        matieres_frame.pack(pady=10)

        matieres_premieres = get_suggestions("matieres_premieres", "nom")

        def ajouter_matiere_premiere():
            frame = tk.Frame(matieres_frame, bg=BG_COLOR)
            frame.pack(fill="x", pady=5)

            matiere_premiere_combobox = ttk.Combobox(frame, values=matieres_premieres, font=("Arial", 14), width=30)
            matiere_premiere_combobox.pack(side="left", padx=5)

            quantite_entry = tk.Entry(frame, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 14), width=10)
            quantite_entry.pack(side="left", padx=5)

            remove_button = tk.Button(frame, text="X", font=("Arial", 12, "bold"), bg="red", fg="white",
                                    command=lambda: frame.destroy())
            remove_button.pack(side="left", padx=5)

        # Bouton pour ajouter une matière première
        tk.Button(frame_principale, text="Ajouter une Matière Première", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, 
                font=("Arial", 16), command=ajouter_matiere_premiere).pack(pady=10)

        # Ajouter une matière première initiale
        ajouter_matiere_premiere()

        def ajouter():
            matiere_produite = matiere_produite_combobox.get()
            dosages = []
            for child in matieres_frame.winfo_children():
                widgets = child.winfo_children()
                matiere_premiere = widgets[0].get()  # Combobox
                quantite = widgets[1].get()  # Entry
                if matiere_premiere and quantite:
                    dosages.append((matiere_premiere, float(quantite)))

            if not matiere_produite or not dosages:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
                return

            try:
                ajouter_dosage(matiere_produite, dosages)
                messagebox.showinfo("Succès", "Dosage ajouté avec succès.")
                matiere_produite_combobox.set('')
                for child in matieres_frame.winfo_children():
                    child.destroy()
                ajouter_matiere_premiere()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        tk.Button(frame_principale, text="Ajouter Dosage", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, 
                font=("Arial", 16, "bold"), command=ajouter).pack(pady=18, ipadx=18, ipady=8)

    # Section : Créer une matière produite
    def bon_de_commande_ui():
        tk.Label(frame_principale, text="Crée Bon De Commande", font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=20)

        matieres_produites = get_suggestions("matieres_produites", "nom")
        # Entrées pour ajouter un article

        tk.Label(frame_principale, text="Nom de Produit Fini :", bg=BG_COLOR, font=("Arial", 16)).pack()
        matiere_produite_combobox = ttk.Combobox(frame_principale, values=matieres_produites, font=("Arial", 14))
        matiere_produite_combobox.pack(ipadx=10, ipady=5, pady=5)

        tk.Label(frame_principale, text="Quantité (Kg ou Litre):", bg=BG_COLOR, font=("Arial", 16)).pack()
        qte_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        qte_entry.pack(ipadx=10, ipady=5, pady=5)

        tk.Label(frame_principale, text="Prix Unitaire :", bg=BG_COLOR, font=("Arial", 16)).pack()
        prix_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        prix_entry.pack(ipadx=10, ipady=5, pady=5)

        def creer():
            nom = matiere_produite_combobox.get()
            qte = qte_entry.get()
            prix = prix_entry.get()
            try:
                creer_bon_de_commande(nom, float(qte), float(prix))
                messagebox.showinfo("Succès", "Bon De Commande crée avec succès.")
                matiere_produite_combobox.set('')
                qte_entry.delete(0, END)
                prix_entry.delete(0, END)
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        tk.Button(frame_principale, text="Créer", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 16, "bold"), command=creer).pack(pady=18, ipadx=18, ipady=8)

    # Section : Créer un bon de livraison
    def creer_bon_livraison_ui():
        tk.Label(frame_principale, text="Créer Bon de Livraison", font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=20)
        
        # Liste des matières produites disponibles
        matieres_produites = get_suggestions("matieres_produites", "nom")

        # Table pour ajouter les articles
        columns = ("Produit Fini", "Quantité")
        treeview = ttk.Treeview(frame_principale, columns=columns, show="headings", height=4)
        for col in columns:
            treeview.heading(col, text=col, anchor="center")
            treeview.column(col, anchor="center", width=150)
        treeview.pack(pady=10, padx=20)

        # Entrées pour ajouter un article
        tk.Label(frame_principale, text="Produit Fini :", bg=BG_COLOR, font=("Arial", 14)).pack()
        matiere_produite_combobox = ttk.Combobox(frame_principale, values=matieres_produites, font=("Arial", 14))
        matiere_produite_combobox.pack(ipadx=10, ipady=5, pady=5)

        tk.Label(frame_principale, text="Quantité (Kg ou Litre):", bg=BG_COLOR, font=("Arial", 14)).pack()
        quantite_entry = tk.Entry(frame_principale, font=("Arial", 14))
        quantite_entry.pack(ipadx=10, ipady=5, pady=5)

        def ajouter_article():
            matiere_produite = matiere_produite_combobox.get()
            quantite = quantite_entry.get()
            if matiere_produite and quantite:
                treeview.insert("", "end", values=(matiere_produite, quantite))
                matiere_produite_combobox.set("")
                quantite_entry.delete(0, tk.END)

        tk.Button(frame_principale, text="Ajouter Article", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 14), command=ajouter_article).pack(pady=10)

        # Bouton pour créer le bon de livraison
        def creer_bon():
            articles = [
                {"matiere_produite_nom": treeview.item(item)["values"][0], "quantite": float(treeview.item(item)["values"][1])}
                for item in treeview.get_children()
            ]
            client = client_entry.get()
            if not client :
                messagebox.showinfo("Entrée manquante","Ajouter Des Article")
                return
            if not articles:
                messagebox.showinfo("Entrée manquante","Entrer Le Champs Client")
                return
            try:
                message = creer_bon_livraison(articles, client)
                messagebox.showinfo("Succès", message)
                treeview.delete(*treeview.get_children())
                client_entry.delete(0, END)
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        tk.Label(frame_principale, text="Client :", bg=BG_COLOR, font=("Arial", 16)).pack()
        client_entry = tk.Entry(frame_principale, bg=ENTRY_BG, fg=ENTRY_FG, font=("Arial", 16))
        client_entry.pack(ipadx=10, ipady=5, pady=5)

        tk.Button(frame_principale, text="Créer Bon de Livraison", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 16, "bold"), command=creer_bon).pack(pady=20, ipadx=10, ipady=5)

    # Section : Afficher un tableau pour les matières premières et produites
    def afficher_tableau_ui():
        style = ttk.Style()
        style.configure("Treeview", rowheight=20)  # Définit une hauteur de ligne de 40 pixels

        # Titre pour les matières premières
        tk.Label(frame_principale, text="Tableau des Matières Premières", font=("Arial", 18, "bold"), bg=BG_COLOR).pack(pady=10)
        
        # Récupérer les données des matières premières depuis la base de données
        matieres_premieres = get_table_data("matieres_premieres")

        # Tableau des matières premières
        columns_1 = ("ID", "Nom", "Référence", "Quantité")
        treeview_1 = ttk.Treeview(frame_principale, columns=columns_1, show="headings", height=7)
        treeview_1.pack(pady=8, padx=18)

        # Définir les en-têtes et colonnes
        column_widths = [100, 160, 160, 100]  # Largeurs spécifiques pour chaque colonne
        for col, width in zip(columns_1, column_widths):
            treeview_1.heading(col, text=col, anchor="center")
            treeview_1.column(col, anchor="center", width=width)
            
        # Configurer des couleurs pour les lignes
        style = ttk.Style()
        style.configure("Treeview", background="lightgray", fieldbackground="lightblue", foreground="black")
        
        # Remplir le tableau avec les données
        for row in matieres_premieres:
            treeview_1.insert("", "end", values=row)

        # Titre pour les matières produites
        tk.Label(frame_principale, text="Tableau des Produits Finis", font=("Arial", 18, "bold"), bg=BG_COLOR).pack(pady=10)

        # Récupérer les données des matières produites depuis la base de données
        matieres_produites = get_table_data("matieres_produites")

        # Tableau des matières produites
        columns_2 = ("ID", "Nom", "Référence", "Quantité", "Prix Unité")
        treeview_2 = ttk.Treeview(frame_principale, columns=columns_2, show="headings", height=7)
        treeview_2.pack(pady=8, padx=18)

        # Définir les en-têtes et colonnes
        column_widths = [100, 150, 180, 180, 100]  # Largeurs spécifiques pour chaque colonne
        for col, width in zip(columns_2, column_widths):
            treeview_2.heading(col, text=col, anchor="center")
            treeview_2.column(col, anchor="center", width=width)

        # Remplir le tableau avec les données
        for row in matieres_produites:
            treeview_2.insert("", "end", values=row)

        # Ajouter un bouton pour revenir à l'interface principale
        def retour():
            afficher_section(ajouter_matiere_premiere_ui)

        tk.Button(frame_principale, text="Retour", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 16, "bold"), command=retour).pack(pady=18, ipadx=18, ipady=8)
        


    # Section : Afficher un tableau pour l'historique des bon de commande
    def afficher_historique_ui():
        style = ttk.Style()
        style.configure("Treeview", rowheight=20)  # Définit une hauteur de ligne de 40 pixels

        # Titre
        tk.Label(frame_principale, text="Historique des Bon De Commande", font=("Arial", 20, "bold"), bg=BG_COLOR).pack(pady=18)
        
        # Récupérer l'historique depuis la base de données
        historique = get_historique_matiere_produite()

        # Tableau pour afficher l'historique
        columns = ("ID", "Nom", "Quantité", "Date de Création")
        treeview = ttk.Treeview(frame_principale, columns=columns, show="headings", height=12)
        treeview.pack(pady=10, padx=20)

        # Définir les en-têtes de colonnes
        column_widths = [100, 160, 100, 180]  # Largeurs spécifiques pour chaque colonne
        for col, width in zip(columns, column_widths):
            treeview.heading(col, text=col, anchor="center")
            treeview.column(col, anchor="center", width=width)

        # Remplir le tableau avec l'historique des matières produites
        for row in historique:
            treeview.insert("", "end", values=row)

        # Ajouter un bouton pour revenir à l'interface principale
        def retour():
            afficher_section(ajouter_matiere_premiere_ui)

        tk.Button(frame_principale, text="Retour", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 14, "bold"), command=retour).pack(pady=16, ipadx=16, ipady=8)


    def afficher_historique_bon_livraison_ui():

        style = ttk.Style()
        style.configure("Treeview", rowheight=45)  # Définit une hauteur de ligne de 40 pixels

        # Titre
        tk.Label(frame_principale, text="Historique des Bons de Livraison", font=("Arial", 20, "bold"), bg=BG_COLOR).pack(pady=18)

        # Récupérer l'historique depuis la base de données
        historique = get_historique_bon_livraison()

        # Tableau pour afficher l'historique
        columns = ("ID Bon", "Produites Finis", "Prix Total", "Client", "Date de Création")
        treeview = ttk.Treeview(frame_principale, columns=columns, show="headings", height=8)
        treeview.pack(pady=10, padx=20)

        # Définir les en-têtes de colonnes
        column_widths = [100, 200, 100, 100, 160]  # Largeurs spécifiques pour chaque colonne
        for col, width in zip(columns, column_widths):
            treeview.heading(col, text=col, anchor="center")
            treeview.column(col, anchor="center", width=width)

        # Remplir le tableau avec l'historique des bons de livraison
        for row in historique:
            bon_id, articles_json, total, client, date_creation = row

            # Convertir les articles JSON en texte lisible
            articles = json.loads(articles_json)
            articles_str = "\n".join([
                f"{article['nom']} (Quantité: {article['quantite']}, Total: {article['total']:.2f})"
                for article in articles
            ])

            treeview.insert("", "end", values=(bon_id, articles_str, f"{total:.2f}", client, date_creation))
        
        # Ajouter un bouton pour revenir à l'interface principale
        def retour():
            afficher_section(ajouter_matiere_premiere_ui)

        tk.Button(frame_principale, text="Retour", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 14, "bold"), command=retour).pack(pady=16, ipadx=16, ipady=6)

    # Lancer l'application avec une section par défaut
    afficher_section(ajouter_matiere_premiere_ui)
    root.mainloop()
