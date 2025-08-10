"""Script file for adding data inside database and initialization functions."""
import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from .encoding_model import sentence_modelling

class Database:
    def __init__(self, env_path='.env'):
        # Load environment variables
        load_dotenv(env_path)
        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')
        self.dbname = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.conn = None
        self.create_init_db()
        self.initialize_db_with_data()

    def connect(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
        return self.conn
    
    def create_init_db(self):
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

        self.execute_query(CREATE_BK_TABLE)
        self.execute_query(CREATE_LB_TABLE)

    def get_cursor(self, dict_cursor=False):
        conn = self.connect()
        if dict_cursor:
            return conn.cursor(cursor_factory=RealDictCursor)
        else:
            return conn.cursor()

    def execute_query(self, query, params=None, fetch=False, dict_cursor=False):
        """
        Executes a query, optionally fetches results.
        Returns fetched data if fetch=True else None.
        """
        with self.get_cursor(dict_cursor=dict_cursor) as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            else:
                self.conn.commit()

    def initialize_db_with_data(self):
        """Filling the database with csv data files"""
        get_losung_data = self.execute_query("""
                                             SELECT * FROM "Lösungsbibliothek"
                                             """,fetch=True)
        get_baukasten_data = self.execute_query("""
                                                SELECT * FROM "Baukasten"
                                                """, fetch=True)
        if len(get_losung_data) <= 0:
            print("Adding data to biblothek")
            losung_bib = pd.read_csv("src/data/losungbib.csv")
            losung_bibliothek_field_req = ["Prozessnummer", "Prozessname", "Prozessart","Merkmalsklasse 1","Merkmalsklasse 2", "Merkmalsklasse 3", "Randbedingung 1","Randbedingung 2","Verknüpfungen Prozessebene","Verknüpfungen Baukastenebene"]
            los_val = losung_bib[losung_bibliothek_field_req]
            insert_query = """INSERT INTO "Lösungsbibliothek" (
                    "Prozessnummer", "Prozessname", "Prozessart","Merkmalsklasse 1","Merkmalsklasse 2", "Merkmalsklasse 3", "Randbedingung 1","Randbedingung 2","Verknüpfungen Prozessebene","Verknüpfungen Baukastenebene", "Prozessname_Embedded")
                VALUES (%s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s)"""
            for _, items in los_val.iterrows():
                items["Prozessname_Embedded"] = sentence_modelling.embed_text(items["Prozessname"])
                params = (items["Prozessnummer"],items["Prozessname"],items["Prozessart"], items["Merkmalsklasse 1"],items["Merkmalsklasse 2"], items["Merkmalsklasse 3"], items["Randbedingung 1"],items["Randbedingung 2"],items["Verknüpfungen Prozessebene"],items["Verknüpfungen Baukastenebene"], items["Prozessname_Embedded"])
                self.execute_query(insert_query, params)
        if len(get_baukasten_data) <= 0:
            print("Add data to baukasten")
            baukasten = pd.read_csv('src/data/baukasten.csv', header=None)
            baukasten = baukasten.drop(index=0).reset_index(drop=True)
            baukasten.columns = baukasten.iloc[0]
            baukasten =baukasten.drop(index=0).reset_index(drop=True)
            baukasten.drop(columns=["Notizen"], inplace=True)

            insert_baukasten = """
            INSERT INTO "Baukasten" (
            "Anwendungsfall", "Lfd. Nummer", "Version", "Bauteilnamen",
            "Bauteilkategorie", "Hersteller", "Typ", "Eigenschaft 1", "Wert 1",
            "Eigenschaft 2", "Wert 2", "Eigenschaft 3", "Wert 3",
            "Ablageort konstruktiv", "Ablageort steuerungstechnisch",
            "Ablageort prüftechnisch", "Ablageort robotertechnisch", "Sonstiges",
            "Spalte1", "Embedding_Values")
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s)"""

            for _, item in baukasten.iterrows():
                making_whole_row_embed_string = f" {item['Bauteilnamen']} {item['Bauteilkategorie']} {item['Hersteller']} {item['Typ']} {item['Eigenschaft 1']}"
                item["Embedding_Values"] = sentence_modelling.embed_text(making_whole_row_embed_string)
                params = (item["Anwendungsfall"], item["Lfd. Nummer"], item["Version"], item["Bauteilnamen"],
                    item["Bauteilkategorie"], item["Hersteller"], item["Typ"], item["Eigenschaft 1"], item["Wert 1"],
                    item["Eigenschaft 2"], item["Wert 2"], item["Eigenschaft 3"], item["Wert 3"],
                    item["Ablageort konstruktiv"], item["Ablageort steuerungstechnisch"],
                    item["Ablageort prüftechnisch"], item["Ablageort robotertechnisch"], item["Sonstiges:"],
                    item["Spalte1"], item["Embedding_Values"])
                self.execute_query(insert_baukasten,params=params)
        self.close()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None