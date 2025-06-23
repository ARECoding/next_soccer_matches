import json
import requests
from bs4 import BeautifulSoup
from os import system
from rich.console import Console
from rich.table import Table


system("clear")

def get_soccer_next_events (sport = "Fútbol", player_or_team_name = ""):
    """
        Devuelve la informacion de los proximos partidos de futbol.
        Esta funcion obtiene la informacion directamente de la pagina Ole. En caso de no encontrar ningun evento devolvera None
    """
    soup = get_soup_from_page()
    if not soup:
        print("Fallo al conectarse a la pagina web.")
        return None

    try:
        element_found = soup.find(id="__NEXT_DATA__")
        raw_event_list = get_events_list_by_sport(element_found, sport)
        if not len(raw_event_list):
            print("There are no events for this sport")
            return None
        next_matches_list = []
        for raw_event in raw_event_list:
            for event in raw_event["eventos"]:
                next_matches_list.append(get_json_sport_event(event))
        next_matches_list = get_filtered_list_by_team(next_matches_list, player_or_team_name)
        if len(next_matches_list):
            createTableOutput(next_matches_list, player_or_team_name)
            return next_matches_list
    except BaseException as error:
        print(error)
        return None
    print("No se encontraron proximos partidos para este equipo o jugador")
    return None
    

def get_soup_from_page():
    url = "https://www.ole.com.ar/agenda-deportiva"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
    except Exception as exerror:
        print(exerror)
        return None;


def get_events_list_by_sport(element_found, sport_category):
    """Recibe un elemento html que contiene la informacion de los eventos y crea una lista con los elementos filtrados por el deporte, en caso de que no se indique el deporte devolvera los eventos de Fútbol"""
    page_dict_data = json.loads(  element_found.string)
    events_data = page_dict_data["props"]["pageProps"]["matchConfig"]["properties"]["service"]["data"]["dates"]
    raw_sport_events_list = []
    for events_data_index, events_data_value in enumerate(events_data):
        for key, value in enumerate(events_data_value["torneos"]):
            if value["deporte"]["nombre"] == sport_category:
                raw_sport_events_list.append(value)
    if not len(raw_sport_events_list):
        return []
    return raw_sport_events_list

def get_json_sport_event(raw_data):
    """Recibe un diccionario con los datos encontrados en la pagina sobre las competencias y retorna un objeto en formato JSON con el nombre del evento, la fecha con horario donde se juega y el canal donde lo transmite"""
    data = {
        "match_title": raw_data["nombre"],
        "date": raw_data["fecha"],
        "channel": list(map(lambda canal : canal["nombre"], raw_data["canales"]))
    }
    return json.dumps(data)

def get_filtered_list_by_team(matches_json, player_or_team_name):
    player_or_team_name = player_or_team_name.lower()
    if player_or_team_name == "":
        return matches_json
    filtered_list = []
    for match_json in matches_json:
        if player_or_team_name in json.loads(match_json)["match_title"].lower():
            filtered_list.append(match_json)        
    return filtered_list

def createTableOutput (next_matches_list, player_or_team_name):
    table_title = "" if player_or_team_name == "" else f"de {player_or_team_name}"
    table = Table(title=f"Proximos partidos {table_title}:\n")    
    table.add_column("Partido")
    table.add_column("Horario")
    table.add_column("Canales")
    for next_match in next_matches_list:        
        table.add_row(f"{json.loads(next_match)["match_title"]}", f"{json.loads(next_match)["date"]}", f"{json.loads(next_match)["channel"]}")
    console = Console()
    console.print(table)

print(get_soccer_next_events(player_or_team_name="river"), end="\n\n")