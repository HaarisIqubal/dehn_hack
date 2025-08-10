import psycopg2
# Database connection parameters
DB_HOST = "localhost"      # or your DB host
DB_PORT = "5432"
DB_NAME = "client1"
DB_USER = "haarisiqubal"
DB_PASS = "Haaris6626"

# Table creation SQL
CREATE_LB_TABLE = """
CREATE TABLE IF NOT EXISTS "Lösungsbibliothek" (
    "Prozessnummer" BIGINT PRIMARY KEY,
    "Prozessname" TEXT,
    "Prozessart" TEXT,
    "Merkmalsklasse 1" TEXT,
    "Merkmalsklasse 2" TEXT,
    "Merkmalsklasse 3" TEXT,
    "Randbedingung 1" TEXT,
    "Randbedingung 2" TEXT,
    "Verknüpfungen Prozessebene" TEXT,
    "Verknüpfungen Baukastenebene" TEXT,
    "Hinweise" TEXT,
    "Ablageort konstruktiv" TEXT,
    "Ablageort steuerungstechnisch" TEXT,
    "Ablageort prüftechnisch" TEXT,
    "Ablageort robotertechnisch" TEXT,
    "Prozessname_Embedded" vector(384)
);
"""

CREATE_BK_TABLE = """
CREATE TABLE IF NOT EXISTS "Baukasten" (
    "id" BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "Anwendungsfall" TEXT,
    "Lfd. Nummer" TEXT,
    "Version" TEXT,
    "Bauteilnamen" TEXT,
    "Bauteilkategorie" TEXT,
    "Hersteller" TEXT,
    "Typ" TEXT,
    "Eigenschaft 1" TEXT,
    "Wert 1" TEXT,
    "Eigenschaft 2" TEXT,
    "Wert 2" TEXT,
    "Eigenschaft 3" TEXT,
    "Wert 3" TEXT,
    "Ablageort konstruktiv" TEXT,
    "Ablageort steuerungstechnisch" TEXT,
    "Ablageort prüftechnisch" TEXT,
    "Ablageort robotertechnisch" TEXT,
    "Sonstiges" TEXT,
    "Spalte1" TEXT,
    "Embedding_Values" vector(384)
);
"""


def create_tables():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        # Create tables
        # cur.execute(CREATE_LB_TABLE)
        cur.execute(CREATE_BK_TABLE)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_tables()