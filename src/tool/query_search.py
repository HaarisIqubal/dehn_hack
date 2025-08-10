from .encoding_model import sentence_modelling
from .db import Database
import pandas as pd

def search_losungbib(query_text, top_k=5)-> list[tuple]:
    query_embed = sentence_modelling.embed_text(query_text)
    query_losung = """
                SELECT "Prozessnummer", "Prozessname", "Prozessart","Merkmalsklasse 1","Merkmalsklasse 2", "Merkmalsklasse 3", "Randbedingung 1","Randbedingung 2","Verknüpfungen Prozessebene","Verknüpfungen Baukastenebene",
                    1 - ("Prozessname_Embedded" <=> %s::vector) AS similarity
                FROM "Lösungsbibliothek"
                ORDER BY "Prozessname_Embedded" <=> %s::vector
                LIMIT %s
            """
    params = (query_embed, query_embed, top_k)
    db = Database()
    losung_query = db.execute_query(query_losung, params, fetch=True)
    db.close()
    return losung_query

def search_list_process(id_list) -> list:
    query_process = """
                SELECT "Prozessnummer", "Prozessname", "Prozessname_Embedded"
                FROM "Lösungsbibliothek"
                WHERE "Prozessnummer" = ANY(%s)
            """
    params = (id_list,)
    db = Database()
    result = db.execute_query(query_process, params=params, fetch=True)
    db.close()
    return result

def search_baukasten(query_vector, top_k=10) -> list[tuple]:
    # Create embedding
    query_baukasten = """
            SELECT "Lfd. Nummer", "Bauteilnamen", "Hersteller", "Typ",
                1 - ("Embedding_Values" <=> %s::vector) AS similarity
            FROM "Baukasten"
            ORDER BY "Embedding_Values" <=> %s::vector
            LIMIT %s
        """
    params = (query_vector, query_vector, top_k)
    db = Database()
    result = db.execute_query(query_baukasten, params, fetch=True)
    db.close()
    return result

def sepearte_out_process(all_process):
    all_haupt_process = [x for x in all_process if x[2] == "Hauptprozess" and x[-1] > 0.5]
    all_teil_process = [x for x in all_process if x[2] == "Teilprozess"]
    # Getting the values of subsequent array values from the data 
    get_haupt_process_sub_array = []
    for item in all_haupt_process:
        #check if the process values is gives
        mid_process = item[8]
        if len(mid_process) > 0:
            break
        # If there is no mid process gives for certain haupt process check the library inside it
        haupt_process_name = item[1]
        get_subs_haupt_process = search_losungbib(haupt_process_name)
    #Getting the values of Verknüpfungen
    mid_process = all_haupt_process[0][8]
    all_processes_id = parse_number_range(mid_process)
    for haput in all_haupt_process:
        all_processes_id.append(haput[0])

    all_processes_id = set(all_processes_id)
    all_processes_id = list(all_processes_id)
    process_names_final = search_list_process(all_processes_id)
    all_baukasten_list = []
    print(process_names_final)
    for item in process_names_final:
        all_baukasten_list.append(search_baukasten(item[-1]))
    seen_ids = set()
    unique_tuples = []
    for sublist in all_baukasten_list:
        if isinstance(sublist,list):
            for tup in sublist:
                id_ = tup[0]
                if id_ not in seen_ids:
                    seen_ids.add(id_)
                    unique_tuples.append(tup)
    return unique_tuples




def parse_number_range(num_str):
    # Remove extra spaces
    num_str = num_str.strip()

    if "-" in num_str:
        # Handle range
        start_str, end_str = num_str.replace(" ", "").split("-")
        start_num, end_num = int(start_str), int(end_str)
        return list(range(start_num, end_num + 1))
    else:
        # Handle single number
        return [int(num_str)]

def final_output():
    loesungbibliothek = pd.read_csv("src/data/losungbib.csv")
    baukasten_df = pd.read_csv('src/data/baukasten.csv', header=None)
    baukasten_df = baukasten_df.drop(index=0).reset_index(drop=True)
    baukasten_df.columns = baukasten_df.iloc[0]
    baukasten_df =baukasten_df.drop(index=0).reset_index(drop=True)
    baukasten_df.drop(columns=["Notizen"], inplace=True)

    HAUPTPROZESS_ID = "100000"  # change if you want another Hauptprozess

    # ---------- helpers ----------
    norm = lambda s: str(s).strip().casefold()

    def get_teilprozesse_for_haupt(loesung_df: pd.DataFrame, haupt_num_str: str) -> pd.DataFrame:
        """
        Return Teilprozesse rows belonging to one Hauptprozess.
        Uses numeric window between this Haupt and the next Haupt.
        Expects columns: Prozessnummer, Prozessart, Prozessname, Merkmalsklasse 1/2 (if available).
        """
        df = loesung_df.copy()
        df["Prozessnummer"] = df["Prozessnummer"].astype(str).str.strip()
        df["Prozessnummer_num"] = pd.to_numeric(df["Prozessnummer"], errors="coerce")
        is_haupt = df["Prozessart"].astype(str).str.strip().eq("Hauptprozess")
        is_teil  = df["Prozessart"].astype(str).str.strip().eq("Teilprozess")

        main = df[is_haupt & df["Prozessnummer"].eq(haupt_num_str)]
        if main.empty:
            raise ValueError(f"Hauptprozess {haupt_num_str} not found.")

        main_num = float(main["Prozessnummer_num"].iloc[0])

        dfs = df.sort_values("Prozessnummer_num", kind="mergesort").reset_index(drop=True)
        idx_haupt = dfs.index[dfs["Prozessart"].astype(str).str.strip().eq("Hauptprozess")].tolist()
        pos_list = dfs.index[dfs["Prozessnummer"].eq(haupt_num_str)].tolist()
        if not pos_list:
            raise ValueError(f"Hauptprozess {haupt_num_str} not found after sorting.")
        pos = pos_list[0]
        next_after = [i for i in idx_haupt if i > pos]
        upper_bound = dfs.loc[next_after[0], "Prozessnummer_num"] if next_after else np.inf

        teil = dfs[
            (dfs["Prozessart"].astype(str).str.strip().eq("Teilprozess")) &
            (dfs["Prozessnummer_num"] > main_num) &
            (dfs["Prozessnummer_num"] < upper_bound)
        ].copy()

        keep_cols = [c for c in ["Prozessnummer","Prozessname","Prozessart","Merkmalsklasse 1","Merkmalsklasse 2"] if c in teil.columns]
        return teil[keep_cols]

    # Mapping: Merkmalsklasse token -> expected Baukasten categories
    # Tweak to match your baukasten_df["Bauteilkategorie"].unique()
    MERKMAL_TO_CATS = {
        "Drucken": {"Etikettendrucker", "NiceLabel"},
        "Bereitstellen": {"Mechanische Anbindung", "Pneumatiksystem"},
        "Aufnehmen": {"Greifer/Sauger", "Pneumatiksystem", "Mechanische Anbindung"},
        "Manipulieren": {"Greifer/Sauger", "Pneumatiksystem", "Mechanische Anbindung"},
        "Greifen": {"Greifer/Sauger", "Pneumatiksystem", "Mechanische Anbindung"},
        "Kontrollieren": {"Prüfsystem", "Vision Sensoren", "Optischer Sensor"},
        "Erkennen": {"Vision Sensoren", "Optischer Sensor", "Prüfsystem"},
        "Auswerten": {"Prüfsystem", "Vision Sensoren"},
        "Korrigieren": {"Roboter"},
        "Applizieren": {"Roboter", "Mechanische Anbindung"},
    }

    def cats_from_merkmalsklassen(row: pd.Series) -> set:
        cats = set()
        for col in ("Merkmalsklasse 1", "Merkmalsklasse 2"):
            if col in row and pd.notna(row[col]):
                token = str(row[col]).strip()
                # normalize to TitleCase for mapping keys
                token_key = token[:1].upper() + token[1:].lower()
                if token_key in MERKMAL_TO_CATS:
                    cats |= MERKMAL_TO_CATS[token_key]
        return cats

    # ---------- choose candidate set ----------
    # Prefer your ID-filtered candidates from Cell 28; else fall back to full Baukasten
    if "filtered_baukasten_for_query" in globals():
        candidates_df = filtered_baukasten_for_query.copy()
    else:
        candidates_df = baukasten_df.copy()

    # Optionally exclude software/docs categories (comment out if you want everything)
    exclude_cats = {
        "Roboterdokumente (KUKA)",
        "Roboterprogramm (KUKA)",
        "Robotersoftware (KUKA)",
        "SPS-Datenbaustein (SIEMENS)",
        "SPS-Datentyp (SIEMENS)",
    }
    if "Bauteilkategorie" in candidates_df.columns:
        candidates_df = candidates_df[~candidates_df["Bauteilkategorie"].astype(str).str.strip().isin(exclude_cats)].copy()

    # ---------- build per-Teilprozess component list ----------
    teil_100000 = get_teilprozesse_for_haupt(loesungbibliothek, HAUPTPROZESS_ID)

    rows = []
    for _, tp in teil_100000.iterrows():
        t_id = str(tp["Prozessnummer"]).strip()
        t_name = str(tp["Prozessname"]).strip()

        expected_cats = cats_from_merkmalsklassen(tp)
        if expected_cats and "Bauteilkategorie" in candidates_df.columns:
            mask = candidates_df["Bauteilkategorie"].notna() & candidates_df["Bauteilkategorie"].map(norm).isin({norm(c) for c in expected_cats})
            kept = candidates_df[mask].copy()
        else:
            # If no Merkmalsklasse hit, keep all for now (or set kept = candidates_df.iloc[0:0] to keep none)
            kept = candidates_df.copy()

        keep_cols = [c for c in ["Lfd. Nummer","Bauteilnamen","Bauteilkategorie","Hersteller","Typ"] if c in kept.columns]
        tmp = kept[keep_cols].copy()
        tmp.insert(0, "Teilprozessnummer", t_id)
        tmp.insert(1, "Teilprozessname", t_name)
        rows.append(tmp)

        per_process_components = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(
            columns=["Teilprozessnummer","Teilprozessname","Lfd. Nummer","Bauteilnamen","Bauteilkategorie","Hersteller","Typ"]
        )

    # Optional: compact counts per teilprozess
    component_counts = (
        per_process_components
        .groupby(["Teilprozessnummer","Teilprozessname"])["Lfd. Nummer"]
        .nunique()
        .reset_index(name="UniqueComponents")
    )

    # ---- outputs you can use downstream ----
    # per_process_components : long table of components per teilprozess
    # component_counts       : count summary per teilprozess

    print("[OK] Built component list per Teilprozess for HP", HAUPTPROZESS_ID)
    print(component_counts.to_string(index=False))
    # display(per_process_components.head(20))  # uncomment in Jupyter to preview
    return component_counts