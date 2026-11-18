# Screenshots

Evidence for the findings in [REPORT.md](../REPORT.md), grouped by report section. All taken between 11 and 18 November 2026.

## Setup and ground truth

| Screenshot | What it shows | Report |
|---|---|---|
| [01](01-setup-trial-plan-card.png) | Trial plan card: "Premium Plan, One-Time", 1,000,000 credits, expires 18 Nov. The docs say Premium is 5,000,000 monthly and only Startup is one-time | Docs §3 |
| [02](02-api-ground-truth-knyc-2024-07-15.png) | Central Park (KNYC), 15 Jul 2024: 32–33 °C around 2 PM and 27–28 °C around 10 AM. Used to prove `start_time` is local time | API §2.4 |

## Documentation

| Screenshot | What it shows | Report |
|---|---|---|
| [03](03-docs-known-limitations-input-constraints.png) | Known Limitations: earliest date 2019-01-01 (the API says 2021-01-01) and "must be a FeatureCollection" (a bare Polygon also works) | §2.3, §3 |
| [04](04-docs-create-heatmap-earliest-date-2019.png) | Create Heatmap: earliest date 2019-01-01 | §2.3 |
| [05](05-docs-result-output-fields-capitalised.png) | Result Output Fields: capitalised names and "sorted temperature values" (actually a five-number summary) | §2.6 |
| [06](06-docs-quickstart-polling-code.png) | Quickstart polling code checks "succeeded"/"error" and doesn't handle 404/429 | §3 |
| [07](07-docs-quickstart-status-table.png) | The status table it should follow (400/422, 404 after submit, 429) | §2.2, §3 |
| [08](08-docs-known-limitations-credit-costs.png) | Credit costs per plan (Premium costs more per request than Basic) | §2.1, §3 |

## Dashboard

| Screenshot | What it shows | Report |
|---|---|---|
| [10](10-dashboard-onboarding-state-and-popups.jpg) | Sign-up asks for "Access US State" without explanation; the Selesious pop-up appears at the same time | §4.1 |
| [11](11-dashboard-tour-overlapping-popups.jpg) | Tour step 9: the Legend tooltip overlaps the Selesious card | §4.1 |
| [12](12-dashboard-demo-metadata-city-na.png) | Demo metadata: City Name "N/A"; type "Temperature Classification Map" (= `tcm`) | §4.1, §3 |
| [13](13-dashboard-accuracy-index-no-numbers.png) | Accuracy index: 7 tiers in words, no error figures | §4.3 |
| [14](14-dashboard-create-heatmap-uploaded-polygon.jpg) | My uploaded GeoJSON: 0.65 mi² / 3.24 mi; "2:00PM" with no time zone; only 100/80/60 m offered | §4.2 |
| [15](15-dashboard-after-generate-state-view.jpg) | After Generate Map: form reset, map zoomed out to New York State, new heatmap not shown | §4.2 |
| [16](16-dashboard-new-heatmap-stripes.jpg) | The new 100 m heatmap: north–south stripes ignoring the ground | §2.5 |
| [17](17-dashboard-stats-and-legend-2.3F-range.jpg) | Mean 90.06 °F matches the API; 12 legend classes over 2.26 °F, two labelled "89.4 – 89.4" | §1, §4.3 |
| [18](18-dashboard-analytics-menu-and-capture.jpg) | Analytics menu (Map/Chart tags) and the Capture View / Capture Tile actions | §4.4 |
| [19](19-dashboard-streetview-front-april-2026.png) | Street View segmentation: image captured 2026-04-01 for a July 2024 heatmap; road left grey | §4.4 |
| [20](20-dashboard-streetview-front-segments.png) | Front-view segments: sums to 100%; generic "Meaning" column | §4.4 |
| [21](21-dashboard-streetview-back-sky-on.png) | Back view, Sky View on: Sidewalk 27.30%, Sky 11.21% | §4.4 |
| [22](22-dashboard-streetview-back-sky-off.png) | Sky View off: Sidewalk 30.75% = 27.30 / (100 − 11.21), so it rescales | §4.4 |
| [23](23-dashboard-time-of-measure-percentiles.jpg) | Time of Measure: percentiles match the API's quartiles; continuous colour bar; "air temperature" | §2.6, §4.4 |
| [24](24-dashboard-heat-intelligence-description.jpg) | Heat Intelligence description mentions "sensors" and "heating systems" | §4.5 |
| [25](25-dashboard-heat-intelligence-report.jpg) | Report page with the LaGuardia 1936 claim and AQI 200 as "Very Unhealthy" | §4.5 |

## Selesious

| Screenshot | What it shows | Report |
|---|---|---|
| [30](30-selesious-outside-new-york.png) | "Lower Manhattan… is outside New York, the region your account covers" and "One heat map covers up to 150 mi²" | §5 |

## MCP (Claude Code)

| Screenshot | What it shows | Report |
|---|---|---|
| [40](40-mcp-docs-nine-tools.png) | Docs: "The current catalog contains nine tools" | §6.2 |
| [41](41-mcp-docs-claude-code-commands.png) | Docs: Mac/Linux-only setup commands (`export`, `\`) | §6.1 |
| [42](42-mcp-connected-11-tools.png) | Live server: connected, authenticated, **11 tools**, tools + resources | §6.1, §6.2 |
| [43](43-mcp-tool-list-11.png) | The 11 tools with read-only / destructive / open-world annotations | §6.2, §6.3 |
| [44](44-mcp-monitoring-tool-unknown-types.png) | `monitoring`: good cost and confirmation guidance, but parameter types "unknown" | §6.3 |
| [45](45-mcp-credit-balance-tool.png) | `credit_balance`: "Enterprise API credits; free and read-only" | §6.4 |
| [46](46-mcp-credit-balance-enterprise-guess.png) | Claude concludes I'm on an Enterprise plan from the tool's wording | §6.4 |
| [47](47-mcp-docs-heatmap-wait-for-completion.png) | Docs: `heatmap` accepts `wait_for_completion`; granularity 60/80/100 | §6.2 |
| [48](48-mcp-docs-streetview-back-view.png) | Docs: `back_view` is a "Required flag to include an optional back-view result" | §6.3 |
| [49](49-mcp-env-params-confirmation.png) | Claude shows parameters and cost and asks before a paid call | §6.3 |
| [50](50-mcp-env-params-results-heat-index.png) | Heat index from a fixed 35 °C peaks at 06:00 (44.7 °C) | §6.4 |
| [51](51-mcp-env-params-raw-first-hour-snapshot.png) | Raw response: `"basis": "first_hour_snapshot"`, timezone with ISO offset | §2.4, §6.4 |
| [52](52-mcp-env-params-raw-trace.png) | Raw `trace`: plan_type, cost_credits 2900, latency_ms 4070 | §6.3 |
| [53](53-mcp-heatmap-confirmation.png) | Heatmap request confirmed: 4,220 credits, 14:00 New York time | §6.4 |
| [54](54-mcp-heatmap-stats-only.png) | Same statistics as REST and dashboard; no tiles, count or link | §1, §6.4 |
| [55](55-mcp-heatmap-arguments-no-wait.png) | Live `heatmap` has no `wait_for_completion`; client slept 20 s and polled | §6.2 |
| [56](56-mcp-final-balance-976000.png) | Final balance 976,000: 24,000 credits used in total | How I tested |
