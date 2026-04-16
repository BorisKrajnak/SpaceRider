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


# ------------------------- SCORE SAVE -------------------------
def save_score(game_name, score, cas=0):
    user = auth.current_user
    is_new_best = False

    local_file = _get_local_file(game_name)
    data = {"skore": score, "cas": cas}

    # LOCAL SAVE
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

        ref = db.child(path).get().val() or {}

        old_best = ref.get("best", 999999)

        # SCHOOL = lower is better
        if game_name == "school":
            if score < old_best:
                is_new_best = True
            new_best = min(old_best, score)

        # OTHER GAMES = higher is better
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
            "name": name,
            "average": score
        })

        return is_new_best

    except Exception as e:
        print("Firebase save_score failed:", e)
        return False


# ------------------------- BEST SCORE -------------------------
def load_best(game_name="raketka"):
    best = 0
    user = auth.current_user

    if user:
        try:
            uid = user["localId"]
            path = f"/users/{uid}/scores/{game_name}"
            data = db.child(path).get().val()

            if data and "best" in data:
                best = data["best"]
        except:
            pass

    try:
        with open(_get_local_file(game_name, best=True), "r", encoding="utf-8") as f:
            data = json.load(f)
            best = max(best, data.get("best", 0))
    except:
        pass

    return best


# ------------------------- LEADERBOARD FIXED -------------------------
def get_leaderboard(game_name="raketka", limit=10):
    try:
        users = db.child("users").get().val()
        if not users:
            return []

        leaderboard = []

        for uid, user_data in users.items():
            scores = user_data.get("scores", {})
            game_data = scores.get(game_name, {})

            value = game_data.get("best", None)
            if value is None:
                continue

            name = game_data.get("name")
            if not name:
                email = user_data.get("email", "")
                name = email.split("@")[0] if "@" in email else f"Player_{uid[:6]}"

            leaderboard.append({
                "name": name,
                "score": value
            })

        # 🔥 FIX: different sorting per game
        if game_name == "school":
            leaderboard.sort(key=lambda x: x["score"])  # lowest = best
        else:
            leaderboard.sort(key=lambda x: x["score"], reverse=True)

        return leaderboard[:limit]

    except Exception as e:
        print("Leaderboard load failed:", e)
        return []