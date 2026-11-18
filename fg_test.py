"""
FortyGuard heatmap test harness.

Usage:
    python fg_test.py <test_name>
    python fg_test.py --list          (shows available tests)

Before running, set your key in the SAME terminal window:
    PowerShell:  $env:FORTYGUARD_API_KEY="paste-your-key"
    CMD:         set FORTYGUARD_API_KEY=paste-your-key
    Mac/Linux:   export FORTYGUARD_API_KEY="paste-your-key"

Requires:  pip install requests

The key is never printed or saved. Every response is saved in ./results/.
"""

import json
import os
import sys
import time
from datetime import datetime

import requests

BASE_URL = "https://api.fortyguard.com"
SUBMIT_URL = BASE_URL + "/v1/heatmap"
STATUS_URL = BASE_URL + "/v1/status/{activity_id}"
POLL_EVERY_S = 5
MAX_WAIT_S = 600

# Lower Manhattan rectangle used in the official docs examples.
DOCS_RING = [[
    [-74.0170, 40.7051],
    [-74.0031, 40.7051],
    [-74.0031, 40.7180],
    [-74.0170, 40.7180],
    [-74.0170, 40.7051],
]]

BARE_POLYGON = {"type": "Polygon", "coordinates": DOCS_RING}

FEATURE_COLLECTION = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {},
        "geometry": {"type": "Polygon", "coordinates": DOCS_RING},
    }],
}

SINGLE_HOUR = {"start_date": "2024-07-15", "start_time": "14:00", "filter_type": 1}

TESTS = {
    # Test 1: the Create Heatmap page's "Single Hour" example, exactly as written (bare Polygon).
    "docs_single_hour": {
        "polygon_aoi": BARE_POLYGON,
        "date_time": SINGLE_HOUR,
        "granularity": 100,
    },
    # Test 2: identical, but polygon wrapped in a FeatureCollection (as Quickstart / Known Limitations say).
    "fc_single_hour": {
        "polygon_aoi": FEATURE_COLLECTION,
        "date_time": SINGLE_HOUR,
        "granularity": 100,
    },
    # Test 3: outside the US (small area in downtown Cairo). Docs: should be rejected with 400, not charged.
    "outside_us": {
        "polygon_aoi": {"type": "Polygon", "coordinates": [[
            [31.230, 30.040], [31.240, 30.040], [31.240, 30.050], [31.230, 30.050], [31.230, 30.040],
        ]]},
        "date_time": SINGLE_HOUR,
        "granularity": 100,
    },
    # Test 4: polygon not closed (last point differs from first). Docs: 400, not charged.
    "broken_polygon": {
        "polygon_aoi": {"type": "Polygon", "coordinates": [DOCS_RING[0][:4]]},
        "date_time": SINGLE_HOUR,
        "granularity": 100,
    },
    # Test 5: granularity 10 m (marketplace claims 10 m; docs allow only 20/60/80/100).
    "granularity_10": {
        "polygon_aoi": BARE_POLYGON,
        "date_time": SINGLE_HOUR,
        "granularity": 10,
    },
    # Test 6: date before the documented earliest date (2019-01-01; marketplace claims 2014).
    "date_2018": {
        "polygon_aoi": BARE_POLYGON,
        "date_time": {"start_date": "2018-07-15", "start_time": "14:00", "filter_type": 1},
        "granularity": 100,
    },
    # Tests 7-8: which earliest date is true? Docs say 2019-01-01, the API error said 2021-01-01.
    "date_2019": {
        "polygon_aoi": BARE_POLYGON,
        "date_time": {"start_date": "2019-07-15", "start_time": "14:00", "filter_type": 1},
        "granularity": 100,
    },
    "date_2020": {
        "polygon_aoi": BARE_POLYGON,
        "date_time": {"start_date": "2020-07-15", "start_time": "14:00", "filter_type": 1},
        "granularity": 100,
    },
    # Test 10: time_of_measure over 06:00-18:00 at 100 m. Peak hours around 14-17 = local time;
    # around 18-22 = UTC output (docs say non-20 m results "retain UTC").
    "time_of_measure": {
        "polygon_aoi": BARE_POLYGON,
        "date_time": {"start_date": "2024-07-15", "start_time": "06:00", "end_time": "18:00", "filter_type": 2},
        "granularity": 100,
        "analytic_type": "time_of_measure",
    },
    # Test 9: the finest documented granularity (20 m). Check it works and tiles really are ~20 m.
    "granularity_20": {
        "polygon_aoi": BARE_POLYGON,
        "date_time": SINGLE_HOUR,
        "granularity": 20,
    },
}


def save(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def as_json(resp):
    try:
        return resp.json()
    except ValueError:
        return {"_non_json_body": resp.text[:2000]}


def show_saved(path):
    """Inspect a saved *_final.json file. Makes no API call and costs no credits."""
    with open(path, encoding="utf-8") as f:
        final = json.load(f)
    result = ((final.get("data") or {}).get("result")) or {}
    tiles = (result.get("map_data") or {}).get("features") or []
    print(f"=== {path} ===")
    print(f"top-level keys      : {list(final.keys())}")
    print(f"data keys           : {list((final.get('data') or {}).keys())}")
    print(f"result keys         : {list(result.keys())}")
    print(f"map_data keys       : {list((result.get('map_data') or {}).keys())}")
    print(f"tiles               : {len(tiles)}")
    coverage = (result.get("map_data") or {}).get("coverage")
    if coverage is not None:
        print(f"coverage            : {json.dumps(coverage, indent=2)[:3000]}")

    if tiles:
        props = [t.get("properties") or {} for t in tiles]
        print(f"tile property names : {sorted(set(k for p in props for k in p))}")
        from collections import Counter
        for key in sorted(set(k for p in props for k in p) - {"tile_id"}):
            vals = [p[key] for p in props if isinstance(p.get(key), (int, float))]
            if vals and len(set(vals)) <= 30:
                counts = sorted(Counter(vals).items())
                print(f"'{key}' value counts : " + ", ".join(f"{v}: {n}" for v, n in counts))
        temps = [p.get("average_temperature") for p in props if isinstance(p.get("average_temperature"), (int, float))]
        if temps:
            import statistics
            print(f"average_temperature : min {min(temps):.4f}, max {max(temps):.4f}, "
                  f"mean {sum(temps) / len(temps):.4f} (computed by this script from the tiles)")
            if len(temps) >= 4:
                for method in ("inclusive", "exclusive"):
                    q1, q2, q3 = statistics.quantiles(temps, n=4, method=method)
                    print(f"quartiles ({method:9}): min {min(temps):.4f}, Q1 {q1:.4f}, median {q2:.4f}, "
                          f"Q3 {q3:.4f}, max {max(temps):.4f}")
        ring = ((tiles[0].get("geometry") or {}).get("coordinates") or [[]])[0]
        if len(ring) >= 3:
            import math
            lat = ring[0][1]
            w = abs(ring[1][0] - ring[0][0]) * 111_320 * math.cos(math.radians(lat))
            h = abs(ring[2][1] - ring[1][1]) * 110_574
            print(f"first tile size     : about {w:.0f} m x {h:.0f} m")

    stats = result.get("stats_data")
    if isinstance(stats, dict):
        print("\n--- stats_data ---")
        for key, value in stats.items():
            if isinstance(value, dict) and all(not isinstance(v, (list, dict)) for v in value.values()):
                print(f"{key}: {json.dumps(value)}")
            elif isinstance(value, list):
                print(f"{key}: list of {len(value)} items, first 5 = {value[:5]}")
            elif isinstance(value, dict):
                parts = []
                for k, v in value.items():
                    parts.append(f"{k}=list[{len(v)}] {v[:3]}..." if isinstance(v, list) else f"{k}={v}")
                print(f"{key}: " + "; ".join(parts))
            else:
                print(f"{key}: {value}")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--show":
        show_saved(sys.argv[2])
        return
    if len(sys.argv) != 2 or sys.argv[1] == "--list":
        print("Available tests:", ", ".join(TESTS))
        return
    name = sys.argv[1]
    if name not in TESTS:
        sys.exit(f"Unknown test '{name}'. Available: {', '.join(TESTS)}")

    api_key = os.environ.get("FORTYGUARD_API_KEY")
    if not api_key:
        sys.exit("FORTYGUARD_API_KEY is not set in this terminal window. See the top of this file.")

    headers = {"api-key": api_key, "Content-Type": "application/json"}
    os.makedirs("results", exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = os.path.join("results", f"{name}_{stamp}")
    body = TESTS[name]
    save(prefix + "_request.json", body)

    print(f"=== Test: {name}  ({datetime.now():%Y-%m-%d %H:%M:%S}) ===")
    t0 = time.time()

    # 1) Submit
    r = requests.post(SUBMIT_URL, headers=headers, json=body, timeout=60)
    submit = as_json(r)
    save(prefix + "_submit.json", {"http_status": r.status_code, "body": submit})
    print(f"[submit] HTTP {r.status_code} in {time.time() - t0:.1f}s")
    print(json.dumps(submit, indent=2)[:1500])

    activity_id = (submit.get("data") or {}).get("activity_id") if isinstance(submit, dict) else None
    if r.status_code != 200 or not activity_id:
        print("\nSubmit did not return an activity_id. Stopping here (this result is itself a finding).")
        return

    # 2) Poll
    counts = {"404": 0, "429": 0, "polls": 0}
    final, status = None, None
    while time.time() - t0 < MAX_WAIT_S:
        s = requests.get(STATUS_URL.format(activity_id=activity_id), headers=headers, timeout=60)
        counts["polls"] += 1
        if s.status_code == 404:
            counts["404"] += 1
            print(f"[poll {counts['polls']}] {time.time() - t0:5.0f}s  HTTP 404 (docs say this can happen right after submit) - retrying")
            time.sleep(POLL_EVERY_S)
            continue
        if s.status_code == 429:
            counts["429"] += 1
            print(f"[poll {counts['polls']}] {time.time() - t0:5.0f}s  HTTP 429 rate limit - waiting longer")
            time.sleep(POLL_EVERY_S * 3)
            continue
        final = as_json(s)
        if s.status_code != 200:
            print(f"[poll {counts['polls']}] HTTP {s.status_code}: {json.dumps(final)[:800]}")
            break
        status = (final.get("data") or {}).get("status")
        print(f"[poll {counts['polls']}] {time.time() - t0:5.0f}s  HTTP 200  status={status}")
        if status and status.lower() not in ("processing", "pending", "queued", "submitted"):
            break
        time.sleep(POLL_EVERY_S)
    else:
        print("Gave up after 10 minutes without a final status (note this).")

    if final is not None:
        save(prefix + "_final.json", final)

    # 3) Summary
    print("\n=== Summary ===")
    print(f"final status : {status}")
    print(f"total time   : {time.time() - t0:.0f}s")
    print(f"polls        : {counts['polls']}  (404s: {counts['404']}, 429s: {counts['429']})")
    result = ((final or {}).get("data") or {}).get("result") or {}
    tiles = (result.get("map_data") or {}).get("features") or []
    print(f"tiles        : {len(tiles)}")
    if tiles:
        print("first tile properties:", json.dumps(tiles[0].get("properties"), indent=2))
    stats = result.get("stats_data")
    if isinstance(stats, dict):
        print("stats_data keys:", list(stats.keys()))
        small = {k: v for k, v in stats.items() if not isinstance(v, (list, dict))}
        print("stats_data values:", json.dumps(small, indent=2))
    print(f"\nFull responses saved as {prefix}_*.json")


if __name__ == "__main__":
    main()
