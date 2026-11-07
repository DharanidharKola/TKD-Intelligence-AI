from pathlib import Path
import shutil

target = Path.cwd() / "backend" / "agents" / "video_agent.py"
if not target.exists():
    raise FileNotFoundError("Run from project root; backend/agents/video_agent.py was not found.")

src = target.read_text(encoding="utf-8")
if "IDENTITY_LOCK_V1" in src:
    raise SystemExit("Identity-lock patch already installed.")

backup = target.with_name("video_agent_before_identity_lock.py")
shutil.copy2(target, backup)

helpers = r'''
# IDENTITY_LOCK_V1: appearance-template association with conservative rejection.
IDENTITY_APPEARANCE_THRESHOLD = 0.30
IDENTITY_COLOR_CONFLICT_MARGIN = 0.045
IDENTITY_MAX_CENTER_DISTANCE = 0.24
IDENTITY_TEMPLATE_UPDATE_RATE = 0.08

def appearance_signature(frame, box):
    h, w = frame.shape[:2]
    x1, y1, x2, y2 = map(int, box)
    x1, x2 = max(0, x1), min(w, x2)
    y1, y2 = max(0, y1), min(h, y2)
    if x2 <= x1 or y2 <= y1:
        return None
    bw, bh = x2 - x1, y2 - y1
    crop = frame[y1 + int(.18*bh):y1 + int(.66*bh),
                 x1 + int(.16*bw):x1 + int(.84*bw)]
    if crop.size == 0:
        return None
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [24, 16], [0, 180, 0, 256])
    cv2.normalize(hist, hist, alpha=1.0, norm_type=cv2.NORM_L1)
    return hist

def appearance_similarity(a, b):
    if a is None or b is None:
        return -1.0
    return float(cv2.compareHist(a, b, cv2.HISTCMP_INTERSECT))

def select_identity_locked(candidates, state, frame_number):
    selected, used = {}, set()

    # Establish identity only from a clear initial red/blue protector detection.
    for color in ("red", "blue"):
        if color not in state:
            pool = [c for c in candidates if c["color"] == color]
            if pool:
                best = max(pool, key=lambda c: c["quality"])
                state[color] = {
                    "template": best.get("appearance"),
                    "center": best["center"],
                    "frame": frame_number,
                    "track_id": best["track_id"]
                }
                selected[color] = best
                used.add(id(best))

    for color in ("red", "blue"):
        if color in selected or color not in state:
            continue
        memory = state[color]
        age = frame_number - memory["frame"]
        pool = []
        for c in candidates:
            if id(c) in used:
                continue
            sim = appearance_similarity(memory["template"], c.get("appearance"))
            if sim < IDENTITY_APPEARANCE_THRESHOLD:
                continue
            opposite = "blue" if color == "red" else "red"
            if c.get("color") == opposite:
                own = float(c.get(color + "_ratio", 0.0))
                other = float(c.get(opposite + "_ratio", 0.0))
                if other - own > IDENTITY_COLOR_CONFLICT_MARGIN:
                    continue
            diag = max(1.0, np.hypot(c["frame_width"], c["frame_height"]))
            dist = np.hypot(c["center"][0]-memory["center"][0],
                            c["center"][1]-memory["center"][1]) / diag
            limit = min(0.42, IDENTITY_MAX_CENTER_DISTANCE + max(0, age-12)*.0018)
            if dist > limit and sim < .48:
                continue
            score = .72*sim + .28*max(0.0, 1.0-dist/max(limit, .001))
            pool.append((score, sim, c))
        pool.sort(key=lambda x: x[0], reverse=True)
        if not pool:
            continue
        if len(pool) > 1 and pool[0][0] - pool[1][0] < .055:
            continue
        _, sim, best = pool[0]
        selected[color] = best
        used.add(id(best))
        hist = best.get("appearance")
        if hist is not None and sim >= .55 and memory["template"] is not None:
            memory["template"] = cv2.addWeighted(
                memory["template"], 1.0-IDENTITY_TEMPLATE_UPDATE_RATE,
                hist, IDENTITY_TEMPLATE_UPDATE_RATE, 0
            )
        memory.update({"center": best["center"], "frame": frame_number,
                       "track_id": best["track_id"]})
    return selected
'''

anchor = "\n# =========================================================\n# DRAWING\n# ========================================================="
if anchor not in src:
    raise RuntimeError("DRAWING anchor not found; no patch applied.")
src = src.replace(anchor, "\n" + helpers + anchor, 1)

old = '                        "identity_recovery": None\n                    }'
new = '                        "identity_recovery": None,\n                        "appearance": appearance_signature(frame, box)\n                    }'
if old not in src:
    raise RuntimeError("Candidate dictionary anchor not found; no patch applied.")
src = src.replace(old, new, 1)

old = '''                    else:
                        # Keep a detection only if it can be conservatively
                        # associated with a recently identified competitor.
                        recovered_color, recovery_method = recover_competitor_identity(
                            candidate, identity_memory, frame_number
                        )
                        if recovered_color is None:
                            continue
                        candidate["color"] = recovered_color
                        candidate["identity_recovery"] = recovery_method
                        # A recovered candidate must not outrank strong direct
                        # color evidence solely because of an arbitrary ratio.
                        candidate["quality"] += 0.08

                    candidates.append(candidate)
'''
new = '''                    else:
                        # Unknown-color detections remain eligible only if their
                        # torso appearance matches an already locked competitor.
                        candidate["identity_recovery"] = "appearance_match"

                    candidates.append(candidate)
'''
if old not in src:
    raise RuntimeError("Unknown-color block not found; no patch applied.")
src = src.replace(old, new, 1)

old = '''            selected = select_one_per_color(
                candidates, previous_centers, frame_number
            )
'''
new = '''            selected = select_identity_locked(
                candidates, identity_state, frame_number
            )
'''
if old not in src:
    raise RuntimeError("Selection call not found; no patch applied.")
src = src.replace(old, new, 1)

old = '''    previous_centers = {}
    identity_memory = {}
    last_seen = {"red": None, "blue": None}
'''
new = '''    previous_centers = {}
    identity_memory = {}
    identity_state = {}
    last_seen = {"red": None, "blue": None}
'''
if old not in src:
    raise RuntimeError("Identity-state initialization not found; no patch applied.")
src = src.replace(old, new, 1)

compile(src, str(target), "exec")
target.write_text(src, encoding="utf-8")
print("Identity-lock patch installed.")
print("Updated:", target)
print("Backup:", backup)
print("Python syntax check: PASSED")
