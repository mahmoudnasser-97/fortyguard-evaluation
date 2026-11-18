# FortyGuard Product Evaluation

**Mahmoud Nasser Elmoghany** · Applicant, Data Engineering Internship (January 2027)

Testing period: 11–18 November 2026 · Products: Temperature API®, Temperature Dashboard®, FortyGuard Temperature MCP, Selesious AI Agent

---

## Summary

I tested the three products as a new customer and as a data engineer would: I read the documentation page by page, called the REST API from my own Python script, recreated the same request in the dashboard and through the MCP in Claude Code, and checked results against each other and against an independent weather station. Every claim below is backed by a request I ran; the scripts and request files are in the accompanying repository.

**What impressed me most**

1. **The three products agree exactly.** The same area and hour (Lower Manhattan, 15 July 2024, 14:00, 100 m) returned identical statistics from the REST API, the dashboard and the MCP: min 31.89 °C, max 33.14 °C, mean 32.26 °C, std 0.41 °C.
2. **Billing is precise and predictable.** Every charge matched the documented price to the credit, invalid requests were never charged, and status/read calls were free.
3. **Validation is fast and readable.** Bad requests are rejected in about one second with messages that name the exact field.
4. **The MCP is designed with agent safety in mind.** Tools carry read-only / destructive annotations, paid tools instruct the AI to show parameters and cost and ask for confirmation, and responses include a `trace` block with plan, cost and latency.
5. **Known Limitations is an unusually honest page**, with a clear per-plan cost table.
6. **The model matched reality in my spot check.** The 14:00 heatmap mean (32.3 °C) was within 1 °C of the Central Park station at 2 PM.

**The most important problems**

1. **Time zones are inconsistent and undocumented.** Request times are interpreted as local time at the area, but `time_of_measure` returns hours in UTC. I proved both (Section 2.4).
2. **The documented data range is wrong.** The docs say the earliest date is 2019-01-01 and the Microsoft Marketplace listing says 2014, but the API rejects every date before 2021-01-01.
3. **20 m and 100 m heatmaps of the same area and hour do not overlap** (means of 33.9 °C vs 32.3 °C), with no explanation.
4. **The Heat Intelligence report contains verifiable factual and geographic errors** and relies mostly on general web sources rather than FortyGuard's own data.
5. **Docs and live behaviour have drifted apart**: the MCP exposes 11 tools while the docs list 9, a documented MCP parameter does not exist, several live parameters are undocumented, and response field names differ from the docs.
6. **The dashboard has no data export**, and the colour legend exaggerates a 2.3 °F range into a full red-to-blue map.
7. **Selesious said Lower Manhattan is "outside New York"**, the state my account covers.

A prioritised list of recommendations is in Section 8.

---

## How I tested

| Item | Detail |
|---|---|
| Plan | Trial key shown as "Premium Plan, One-Time", 1,000,000 credits, expiring 18 Nov 2026 |
| REST API | My own Python script (`fg_test.py`): submits, polls with 404/429 handling, saves every request and response as JSON |
| Dashboard | Chrome on Windows; recreated the API test by uploading the identical polygon as GeoJSON |
| MCP | Claude Code 2.1 on Windows PowerShell, manual permission mode so I could see every argument sent |
| Independent check | Weather Underground history for Central Park (KNYC), 15 July 2024 |
| Test area | Lower Manhattan rectangle from the docs' own example: lon −74.0170 to −74.0031, lat 40.7051 to 40.7180 (≈1.68 km²) |

**Credits used: 24,000 of 1,000,000 (2.4%).** I kept usage deliberate: most tests were designed to be rejected (free) or reused data already returned.

| Step | Credits | Balance |
|---|---|---|
| Start | — | 1,000,000 |
| REST: 4 successful heatmaps (4 × 4,220) | 16,880 | 983,120 |
| REST: 6 deliberately invalid requests | 0 | 983,120 |
| Dashboard: heatmap, analytics, Street View segmentation, Heat Intelligence report | 0 | 983,120 |
| MCP: `env_params` (docs' own test prompt) | 2,900 | 980,220 |
| MCP: heatmap (same request as REST) | 4,220 | 976,000 |

---

## 1. Cross-product consistency

Same polygon, 15 July 2024, 14:00 local, 100 m, default analytic type:

| | REST API | Dashboard | MCP (Claude Code) |
|---|---|---|---|
| Minimum | 31.887 °C | 89.40 °F (= 31.89 °C) | 31.89 °C |
| Maximum | 33.1424 °C | 91.66 °F (= 33.14 °C) | 33.14 °C |
| Mean | 32.255 °C | 90.06 °F (= 32.26 °C) | 32.26 °C |
| Std. deviation | 0.415 °C | 0.75 °F (= 0.415 °C) | 0.41 °C |
| Tiles | 150 | ≈150 (12 × 13 grid, corner over water omitted) | not returned |
| Credits | 4,220 | 0 | 4,220 |

The engine is clearly shared and deterministic: the same REST request sent twice (once as a bare Polygon, once as a FeatureCollection) returned identical tiles and statistics, and the saved results were the same size to the byte. This is a real strength and worth stating in the docs.

---

## 2. Temperature API

### 2.1 Reliability and billing

| Test | Result |
|---|---|
| Docs' Single Hour example (bare `Polygon`) | Completed in 22 s, 150 tiles, 4,220 credits |
| Same request with `FeatureCollection` | Completed in 28 s, identical result, 4,220 credits |
| 20 m granularity | Completed in 16 s, 4,207 tiles, 4,220 credits |
| `time_of_measure`, 06:00–18:00 | Completed in 22 s, 150 tiles, 4,220 credits |
| Polling | No 404s or 429s in any run; submit responses in 1–4 s |

- Every charge matched the documented Premium price exactly; failed validation never charged.
- **Duplicate requests are charged twice.** Results are deterministic, so a retry after a network error costs the customer twice. The MCP's live `heatmap` tool already accepts an idempotency key; the REST API should document and support the same.
- Pricing is per request regardless of resolution: a 20 m map (4,207 tiles) cost the same as 100 m (150 tiles). That's good for customers but isn't stated anywhere.

### 2.2 Validation and error handling

| Request | HTTP | `code` | Message quality | Charged |
|---|---|---|---|---|
| Polygon in Cairo | 400 | `OUT_OF_COVERAGE` | Clear, explains U.S.-only coverage | No |
| Polygon ring not closed | 400 | *(none)* | Clear, names `polygon_aoi.coordinates[0]` | No |
| `granularity: 10` | **422** | *(none)* | Clear, plus a `detail` array | No |
| Date 2018 / 2019 / 2020 | 400 | `NO_COVERAGE` | Clear, gives earliest date | No |

All rejections came back in about one second, before any background job started. That's excellent. The problem is **shape consistency**: two status codes for validation (Known Limitations promises 400; only the Quickstart mentions 422), a machine-readable `code` on some errors but not others, and a `detail` array on one. A pipeline needs one predictable error schema with a `code` on every error and a documented list of codes.

### 2.3 Supported date range: three sources, three answers

| Source | Earliest date claimed |
|---|---|
| Microsoft Marketplace listing | 2014 |
| Known Limitations and Create Heatmap docs | 2019-01-01 |
| **The API itself (tested)** | **2021-01-01** (rejected 2018-07-15, 2019-07-15 and 2020-07-15) |

A customer planning a historical study would lose two years they were promised. The same pattern applies to resolution: the Marketplace claims 10 m to 10 km, the API rejects 10 m (`Input should be 20, 60, 80 or 100`).

**Suggestion:** a free `GET /v1/coverage` endpoint returning supported dates, regions and granularities per plan, used as the single source of truth for docs, dashboard and marketing.

### 2.4 Time zones (proved with two tests)

**Input is local time.** My 14:00 request for Lower Manhattan returned a mean of 32.3 °C. Central Park (KNYC) recorded 32 °C at 1:51 PM and 33 °C at 2:51 PM EDT, but only 27–28 °C at 9:51–10:51 AM (14:00 UTC). The 20 m map (mean 33.9 °C) also matches the afternoon, so both resolutions read `start_time` as local.

**Output is UTC.** A `time_of_measure` request for 06:00–18:00 returned `window_utc` 10:00–21:00 (end inclusive) and every tile valued `19`, which is 15:00 EDT. That's a plausible peak, since the station's highest reading in that window was 33 °C at 2:51 PM.

So one request mixes two time zones. The stats are labelled `_utc`, but the tile `value` isn't, and nothing in the docs says whether input is local or UTC or whether `end_time` is exclusive (it is: "18:00" ended at 17:00 local). The Create Heatmap page describes time three different ways: "20 m uses the AOI timezone, existing resolutions retain UTC", a code comment saying "0–23, UTC", and nothing on `start_time` itself.

Interestingly, the MCP `env_params` response already does this right: `"timezone": "America/Phoenix"` with ISO 8601 timestamps carrying offsets. **Suggestion:** apply that pattern everywhere — accept and return ISO 8601 with explicit offsets, or add a `timezone` parameter.

### 2.5 Resolution: 20 m and 100 m disagree

| Same area, same hour | 100 m | 20 m |
|---|---|---|
| Tiles | 150 | 4,207 |
| Tile size (measured from geometry) | ≈100 m × 98 m | ≈20 m × 20 m |
| Mean | 32.26 °C | 33.89 °C |
| Range | 31.89 – 33.14 °C | 33.20 – 34.95 °C |
| Standard deviation | 0.41 | 0.23 |

If 20 m were a sharper view of the same field, the means would be close and the 20 m range would be wider and contain the 100 m range. Instead the ranges **don't overlap at all** and the finer grid varies less. The docs mention that 20 m uses "a separate catalog", but not that absolute values shift by 1.6 °C. A customer switching resolution would see an unexplained jump. Which resolution is better validated?

On the dashboard, the 100 m map shows near-perfect north–south stripes that run straight across buildings, Battery Park and the waterfront, with the hottest column along the East River. I'd expect water to cool nearby tiles. That suggests the 100 m layer may be interpolated from coarser data. I'm raising it as a question, not a conclusion.

### 2.6 Response structure and data quality

- **`overall_temperature_distribution` is a five-number summary, not "sorted values".** It returned 5 numbers. I computed quartiles from the 150 tiles, and the inclusive-method values match exactly: 31.887, 31.9136, 32.0811, 32.6254, 33.1424. Labelled keys (`min`, `q1`, `median`, `q3`, `max`) would make this self-explanatory. The dashboard uses it for a box plot, but the API docs don't say so.
- **Statistics are internally consistent.** API min/max/mean match my own calculation from the tiles, histogram counts sum to the tile count (111 + 39 = 150), and the fitted curve spans mean ± 3σ.
- **Field names differ from the docs.** The docs say `Temperature_stats`, `Overall_temperature_distribution` and `Minimum`; the API returns lowercase `temperature_stats` and `minimum`. JSON keys are case-sensitive, so code written from the docs breaks. Tile properties (`tile_id`, `average_temperature`, `min_temperature`, `max_temperature`) are undocumented, and the Result Schema example shows empty `{}` objects.
- **Three naming styles for the same concepts:** tiles use `min_temperature`, stats use `minimum`, docs use `Minimum`.
- **The histogram is unsorted and too coarse.** At 20 m, `temperature_frequency` returned bins in the order [34, 33, 35], with 4,057 of 4,207 tiles (96%) in one 1 °C bin. Bin edges and widths aren't documented.
- **Coverage metadata is excellent but inconsistent.** 20 m responses include `coverage` (expected vs present hours, sample fraction, `complete: true`), which lets a pipeline check completeness automatically. But it's missing at 100 m. It reports 5,693 source cells versus 4,207 output tiles without explaining the relationship, and `statistics_basis: "available samples; existing temporal aggregation applies"` is jargon.
- **`stats_data` changes shape by analytic type.** `time_of_measure` returns `window_utc`, `hour_counts_utc`, `tie_rule` and so on, none of which are in Result Output Fields.
- **Precision is inconsistent.** Tiles have 4 decimals; stats are raw floats like 32.255170666666665.

### 2.7 Scale: response size

| Resolution | Tiles | Saved JSON | Per tile |
|---|---|---|---|
| 100 m | 150 | 168 KB | ≈1.1 KB |
| 20 m | 4,207 | 4.5 MB | ≈1.1 KB |

My test area is only 1.68 km². A Premium maximum of 50 mi² (≈130 km²) at 20 m would be roughly 320,000 tiles, or on the order of 300 MB of JSON in one response (estimated from my indented files, so the real figure is somewhat lower). Each tile repeats a full 5-point polygon and, for a single hour, three identical temperature values.

**Suggestions:**
- a compact format (centroid + value, or GeoParquet/Cloud-Optimised GeoTIFF)
- gzip
- pagination or a signed download URL for large results

---

## 3. Documentation

**Strengths:**
- clean structure
- copy buttons and tabbed examples for every filter and analytic type
- credit cost and plan limits shown on each endpoint page
- an honest Known Limitations page
- release notes
- live plan and credit balance on the Check API Credits Usage page

**Issues, in rough priority order:**

1. **Out-of-date facts:** earliest date (2.3), MCP tool count (6.2), `wait_for_completion` (6.2), field-name casing (2.6).
2. **Contradictions between pages:**
   - Known Limitations says `polygon_aoi` *must* be a FeatureCollection, while every Create Heatmap example sends a bare Polygon. I tested both, and both work.
   - "≤ 1 month" vs "at most 31 days".
   - 400 vs 400/422.
3. **Time zones are never stated** (2.4).
4. **Quickstart code doesn't follow its own status table.** The table lists Processing/Completed/Failed and warns about 404 right after submission and 429. The polling code checks for "succeeded"/"error", which don't exist, and calls `response.json()["data"]["status"]` without checking the HTTP status, so a 404 or 429 would crash it instead of retrying.
5. **Key handling:**
   - REST examples hardcode `"YOUR_API_KEY"` in source, with no environment-variable example and no rotation or revocation guidance. The MCP Authentication page has good guidance, so it could be reused.
6. **Unexplained terms:**
   - `tcm` — I only learned it means "Temperature Classification Map" from the dashboard metadata.
   - `map_type` `bm` / `tcm` / `tccm`.
   - "Map Statistics".
   - "reference temperature".
   - plan names: "Enterprise API" vs "Temperature API®"; a "Startup" plan that appears only in Known Limitations; a "hackathon" tier that the MCP mentions but no docs list.
7. **Plan Availability:**
   - the BASIC tag reads as "Basic only"
   - it doesn't link to the Known Limitations cost table, so a new user can't estimate credit usage
   - Premium costs *more* per request than Basic (4,220 vs 3,500 for a heatmap), which is unusual and unexplained
8. **Platform coverage:** every MCP setup command is Mac/Linux only (6.1).

---

## 4. Temperature Dashboard

### 4.1 Onboarding

- **Positives:**
  - a preloaded demo heatmap, so the first screen already shows a result
  - an 11-step tour with a progress bar, Back/Next and close
  - a helpful empty state
  - the API-key email arrived within seconds and went to the inbox
- **The sign-up form asks for "Access US State" without explaining it.** I learned it limits what you can view only when Selesious refused Manhattan (Section 5).
- **Two overlapping pop-ups:**
  - the details form and the "Meet Selesious" card appear together
  - the Selesious card stays on screen through the whole tour, and in step 9 the Legend tooltip covers it
- **Tour steps describe benefits rather than how to use each feature** (e.g. Map Controls).
- **The demo heatmap doesn't show its date, hour or resolution** until you open Metadata, and the colours mean nothing until you open the Legend. City Name shows "N/A" on a map named "Demo Heatmap – New York".

### 4.2 Creating a heatmap

- **Positives:**
  - Polygon, Circle and GeoJSON Upload
  - my uploaded file was accepted as-is and the map zoomed to it
  - a live area/perimeter estimate (0.65 mi² / 3.24 mi, which is exactly correct for my rectangle)
  - "Email me when ready"
  - a disabled Generate button until the form is valid
  - generation took about 20 s
- **After generating, the form reset and the map jumped to a state-wide view** instead of showing the new heatmap. The demo heatmap stayed drawn on the map, so I first clicked a demo tile (51.4 °F in Queens) thinking it was my result.
- **The time picker shows "2:00PM" with no time zone.**
- **Only 100/80/60 m are offered.** 20 m, which the API supports, isn't available in the dashboard.
- **Dashboard usage didn't consume credits** (balance unchanged across a heatmap, analytics, segmentation and a report). Good for users, but it isn't stated anywhere, and the API charges 4,220–8,600 for the same work.

### 4.3 Visualisation and statistics

- **Positives:**
  - statistics match the API exactly
  - Metadata is thorough (ID with copy button, start/end times, granularity)
  - charts map to the API fields: Bar Graph = `temperature_frequency`, Normal Curve = `normal_temperature_distribution`, Box Plot = the five-number summary
  - clicking a tile shows temperature and coordinates
- **The legend exaggerates differences.** 12 colour classes span only 2.26 °F (89.40–91.66 °F), with uneven widths (one class is 0.01 °F wide) and two classes labelled identically "89.4 °F – 89.4 °F". A near-uniform area looks dramatic, and maps from different days can't be compared visually. The Time of Measure view already uses a continuous bar. An absolute or fixed-step scale option would make maps honest and comparable.
- **Units:**
  - the map is in °F while the API returns °C
  - a °F/°C switch exists in Analytics but not on the main map
  - the statistics cards are cut off horizontally ("…ature Range") and need sideways scrolling
- **The Accuracy panel describes a 7-tier index in words only.** There's no error figure (± °C) per tier, it's unclear which tier a map has, and the API response carries no tier.

### 4.4 Analytics, segmentation and capture

- **Analytics menu:** clear, with each item tagged Map or Chart. Time of Measure percentiles match the API exactly, and it states "air temperature", the only place that says what is measured. It ran on a single-hour map without warning that every tile will trivially show 14:00.
- **"Capture View" and "Capture Tile" aren't exports.** They select imagery or a tile for segmentation and Heat Intelligence. I couldn't find any way to download heatmap data (CSV/GeoJSON) from the dashboard.
- **Capture buttons were laggy.** Steps: click a tile → Actions tab → Capture View / Capture Tile. Expected: the button responds. Actual: it often didn't respond until I switched to the Information tab and back to Actions.
- **Street View segmentation:**
  - fast (≈10 s), dated ("captured on 2026-04-01")
  - percentages sum to 100.00% in both views
  - an honest "pre-trained model" disclaimer
- **Street View issues:**
  - The image is from April 2026, while the heatmap is July 2024, with no warning about the mismatch. Bare April branches likely understate July tree cover (Tree 19.02%).
  - Road is tinted grey, the same as asphalt, so it looks unsegmented.
  - Car and Tree are both green.
  - The "Meaning" column repeats "Proportion of the image area covered by X" for every row and never links a class to heat (shade cools, asphalt stores heat) or defines Tree vs Plant.
- **"Sky View On/Off" actually means "include sky in the percentages".** Off rescales everything else: Sidewalk 27.30% → 30.75% = 27.30 / (100 − 11.21). The label suggests the sky view factor, a real urban-heat metric.

### 4.5 Heat Intelligence report: audit

I generated a report for one tile (40.7175, −74.0039; 91.66 °F) and read the full 35-page PDF.

**Strengths:**
- impressive breadth (5 sections, a table of contents, climate normals, AQI, shade at 2 PM, street canyons)
- correct use of local time ("14:00 EDT")
- free in the dashboard

**Issues I verified:**

| Report says | Reality |
|---|---|
| 106 °F record of 9 July 1936 "measured at LaGuardia" | LaGuardia Airport opened in 1939; the record is Central Park's |
| AQI 200 is the "Very Unhealthy threshold" | On the US EPA scale 200 is the top of *Unhealthy*; *Very Unhealthy* starts at 201 |
| The Battery is ~0.3 mi from the point | ≈1.2 mi (computed from the coordinates) |
| City Hall Park is ~0.2 mi **north** | ≈0.35 mi **south** |
| Location is the "Financial District" | The point is in Tribeca / Civic Center |
| 91.7 °F is "the provided average" | It's a single-hour value at 14:00 |

- **Sources are generic:** only four distinct links across 35 pages — Open-Meteo (13×), the general Wikipedia "New York City" article (8×), the nyc.gov homepage (6×) and a U.S. News travel guide (2×).
- **It barely uses FortyGuard's own data.** The word "FortyGuard" doesn't appear in the report. Apart from the input temperature, it doesn't use the heatmap gradient, the segmentation I ran on that exact street, or the coverage data.
- **Coordinates differ slightly** between the selected tile (40.717451, −74.003991) and the report (40.717539, −74.003871), about 12 m.
- **Workflow:** the job looked stuck on "pending" for about 10 minutes and only completed when I clicked it in the Task Queue, so the status doesn't seem to refresh by itself.
- **The panel's description mentions "sensors" and "efficiency in heating systems"**, which doesn't match an urban-heat cooling product.

**Suggestions:**
- ground the report in FortyGuard's outputs
- compute distances from real geodata
- cite specific sources
- clearly label AI-generated text

For decision-makers, one verifiable error undermines trust in the whole document.

---

## 5. Selesious AI Agent

I asked: *"What was the temperature in Lower Manhattan (Financial District) on July 15, 2024 at 2 PM local time?"* I already knew the answer from the API: 32.3 °C / 90.1 °F.

- **Good:** it asked a sensible clarifying question with three clear options (draw on the map, name a street, or start from the centre).
- **It then said "Lower Manhattan (Financial District) is outside New York, the region your account covers".** Lower Manhattan is in New York State and New York City. The same request works in the dashboard and the API under the same account. This looks like a broken geographic check, and it blocks the most obvious first question a New York user would ask.
- **It said "One heat map covers up to 150 mi²".** The docs say 10 mi² (Basic) or 50 mi² (Premium).
- **The pop-up appears on every screen,** including during the tour.

---

## 6. FortyGuard Temperature MCP

### 6.1 Setup (Claude Code on Windows)

- **Positives:**
  - remote MCP, so there's nothing to install
  - one command, connected and authenticated on the first try
  - current protocol version (2026-07-28)
  - well-structured pages: Overview → Quickstart → per-client setup → Available Tools → Troubleshooting
  - the docs' own test prompt worked first time
- **Every command is Mac/Linux only.** In PowerShell, `export FORTYGUARD_API_KEY=…` fails with *"The term 'export' is not recognized"*, and the `\` line continuations break the `claude mcp add` command. A PowerShell tab would fix it. The working command was:
  `claude mcp add --transport http fortyguard https://tos-mcp.app.fortyguard.com/mcp --header "Authorization: Bearer $env:FORTYGUARD_API_KEY"`
- **The documented command stores the key in plain text.** The shell expands `$FORTYGUARD_API_KEY` when the command runs, so the literal key is saved in the client's config file (`~/.claude.json`). That contradicts the "store keys securely" advice on the same page. Documenting variable expansion inside the client config, or an OAuth flow, would avoid this.
- **The Authorization header is a static Bearer key.** It may not be usable from chat apps whose custom connectors expect OAuth, which matters for non-developer users.

### 6.2 Docs vs the live server

| Docs say | Live server |
|---|---|
| "The current catalog contains nine tools" | 11 tools: `credit_balance` and `monitoring` are undocumented |
| `heatmap` accepts `wait_for_completion` | Not in the live schema; the client had to submit, sleep 20 s and poll |
| — | Live `heatmap` also accepts `notify_by_email`, `threshold`, `direction` and an **idempotency key** (undocumented, and the idempotency key is exactly what the REST API needs) |
| — | The server advertises a `resources` capability that no page mentions |

### 6.3 Tool design

- **Excellent:**
  - Tools are annotated read-only, destructive or open-world.
  - `credit_balance` says "free and read-only".
  - `monitoring` lists which operations are free and what the rest cost, and instructs the agent to show the parameters and cost and ask for confirmation before any paid operation. In practice Claude did exactly that: it showed a parameter table and "Cost: 2,900 credits… Should I go ahead?"
  - Every response includes a `trace` (`plan_type`, `cost_credits`, `latency_ms`, `trace_id`), `evidence` (source endpoint, `catalog_version`) and `warnings`. That's very good for auditability.
- **The ID parameter has three names:** `heatmap_id`, `analytics_id` ("also accepts activity_id") and `activity_id`. The example ID `hm_123` doesn't resemble real UUIDs.
- **`monitoring`:**
  - Every parameter except `operation` has type "unknown", so agents must guess the format of `rules` or `boundary_geojson`.
  - Its 3,500-credit price isn't in the Known Limitations table, and it equals the *Basic* heatmap price while Premium heatmaps cost 4,220.
  - It sends real email, SMS or WhatsApp notifications.
- **Unclear inputs:**
  - `streetview.back_view` is described as a "Required flag to include an optional back-view result".
  - `vertical_angle` has no range.
  - The satellite input is named `sat`.
  - Costs are described only as "may consume usage or credits".
- **Resolution sets differ by product:** REST 20/60/80/100, MCP 60/80/100, dashboard 60/80/100.

### 6.4 What I ran

1. **`credit_balance`**
   - Free; returned 983,120, matching the dashboard.
   - It returns only a number, with no plan, expiry or reset date.
   - Because the description says "Enterprise API credits", Claude concluded I was on an Enterprise plan. I'm on a Premium trial.
2. **`env_params`** with the docs' test prompt (Phoenix, 2025-09-20, reference 35 °C)
   - 2,900 credits exactly, 4.07 s latency, 24 hourly values for each measure.
   - **The "reference temperature" design produces misleading heat-index values.** The heat index uses the user's fixed 35 °C for every hour, combined with that hour's humidity, so it peaked at 44.7 °C at 06:00, the coolest and most humid hour, when the apparent temperature was about 29 °C. FortyGuard has its own hourly temperature model; using it would make the heat index meaningful.
   - The top-level values for a whole-day request are the midnight snapshot (`"basis": "first_hour_snapshot"`). That's labelled, but a daily min/max/mean would be a more useful default.
3. **`heatmap`, then `heatmap_read`** (the same request as REST)
   - Identical statistics (Section 1), 4,220 credits, free reads.
   - Claude correctly read 14:00 as New York time.
   - **The result is statistics only: no tiles, no GeoJSON, no tile count, no download link.** Claude had to guess "roughly 180 cells"; the real count is 150. An agent can describe a heatmap but can't hand the actual map to another tool. Returning the tile count and a GeoJSON or download link would fix this.

---

## 7. Scalability and maintainability

1. **One source of truth for limits.** Supported dates, granularities, area limits, tool count and prices differ between the API, docs, dashboard, MCP, Selesious and the Marketplace. Generating docs and agent tool descriptions from a single machine-readable spec (an OpenAPI file plus a `/v1/coverage` endpoint) would stop the drift.
2. **A published OpenAPI spec** with real response schemas, including the per-analytic-type `stats_data` shapes, would let customers generate clients and catch the casing problems automatically.
3. **One error schema** with a stable `code` on every error.
4. **Idempotency keys on every paid endpoint**, in both REST and MCP.
5. **Compact, paginated or downloadable results** before customers request 50 mi² at 20 m.
6. **Explicit time zones** in every request and response.
7. **Contract tests** that run the docs' own examples and the MCP schema against production on each release. These would have caught `wait_for_completion`, the tool count and the field casing.
8. **Response versioning:** `catalog_version: v3` and `calculation_version: 2` already exist, which is a good base. Documenting them would let customers track model changes over time.

---

## 8. Prioritised recommendations

| # | Priority | Area | Recommendation |
|---|---|---|---|
| 1 | High | API / docs | State and standardise time zones: ISO 8601 with offsets in and out (already done in `env_params`) |
| 2 | High | Data | Explain or reconcile the 20 m vs 100 m difference; document which is validated and expected error per resolution |
| 3 | High | Docs / marketing | Fix the earliest date (2021 vs 2019 vs 2014) and resolution claims; add `/v1/coverage` |
| 4 | High | Heat Intelligence | Ground reports in FortyGuard data and real geodata; specific citations; label AI text |
| 5 | High | Selesious | Fix the region check that rejects Lower Manhattan for a New York account |
| 6 | Medium | Dashboard | Data export (CSV / GeoJSON); show the new heatmap after generation; absolute legend option |
| 7 | Medium | API | One error schema with codes; idempotency keys; compact or paginated large results |
| 8 | Medium | MCP | Sync docs with the live server (11 tools, parameters); typed schemas for `monitoring`; tile count and download link in `heatmap_read`; consistent ID names |
| 9 | Medium | Docs | Fix the Quickstart polling code; Windows/PowerShell examples; environment-variable key handling; explain `tcm`/`bm`/`tccm` and plan names |
| 10 | Low | Env params | Use FortyGuard's modelled hourly temperature instead of a user-supplied reference; return daily summaries |

---

## Appendix A: test log

| # | Product | Test | Outcome | Credits |
|---|---|---|---|---|
| 1 | REST | Docs' Single Hour example (bare Polygon) | Completed, 150 tiles, 22 s | 4,220 |
| 2 | REST | Same as FeatureCollection | Completed, identical, 28 s | 4,220 |
| 3 | REST | Outside US (Cairo) | 400 `OUT_OF_COVERAGE` | 0 |
| 4 | REST | Unclosed polygon | 400, no code | 0 |
| 5 | REST | Granularity 10 m | 422, no code | 0 |
| 6–8 | REST | Dates 2018 / 2019 / 2020 | 400 `NO_COVERAGE`, "earliest supported date (2021-01-01)" | 0 |
| 9 | REST | Granularity 20 m | Completed, 4,207 tiles, 16 s | 4,220 |
| 10 | REST | `time_of_measure` 06:00–18:00 | Completed; `window_utc` 10:00–21:00; all tiles = 19 | 4,220 |
| 11 | Check | Weather Underground KNYC 15 Jul 2024 | 32–33 °C at 2 PM, 27–28 °C at 10 AM | — |
| 12 | Dashboard | Same polygon uploaded, 2 PM, 100 m | Identical statistics | 0 |
| 13 | Dashboard | Time of Measure, Street View segmentation, Heat Intelligence | See Section 4 | 0 |
| 14 | Selesious | Temperature in Lower Manhattan, 15 Jul 2024, 2 PM | "Outside New York" | 0 |
| 15 | MCP | `credit_balance` (×3) | 983,120 / 980,220 / 976,000 | 0 |
| 16 | MCP | `env_params`, docs' test prompt | Completed, 4.07 s | 2,900 |
| 17 | MCP | `heatmap` + `heatmap_read`, same as #1 | Identical statistics, stats only | 4,220 |

## Appendix B: what I didn't test, and caveats

- I didn't test routing, satellite segmentation through the API or MCP, or monitoring. Monitoring sends real notifications and costs credits.
- The accuracy comparison is one location, one hour, against a park station about 6 km away. It's encouraging, not a validation.
- My response-size projection is an estimate from indented JSON files.
- Findings reflect the products as of 11–18 November 2026.

The scripts, polygon and request/response evidence are in the accompanying GitHub repository. Screenshots for each finding are indexed by section in [`screenshots/README.md`](screenshots/README.md).
