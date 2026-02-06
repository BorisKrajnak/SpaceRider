import os
import json
from core.firebase_init import auth, db
from core.config import get_path

LOCAL_DIR = get_path("data")

# ------------------------- UID -------------------------
def _get_uid():
    user = auth.current_user
    return user["localId"] if user else "guest"

def _get_local_file(game_name, best=False):
    uid = _get_uid()
    filename = (
        f"best_score_{game_name}_{uid}.json"
        if best else
        f"skore_{game_name}_{uid}.json"
    )
    return os.path.join(LOCAL_DIR, filename)

# ------------------------- SCORE -------------------------
def load_score(game_name="raketka"):
    user = auth.current_user
    if user:
        try:
            uid = user['localId']
            path = f"/users/{uid}/scores/{game_name}"
            data = db.child(path).get().val()
            if data:
                return data.get("skore", 0), data.get("cas", 0)
        except Exception as e:
            print("Firebase load_score failed:", e)

    # Lokálny fallback (už viazaný na UID)
    try:
        with open(_get_local_file(game_name), "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("skore", 0), data.get("cas", 0)
    except:
        return 0, 0

def save_score(game_name, score, cas=0, best=False):
    # --- Lokálne uloženie ---
    local_file = _get_local_file(game_name, best=best)
    data = {"best": score} if best else {"skore": score, "cas": cas}
    try:
        with open(local_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("Error saving local score:", e)

    # --- Firebase uloženie ---
    user = auth.current_user
    if user:
        try:
            uid = user['localId']
            path = f"/users/{uid}/scores/{game_name}"
            if best:
                db.child(path).update({"best": score})
            else:
                db.child(path).update({"skore": score, "cas": cas})
        except Exception as e:
            print("Firebase save_score failed:", e)

# ------------------------- BEST SCORE -------------------------
def load_best(game_name="raketka"):
    best = 0
    user = auth.current_user

    # Firebase má prioritu
    if user:
        try:
            uid = user['localId']
            path = f"/users/{uid}/scores/{game_name}"
            data = db.child(path).get().val()
            if data and "best" in data:
                best = data["best"]
        except Exception as e:
            print("Firebase load_best failed:", e)

    # Lokálny fallback viazaný na UID
    try:
        with open(_get_local_file(game_name, best=True), "r", encoding="utf-8") as f:
            data = json.load(f)
            best = max(best, data.get("best", 0))
    except:
        pass

    return best
