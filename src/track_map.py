import json
from logger import get_logger

log = get_logger()
def validate_corner_map(path: str) -> bool:
    log.info(f" -> Validate Corner Map, path: {path}")
    with open(path, "r", encoding="utf-8") as f:
        m = json.load(f)
    track_length = float(m["track_length_m"])
    ok = True
    prev_end = -1e9
    for c in m["corners"]:
        s, a, e = c["start_d"], c["apex_d"], c["end_d"]
        name = c["name"]
        if not (s <= a <= e):
            ok = False
            log.error(f"{name}: start<=apex<=end verletzt ({s} <= {a} <= {e})")

        if s < 0 or e > track_length:
            ok = False
            log.error(f"{name}: Distanz außerhalb [0,{track_length}]")

        if s < prev_end and s >= 0:
            log.error(f"{name}: {name}: Überlappt evtl. mit vorherigem (prev_end={prev_end}, start={s})")

    if ok:
        log.info("Corner map loaded")
    return ok
