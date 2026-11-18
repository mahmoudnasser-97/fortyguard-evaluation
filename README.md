# FortyGuard Product Evaluation

My evaluation of FortyGuard's **Temperature API®**, **Temperature Dashboard®**, **Temperature MCP** and **Selesious AI agent**, written as part of my application for the Data Engineering Internship (January 2027).

**Full report: [REPORT.md](REPORT.md)** (also attached to my application as a PDF).

— Mahmoud Nasser Elmoghany, November 2026

## Highlights

- **Cross-product consistency.** The same request (Lower Manhattan, 15 Jul 2024, 14:00, 100 m) gave identical statistics from the REST API, the dashboard and the MCP: mean 32.26 °C, std 0.41 °C.
- **Ground truth.** The API's 32.3 °C mean matched the Central Park station's 32–33 °C at 2 PM local time.
- **Time zones.** Request times are local, but `time_of_measure` returns UTC: a 06:00–18:00 request came back as `window_utc` 10:00–21:00.
- **Data range.** The docs say data starts in 2019 and the Marketplace says 2014, but the API rejects every date before **2021-01-01**.
- **Resolution.** 20 m and 100 m maps of the same area and hour don't overlap (means of 33.9 °C vs 32.3 °C).
- **Docs vs live MCP.** The server exposes 11 tools while the docs list 9, and a documented parameter doesn't exist.
- **Heat Intelligence audit.** The report contains verifiable errors in dates, distances and directions.

## What's in this repo

| File | Purpose |
|---|---|
| `REPORT.md` | The full evaluation: method, findings, evidence tables, recommendations, test log |
| `fg_test.py` | Test harness for the REST API: submits a heatmap, polls with 404/429 handling, saves every request and response, and inspects saved results offline |
| `lower_manhattan.geojson` | The test polygon (the docs' own example area), also uploaded to the dashboard |
| `evidence/` | The request bodies and submit/error responses from my test runs |
| [`screenshots/`](screenshots/README.md) | 42 annotated screenshots, one per finding, indexed by report section |

Full result files, which contain FortyGuard's tile data, are left out of the repo on purpose, because that data belongs to FortyGuard. I'm happy to share them on request.

## Running the tests

```
pip install requests

# PowerShell
$env:FORTYGUARD_API_KEY="your-key"
# Mac/Linux
export FORTYGUARD_API_KEY="your-key"

python fg_test.py --list                 # show available tests
python fg_test.py docs_single_hour       # run one test (paid tests cost 4,220 credits on Premium)
python fg_test.py --show results/<file>_final.json   # inspect a saved result, no API call
```

Tests that are rejected by validation (`outside_us`, `broken_polygon`, `granularity_10`, `date_2018` to `date_2020`) are never charged.

The API key is read from an environment variable and is never printed or saved.
