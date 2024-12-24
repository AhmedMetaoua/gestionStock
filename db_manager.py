import sqlite3

DB_NAME = "stock_management.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Table des matières premières
    cursor.execute('''CREATE TABLE IF NOT EXISTS matieres_premieres (
        id INTEGER PRIMARY KEY,
        nom TEXT NOT NULL,
        reference TEXT UNIQUE NOT NULL,
        quantite REAL NOT NULL
    )''')

    # Table des matières produites
    cursor.execute('''CREATE TABLE IF NOT EXISTS matieres_produites (
        id INTEGER PRIMARY KEY,
        nom TEXT NOT NULL,
        reference TEXT UNIQUE NOT NULL,
        quantite REAL NOT NULL,
        prix_unitaire REAL NOT NULL
    )''')

    # Table des dosages
    cursor.execute('''CREATE TABLE IF NOT EXISTS dosages (
        id INTEGER PRIMARY KEY,
        matiere_produite_reference TEXT NOT NULL,
        matiere_premiere_id INTEGER NOT NULL,
        proportion REAL NOT NULL,
        FOREIGN KEY (matiere_produite_reference) REFERENCES matieres_produites(reference),
        FOREIGN KEY (matiere_premiere_id) REFERENCES matieres_premieres(id)
    )''')


    # Table des bons de livraison
    cursor.execute('''CREATE TABLE IF NOT EXISTS bons_livraison (
        id INTEGER PRIMARY KEY,
        matiere_produite_id INTEGER NOT NULL,
        quantite REAL NOT NULL,
        date TEXT NOT NULL,
        client TEXT NOT NULL,
        FOREIGN KEY (matiere_produite_id) REFERENCES matieres_produites(id)
    )''')

    # Table d'historique de bon de commande'
    cursor.execute('''CREATE TABLE IF NOT EXISTS historique_matiere_produite (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        quantite REAL NOT NULL,
        date_creation    DEFAULT CURRENT_TIMESTAMP
    )''')

    # Table d'historique de bon de livraison'
    cursor.execute('''CREATE TABLE historique_bon_livraison (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reference TEXT NOT NULL,
        client TEXT NOT NULL,
        articles TEXT NOT NULL, -- JSON ou texte contenant les détails des articles
        total REAL NOT NULL
    )''')
    


    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_NAME)
