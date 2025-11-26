import os
import json

# -------------------------
# CESTY K PROJEKTU
# -------------------------

# Hlavný priečinok projektu (kde je main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /core
BASE_DIR = os.path.dirname(BASE_DIR)  # Root: /SpaceRider

# Cesty k folderom
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMG_DIR = os.path.join(ASSETS_DIR, "img")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")

# !!! OPRAVA FONT CESTY TU !!!
FONT_DIR = os.path.join(ASSETS_DIR, "Font")  # presne podľa tvojej štruktúry

DATA_DIR = os.path.join(BASE_DIR, "data")

# -------------------------
# FUNKCIE NA SÚBORY
# -------------------------

def get_path(*parts):
    """Generuje absolútnu cestu k súboru v rámci projektu."""
    return os.path.join(BASE_DIR, *parts)

def load_json(filename, default=None):
    """Bezpečné načítanie JSON súboru z /data."""
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
    """Uloží JSON do /data."""
    path = os.path.join(DATA_DIR, filename)

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Chyba pri zapisovaní '{filename}': {e}")

# -------------------------
# AUTO VYTVORENIE PRIEČINKOV
# -------------------------

for folder in [ASSETS_DIR, IMG_DIR, MUSIC_DIR, FONT_DIR, DATA_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)


# -------------------------
# DEBUG LOGOVANIE
# -------------------------

print("\n===== PATH CHECK =====")
print("BASE_DIR:", BASE_DIR)
print("FONT_DIR:", FONT_DIR, "→ exists:", os.path.exists(FONT_DIR))
print("IMG_DIR:", IMG_DIR, "→ exists:", os.path.exists(IMG_DIR))
print("======================\n")
