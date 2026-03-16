# 2026 March Madness Family Bracket Challenge

A single-file Streamlit app for filling out and exporting your 2026 NCAA Men's Basketball Tournament bracket. Built with a NYT Games-inspired aesthetic, it walks you through the entire bracket round by round and exports a polished PDF when you're done.

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run bracket_app.py
```

The app opens at `http://localhost:8501` in your browser.

---

## How to Use

### Phase 0 — Enter Your Name
When the app loads, enter your name and click **Start Bracket**. Your name appears in the sidebar and on the exported PDF.

### Phase 1 — First Four (Play-In Games)
Pick the winner of each of the four play-in games. These teams fill the corresponding Round of 64 slots:

| Matchup | Slot Filled |
|---------|-------------|
| UMBC vs. Howard | Midwest — Michigan's 16-seed |
| Texas vs. NC State | West — BYU's 11-seed |
| Prairie View A&M vs. Lehigh | South — Florida's 16-seed |
| Miami (OH) vs. SMU | Midwest — Tennessee's 11-seed |

### Phase 2 — Round of 64 (32 games)
All 32 first-round games organized by region in collapsible sections. Winners auto-populate into the Round of 32.

### Phase 3 — Round of 32 (16 games)
Pick from the Round of 64 winners. Games organized by region.

### Phase 4 — Sweet 16 (8 games)
The final sixteen teams, two games per region.

### Phase 5 — Elite Eight (4 games)
One game per region determines each Regional Champion.

### Phase 6 — Final Four (2 games)
- East Champion vs. West Champion
- Midwest Champion vs. South Champion

### Phase 7 — Championship (1 game)
Pick your 2026 National Champion. Click **Complete My Bracket** to finish.

### Phase 8 — Complete
Your champion is displayed in a celebratory banner. A full bracket summary is shown with all picks color-coded (green = winner, gray = eliminated).

---

## Exporting Your Bracket

On the completion screen, click **Generate PDF** and then **Download PDF Bracket**. The PDF includes:

- Your name and export date/time in the header
- All four regions with picks for every round (R64 through Elite Eight)
- Final Four matchups and results
- Your National Champion displayed prominently at the bottom
- Landscape orientation, clean Helvetica typography

The file saves as `{YourName}_bracket_2026.pdf`.

---

## Sidebar Features

The sidebar shows at all times:

- **Your name**
- **Progress bar** — X / 63 games completed
- **Champion Pick** — highlighted in green once selected
- **Current Round** — which phase you're on
- **Reset Bracket** — clears all picks and returns to Phase 0 (name entry)

---

## Bracket Color Guide

| Color | Meaning |
|-------|---------|
| Green | Team picked to win this game |
| Gray (strikethrough) | Team eliminated in this game |
| White | Game not yet picked |

---

## 2026 Tournament Structure

| Region | #1 Seed | Location |
|--------|---------|----------|
| East | Duke | — |
| West | Arizona | — |
| Midwest | Michigan | — |
| South | Florida | — |

**Note:** Houston's 15-seed in the South Region was listed as TBD at the time of app creation. Update line `south_r64_7` in `bracket_app.py` with the confirmed team name once available.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Runtime |
| [Streamlit](https://streamlit.io) | Web UI framework |
| [ReportLab](https://www.reportlab.com) | PDF generation |

No external API calls are made at runtime — all bracket data is hardcoded.

---

## File Structure

```
March Madness/
├── bracket_app.py       # Complete Streamlit application (single file)
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## Troubleshooting

**Radio buttons don't show previous pick after page interaction**
This is expected Streamlit behavior when widgets are first rendered. Picks are persisted in session state and re-applied on each interaction.

**"— Pending —" shown in bracket visual**
Upstream picks haven't been made yet. Complete earlier rounds first.

**PDF download doesn't appear immediately**
Click "Generate PDF" first; then a Download button will appear below it.

**Reset doesn't clear everything**
Click the sidebar **Reset Bracket** button. This clears all session state including widget states and returns you to the name entry screen.
