import os
import json

# CESTY K PROJEKTU-

# Hlavný priečinok projektu (kde je main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(BASE_DIR)

# Cesty k folderom
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMG_DIR = os.path.join(ASSETS_DIR, "img")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
FONT_DIR = os.path.join(ASSETS_DIR, "Font")
DATA_DIR = os.path.join(BASE_DIR, "data")

# FUNKCIE NA SÚBORY
def get_path(*parts):
    return os.path.join(BASE_DIR, *parts)

def load_json(filename, default=None):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"[WARN] Súbor {filename} neexistuje — použijem predvolenú hodnotu.")
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Chyba pri čítaní '{filename}': {e}")
        return default if default is not None else {}

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Chyba pri zapisovaní '{filename}': {e}")

def save_game_config_file(game_name):
    config = load_json("game_config.json", {"active_game": "unknown"})
    config["active_game"] = game_name
    save_json("game_config.json", config)


# FUNKCIE KONKRÉTNE PRE HRY
def save_game_config(active_game, map_image):
    config = {"active_game": active_game, "map_image": map_image}
    save_json("game_config.json", config)

def load_game_config():
    config = load_json("game_config.json", {"active_game": "unknown", "map_image": None})
    return config.get("active_game", "unknown"), config.get("map_image", None)

def load_score():
    data = load_json("skore.json", {"skore": 0, "cas": 0})
    return data.get("skore", 0), data.get("cas", 0)

def load_best(file_name):
    data = load_json(file_name, {"best": 0})
    return data.get("best", 0)

def save_score(score, elapsed_time):
    save_json("skore.json", {
        "skore": score,
        "cas": int(elapsed_time)
    })



# AUTO VYTVORENIE PRIEČINKOV
for folder in [ASSETS_DIR, IMG_DIR, MUSIC_DIR, FONT_DIR, DATA_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# DEBUG LOGOVANIE
print("\n===== PATH CHECK =====")
print("BASE_DIR:", BASE_DIR)
print("FONT_DIR:", FONT_DIR, "→ exists:", os.path.exists(FONT_DIR))
print("IMG_DIR:", IMG_DIR, "→ exists:", os.path.exists(IMG_DIR))
print("DATA_DIR:", DATA_DIR, "→ exists:", os.path.exists(DATA_DIR))
print("======================\n")
