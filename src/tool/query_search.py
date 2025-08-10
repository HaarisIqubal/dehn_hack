from .encoding_model import sentence_modelling
from .db import Database

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
            SELECT "id", "Anwendungsfall", "Lfd. Nummer", "Version", "Bauteilnamen",
                1 - ("Embedding_Values" <=> %s::vector) AS similarity
            FROM "Baukasten"
            ORDER BY "Embedding_Values" <=> %s::vector
            LIMIT %s
        """
    params = (query_vector, query_vector, top_k)
    db = Database()
    result = db.execute_query(query_baukasten, params)
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
    for item in process_names_final:
        all_baukasten_list.append(search_baukasten(item[-1]))
    seen_ids = set()
    unique_tuples = []
    print(all_baukasten_list)
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
