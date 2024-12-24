import sqlite3

DB_NAME = "stock_management.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Table des matières premières
    # cursor.execute('''DELETE FROM matieres_premieres WHERE id = ?;''', (9,))
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
    # cursor.execute('''DROP TABLE IF EXISTS bons_livraison;''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bons_livraison (
        id INTEGER PRIMARY KEY,
        matiere_produite_id INTEGER ,
        quantite REAL ,
        date TEXT ,
        client TEXT NOT NULL,
        FOREIGN KEY (matiere_produite_id) REFERENCES matieres_produites(id)
    )''')

    # Table d'historique de bon de commande'
    cursor.execute('''CREATE TABLE IF NOT EXISTS historique_matiere_produite (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        quantite REAL NOT NULL,
        date_creation DEFAULT CURRENT_TIMESTAMP
    )''')

    # Table d'historique de bon de livraison'
    # cursor.execute("ALTER TABLE historique_bon_livraison ADD COLUMN articles TEXT;")
    # cursor.execute('''DROP TABLE IF EXISTS historique_bon_livraison;''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS historique_bon_livraison (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bon_id INTEGER NOT NULL,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        client TEXT NOT NULL,
        total REAL NOT NULL,
        articles TEXT,
        FOREIGN KEY (bon_id) REFERENCES bons_livraison (id)
    )''')

        # matiere_produite_nom TEXT NOT NULL,
        # quantite REAL NOT NULL,
    cursor.execute('''CREATE TABLE IF NOT EXISTS details_bon_livraison (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bon_livraison_id INTEGER,
        matiere_produite_id INTEGER,
        quantite REAL,
        FOREIGN KEY (bon_livraison_id) REFERENCES bons_livraison(id),
        FOREIGN KEY (matiere_produite_id) REFERENCES matieres_produites(id)
    )''')


    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_NAME)
