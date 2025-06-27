import requests
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#Showdown name for better searching
def clean_species_name(name):
    name = name.strip().lower()
    name = re.sub(r"\s*\((m|f)\)$", "", name)
    name = name.replace(" ", "-").replace("’", "").replace(".", "").replace(":", "")
    name = name.replace("♂", "-m").replace("♀", "-f")

    manual_fixes = {
        "nidoran♂": "nidoran-m",
        "nidoran♀": "nidoran-f",
        "farfetchd": "farfetchd",
        "sirfetchd": "sirfetchd",
        "mr-mime": "mr-mime",
        "mime-jr": "mime-jr",
        "type-null": "type-null",
        "jangmo-o": "jangmo-o",
        "hakamo-o": "hakamo-o",
        "kommo-o": "kommo-o",
        "tapu-koko": "tapu-koko",
        "tapu-lele": "tapu-lele",
        "tapu-bulu": "tapu-bulu",
        "tapu-fini": "tapu-fini",
        "zacian-crowned": "zacian-crowned",
        "zamazenta-crowned": "zamazenta-crowned",
        "rotom-wash": "rotom-wash",
        "rotom-heat": "rotom-heat",
        "rotom-frost": "rotom-frost",
        "rotom-fan": "rotom-fan",
        "rotom-mow": "rotom-mow"
    }

    return manual_fixes.get(name, name)

#Get the top moves for a pokemon from Pikalytics
def get_top_moves_pikalytics(pokemon_name="incineroar", tier="gen9ou"):
    url = f"https://pikalytics.com/#/{tier}/pokemon/{pokemon_name.lower()}"
    print(f"Fetching Pikalytics data from: {url}")

    options = Options()
    driver = webdriver.Safari(options=options)
    driver.get(url)

    try:
        # Wait until move section loads
        move_table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "PokemonMoves_table__2V46W"))
        )

        rows = move_table.find_elements(By.TAG_NAME, "tr")[1:]  # skip header row
        moves = []
        for row in rows[:10]:  # top 10
            move_name = row.find_elements(By.TAG_NAME, "td")[0].text.strip()
            moves.append(move_name)

        print(f"Top moves for {pokemon_name}: {moves}")
        driver.quit()
        return moves

    except Exception as e:
        print(f"❌ Failed to fetch or parse data: {e}")
        driver.quit()
        return None

#Get base stats from pokeAPI
def get_base_stats(name):
    cleaned = clean_species_name(name)
    url = f"https://pokeapi.co/api/v2/pokemon/{cleaned}"
    res = requests.get(url)
    if res.status_code != 200:
        print(f"❌ Failed to get stats for: {name} ({url})")
        return None
    data = res.json()
    stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
    types = [t['type']['name'] for t in data['types']]
    return {"types": types, "stats": stats}

#Scrape from pokepaste URL
def parse_showdown_team(team_text):
    mons = []
    current = {}
    for line in team_text.strip().splitlines():
        line = line.strip()
        if not line:
            if current:
                mons.append(current)
                current = {}
            continue
        if line.startswith("- "):
            current.setdefault("moves", []).append(line[2:].strip())
        elif " @ " in line:
            name, item = line.split(" @ ")
            current["name"] = name.strip()
            current["item"] = item.strip()
        elif line.startswith("Ability:"):
            current["ability"] = line.split(":", 1)[1].strip()
        elif line.startswith("Level:"):
            current["level"] = int(line.split(":", 1)[1].strip())
        elif line.startswith("EVs:"):
            current["evs"] = line.split(":", 1)[1].strip()
        elif line.endswith("Nature"):
            current["nature"] = line.replace(" Nature", "").strip()
    if current:
        mons.append(current)
    return mons

#Helps load the team from the pokepaste URL
def load_team_from_url(url):
    if "pokepast.es" in url and not url.endswith("/raw"):
        url += "/raw"
    res = requests.get(url)
    res.raise_for_status()
    return res.text
