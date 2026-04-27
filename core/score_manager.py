import os
import json
from core.firebase_init import auth, db
from core.config import get_path

LOCAL_DIR = get_path("data")


# ------------------------- UID -------------------------
def _get_uid():
    user = auth.current_user
    return user["localId"] if user else "guest"


# ------------------------- LOCAL FILE -------------------------
def _get_local_file(game_name, best=False):
    uid = _get_uid()
    filename = (
        f"best_score_{game_name}_{uid}.json"
        if best else
        f"skore_{game_name}_{uid}.json"
    )
    return os.path.join(LOCAL_DIR, filename)


# ------------------------- GAME RULE -------------------------
def is_min_game(game_name):
    return game_name == "school"


# ------------------------- SCORE SAVE -------------------------
def save_score(game_name, score, cas=0):
    user = auth.current_user
    is_new_best = False

    local_file = _get_local_file(game_name)
    data = {"skore": score, "cas": cas}

    try:
        with open(local_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("Local save error:", e)

    if not user:
        return False

    try:
        uid = user["localId"]
        path = f"/users/{uid}/scores/{game_name}"

        ref = db.child(path).get().val()
        if not ref:
            ref = {}

        old_best = ref.get("best")

        if old_best is None:
            old_best = float("inf") if is_min_game(game_name) else 0

        if is_min_game(game_name):
            if score < old_best:
                is_new_best = True
            new_best = min(old_best, score)
        else:
            if score > old_best:
                is_new_best = True
            new_best = max(old_best, score)

        email = user.get("email", "unknown")
        name = email.split("@")[0]

        db.child(path).update({
            "skore": score,
            "cas": cas,
            "best": new_best,
            "email": email,
            "name": name
        })

        return is_new_best

    except Exception as e:
        print("Firebase save_score failed:", e)
        return False


# ------------------------- BEST SCORE -------------------------
def load_best(game_name="raketka"):
    user = auth.current_user

    best = float("inf") if is_min_game(game_name) else 0

    if user:
        try:
            uid = user["localId"]
            path = f"/users/{uid}/scores/{game_name}"
            data = db.child(path).get().val()

            if data and "best" in data:
                best = data["best"]

        except Exception as e:
            print("load_best firebase error:", e)

    return best


# ------------------------- LEADERBOARD -------------------------
def get_leaderboard(game_name="raketka"):
    try:
        users = db.child("users").get().val()
        if not users:
            return []

        leaderboard = []

        for uid, user_data in users.items():
            scores = user_data.get("scores", {})
            game_data = scores.get(game_name, {})

            value = game_data.get("best")
            if value is None:
                continue

            email = user_data.get("email", "")
            name = game_data.get("name") or email.split("@")[0]

            leaderboard.append({
                "name": name,
                "score": value
            })

        if is_min_game(game_name):
            leaderboard.sort(key=lambda x: x["score"])
        else:
            leaderboard.sort(key=lambda x: x["score"], reverse=True)

        return leaderboard

    except Exception as e:
        print("Leaderboard load failed:", e)
        return []