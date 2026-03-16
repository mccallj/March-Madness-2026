"""
2026 NCAA March Madness Family Bracket Challenge
Single-file Streamlit app — all bracket data hardcoded, no runtime API calls.
Run: streamlit run bracket_app.py
"""

# ── SECTION 1: Imports ────────────────────────────────────────────────────────
import copy
import io
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors as rl_colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ── SECTION 2: Constants ──────────────────────────────────────────────────────

FIRST_FOUR = [
    {
        "id": "ff0",
        "team_a": "UMBC",
        "team_b": "Howard",
        "label": "16-seed for Midwest — Michigan's opponent",
        "feeds_region": "midwest",
        "feeds_game": 0,
        "feeds_slot": "team_b",
    },
    {
        "id": "ff1",
        "team_a": "Texas",
        "team_b": "NC State",
        "label": "11-seed for West — BYU's opponent",
        "feeds_region": "west",
        "feeds_game": 4,
        "feeds_slot": "team_b",
    },
    {
        "id": "ff2",
        "team_a": "Prairie View A&M",
        "team_b": "Lehigh",
        "label": "16-seed for South — Florida's opponent",
        "feeds_region": "south",
        "feeds_game": 0,
        "feeds_slot": "team_b",
    },
    {
        "id": "ff3",
        "team_a": "Miami (OH)",
        "team_b": "SMU",
        "label": "11-seed for Midwest — Tennessee's opponent",
        "feeds_region": "midwest",
        "feeds_game": 4,
        "feeds_slot": "team_b",
    },
]

# Region game order: (1v16), (8v9), (5v12), (4v13), (6v11), (3v14), (7v10), (2v15)
REGIONS = {
    "east": {
        "name": "EAST",
        "matchups": [
            {"game_id": "east_r64_0", "seed_a": 1,  "team_a": "Duke",           "seed_b": 16, "team_b": "Siena",            "ff_ref": None},
            {"game_id": "east_r64_1", "seed_a": 8,  "team_a": "Ohio State",     "seed_b": 9,  "team_b": "TCU",              "ff_ref": None},
            {"game_id": "east_r64_2", "seed_a": 5,  "team_a": "St. John's",     "seed_b": 12, "team_b": "Northern Iowa",    "ff_ref": None},
            {"game_id": "east_r64_3", "seed_a": 4,  "team_a": "Kansas",         "seed_b": 13, "team_b": "Cal Baptist",      "ff_ref": None},
            {"game_id": "east_r64_4", "seed_a": 6,  "team_a": "Louisville",     "seed_b": 11, "team_b": "South Florida",    "ff_ref": None},
            {"game_id": "east_r64_5", "seed_a": 3,  "team_a": "Michigan State", "seed_b": 14, "team_b": "North Dakota St",  "ff_ref": None},
            {"game_id": "east_r64_6", "seed_a": 7,  "team_a": "UCLA",           "seed_b": 10, "team_b": "UCF",              "ff_ref": None},
            {"game_id": "east_r64_7", "seed_a": 2,  "team_a": "UConn",          "seed_b": 15, "team_b": "Furman",           "ff_ref": None},
        ],
    },
    "west": {
        "name": "WEST",
        "matchups": [
            {"game_id": "west_r64_0", "seed_a": 1,  "team_a": "Arizona",     "seed_b": 16, "team_b": "LIU",           "ff_ref": None},
            {"game_id": "west_r64_1", "seed_a": 8,  "team_a": "Villanova",   "seed_b": 9,  "team_b": "Utah State",    "ff_ref": None},
            {"game_id": "west_r64_2", "seed_a": 5,  "team_a": "Wisconsin",   "seed_b": 12, "team_b": "High Point",    "ff_ref": None},
            {"game_id": "west_r64_3", "seed_a": 4,  "team_a": "Arkansas",    "seed_b": 13, "team_b": "Hawaii",        "ff_ref": None},
            {"game_id": "west_r64_4", "seed_a": 6,  "team_a": "BYU",         "seed_b": 11, "team_b": "TBD",           "ff_ref": "ff1"},
            {"game_id": "west_r64_5", "seed_a": 3,  "team_a": "Gonzaga",     "seed_b": 14, "team_b": "Kennesaw St",   "ff_ref": None},
            {"game_id": "west_r64_6", "seed_a": 7,  "team_a": "Miami (FL)",  "seed_b": 10, "team_b": "Missouri",      "ff_ref": None},
            {"game_id": "west_r64_7", "seed_a": 2,  "team_a": "Purdue",      "seed_b": 15, "team_b": "Queens",        "ff_ref": None},
        ],
    },
    "midwest": {
        "name": "MIDWEST",
        "matchups": [
            {"game_id": "midwest_r64_0", "seed_a": 1,  "team_a": "Michigan",    "seed_b": 16, "team_b": "TBD",            "ff_ref": "ff0"},
            {"game_id": "midwest_r64_1", "seed_a": 8,  "team_a": "Georgia",     "seed_b": 9,  "team_b": "Saint Louis",    "ff_ref": None},
            {"game_id": "midwest_r64_2", "seed_a": 5,  "team_a": "Texas Tech",  "seed_b": 12, "team_b": "Akron",          "ff_ref": None},
            {"game_id": "midwest_r64_3", "seed_a": 4,  "team_a": "Alabama",     "seed_b": 13, "team_b": "Hofstra",        "ff_ref": None},
            {"game_id": "midwest_r64_4", "seed_a": 6,  "team_a": "Tennessee",   "seed_b": 11, "team_b": "TBD",            "ff_ref": "ff3"},
            {"game_id": "midwest_r64_5", "seed_a": 3,  "team_a": "Virginia",    "seed_b": 14, "team_b": "Wright State",   "ff_ref": None},
            {"game_id": "midwest_r64_6", "seed_a": 7,  "team_a": "Kentucky",    "seed_b": 10, "team_b": "Santa Clara",    "ff_ref": None},
            {"game_id": "midwest_r64_7", "seed_a": 2,  "team_a": "Iowa State",  "seed_b": 15, "team_b": "Tennessee St",   "ff_ref": None},
        ],
    },
    "south": {
        "name": "SOUTH",
        "matchups": [
            {"game_id": "south_r64_0", "seed_a": 1,  "team_a": "Florida",       "seed_b": 16, "team_b": "TBD",         "ff_ref": "ff2"},
            {"game_id": "south_r64_1", "seed_a": 8,  "team_a": "Clemson",       "seed_b": 9,  "team_b": "Iowa",        "ff_ref": None},
            {"game_id": "south_r64_2", "seed_a": 5,  "team_a": "Vanderbilt",    "seed_b": 12, "team_b": "McNeese",     "ff_ref": None},
            {"game_id": "south_r64_3", "seed_a": 4,  "team_a": "Nebraska",      "seed_b": 13, "team_b": "Troy",        "ff_ref": None},
            {"game_id": "south_r64_4", "seed_a": 6,  "team_a": "North Carolina","seed_b": 11, "team_b": "VCU",         "ff_ref": None},
            {"game_id": "south_r64_5", "seed_a": 3,  "team_a": "Illinois",      "seed_b": 14, "team_b": "Penn",        "ff_ref": None},
            {"game_id": "south_r64_6", "seed_a": 7,  "team_a": "Saint Mary's",  "seed_b": 10, "team_b": "Texas A&M",   "ff_ref": None},
            {"game_id": "south_r64_7", "seed_a": 2,  "team_a": "Houston",       "seed_b": 15, "team_b": "TBD",         "ff_ref": None},
        ],
    },
}

REGION_ORDER = ["east", "west", "midwest", "south"]

ROUND_LABELS = {
    2: "Round of 64",
    3: "Round of 32",
    4: "Sweet 16",
    5: "Elite Eight",
    6: "Final Four",
    7: "Championship",
}

ROUND_KEYS = {
    1: "first_four_picks",
    2: "picks_r64",
    3: "picks_r32",
    4: "picks_s16",
    5: "picks_e8",
    6: "picks_ff",
    7: "picks_championship",
}

ROUND_SIZES = {1: 4, 2: 32, 3: 16, 4: 8, 5: 4, 6: 2, 7: 1}

SESSION_STATE_DEFAULTS = {
    "current_phase": 0,
    "user_name": "",
    "first_four_picks": {},
    "picks_r64": {},
    "picks_r32": {},
    "picks_s16": {},
    "picks_e8": {},
    "picks_ff": {},
    "picks_championship": "",
}

# ── SECTION 3: Session State Management ──────────────────────────────────────

def init_session_state():
    for key, default in SESSION_STATE_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = copy.deepcopy(default)


def reset_session_state():
    for key, default in SESSION_STATE_DEFAULTS.items():
        st.session_state[key] = copy.deepcopy(default)
    # Clear widget state for all radio buttons
    widget_keys = [k for k in list(st.session_state.keys()) if k.startswith("w_")]
    for k in widget_keys:
        del st.session_state[k]
    st.rerun()


def count_total_picks():
    total = 0
    for k in ["picks_r64", "picks_r32", "picks_s16", "picks_e8", "picks_ff"]:
        total += len(st.session_state.get(k, {}))
    if st.session_state.get("picks_championship"):
        total += 1
    return total

# ── SECTION 4: Matchup Resolution ─────────────────────────────────────────────

def resolve_tbd_teams():
    """Return a deep copy of REGIONS with First Four TBD slots filled."""
    resolved = copy.deepcopy(REGIONS)
    ff_picks = st.session_state.get("first_four_picks", {})
    for ff in FIRST_FOUR:
        winner = ff_picks.get(ff["id"])
        if winner:
            region = ff["feeds_region"]
            game_idx = ff["feeds_game"]
            slot = ff["feeds_slot"]
            resolved[region]["matchups"][game_idx][slot] = winner
    return resolved


def get_r32_matchups(region_key):
    matchups = []
    for i in range(4):
        a_id = f"{region_key}_r64_{i * 2}"
        b_id = f"{region_key}_r64_{i * 2 + 1}"
        team_a = st.session_state["picks_r64"].get(a_id)
        team_b = st.session_state["picks_r64"].get(b_id)
        matchups.append({
            "game_id": f"{region_key}_r32_{i}",
            "team_a": team_a,
            "team_b": team_b,
        })
    return matchups


def get_s16_matchups(region_key):
    matchups = []
    for i in range(2):
        a_id = f"{region_key}_r32_{i * 2}"
        b_id = f"{region_key}_r32_{i * 2 + 1}"
        team_a = st.session_state["picks_r32"].get(a_id)
        team_b = st.session_state["picks_r32"].get(b_id)
        matchups.append({
            "game_id": f"{region_key}_s16_{i}",
            "team_a": team_a,
            "team_b": team_b,
        })
    return matchups


def get_e8_matchup(region_key):
    team_a = st.session_state["picks_s16"].get(f"{region_key}_s16_0")
    team_b = st.session_state["picks_s16"].get(f"{region_key}_s16_1")
    return {"game_id": f"{region_key}_e8_0", "team_a": team_a, "team_b": team_b}


def get_ff_matchups():
    return [
        {
            "game_id": "ff_game_0",
            "label": "East Champion vs. West Champion",
            "team_a": st.session_state["picks_e8"].get("east_e8_0"),
            "team_b": st.session_state["picks_e8"].get("west_e8_0"),
        },
        {
            "game_id": "ff_game_1",
            "label": "Midwest Champion vs. South Champion",
            "team_a": st.session_state["picks_e8"].get("midwest_e8_0"),
            "team_b": st.session_state["picks_e8"].get("south_e8_0"),
        },
    ]


def get_championship_matchup():
    return {
        "game_id": "championship",
        "team_a": st.session_state["picks_ff"].get("ff_game_0"),
        "team_b": st.session_state["picks_ff"].get("ff_game_1"),
    }

# ── SECTION 5: Validation ─────────────────────────────────────────────────────

def is_round_complete(phase):
    rk = ROUND_KEYS.get(phase)
    if not rk:
        return False
    if rk == "picks_championship":
        return bool(st.session_state.get("picks_championship"))
    return len(st.session_state.get(rk, {})) == ROUND_SIZES[phase]


def get_team_status(team, game_id, round_key):
    """Return 'picked', 'eliminated', or 'unpicked'."""
    pick = st.session_state.get(round_key, {}).get(game_id)
    if pick is None:
        return "unpicked"
    return "picked" if pick == team else "eliminated"

# ── SECTION 6: Visual Bracket HTML ───────────────────────────────────────────

def _bracket_css():
    return """
    /* ── CSS tokens — light defaults ── */
    :root {
        --bg:           #F9FAFB;
        --surface:      #FFFFFF;
        --txt:          #111827;
        --txt-muted:    #6B7280;
        --txt-faint:    #9CA3AF;
        --border:       #D1D5DB;
        --line:         rgba(150,160,180,0.45);
        --picked-bg:    #6aaa64;
        --picked-txt:   #ffffff;
        --elim-bg:      #787c7e;
        --elim-txt:     #ffffff;
        --sep:          #E5E7EB;
        --ff-bg:        #F3F4F6;
        --champ-color:  #6aaa64;
    }
    /* ── Dark mode overrides ── */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg:           #0E1117;
            --surface:      #1C2333;
            --txt:          #F0F4FF;
            --txt-muted:    #8899BB;
            --txt-faint:    #4D618A;
            --border:       #2D3D5A;
            --line:         rgba(100,120,160,0.5);
            --picked-bg:    #166534;
            --picked-txt:   #86efac;
            --elim-bg:      #1f2937;
            --elim-txt:     #6B7280;
            --sep:          #1A2540;
            --ff-bg:        #252D42;
            --champ-color:  #4ade80;
        }
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: 'Source Sans 3', 'Helvetica Neue', Arial, sans-serif;
        background: var(--bg);
        padding: 16px;
        color: var(--txt);
    }
    .bracket-title {
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 16px;
        color: var(--txt);
    }
    .region-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 6px;
        color: var(--txt-muted);
    }
    .ts {
        height: 24px;
        width: 148px;
        border: 1.5px solid var(--border);
        display: flex;
        align-items: center;
        padding: 0 5px;
        font-size: 10.5px;
        font-weight: 500;
        background: var(--surface);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        border-radius: 2px;
        color: var(--txt);
    }
    .ts.picked {
        background: var(--picked-bg);
        border-color: var(--picked-bg);
        color: var(--picked-txt);
        font-weight: 700;
    }
    .ts.eliminated {
        background: var(--elim-bg);
        border-color: var(--elim-bg);
        color: var(--elim-txt);
        text-decoration: line-through;
        opacity: 0.85;
    }
    .ts.unpicked {
        background: var(--surface);
        color: var(--txt);
    }
    .ts .seed {
        font-size: 9px;
        font-weight: 700;
        min-width: 16px;
        color: inherit;
        opacity: 0.75;
    }
    .ts.picked .seed, .ts.eliminated .seed {
        color: inherit;
    }
    .ff-section {
        text-align: center;
        margin: 24px auto;
        max-width: 800px;
    }
    .ff-title {
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--txt-muted);
        margin-bottom: 12px;
    }
    .ff-game {
        display: inline-flex;
        flex-direction: column;
        margin: 0 16px;
        vertical-align: top;
    }
    .ff-game-label {
        font-size: 9px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--txt-faint);
        text-align: center;
        margin-bottom: 4px;
    }
    .ff-vs {
        font-size: 9px;
        text-align: center;
        color: var(--txt-faint);
        padding: 2px 0;
    }
    .champ-section {
        text-align: center;
        margin: 20px auto;
    }
    .champ-label {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--txt-muted);
        margin-bottom: 8px;
    }
    .champ-name {
        font-size: 22px;
        font-weight: 900;
        color: var(--champ-color);
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .champ-pending {
        font-size: 18px;
        font-weight: 700;
        color: var(--txt-faint);
        letter-spacing: 1px;
    }
    .regions-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 24px;
        margin-bottom: 24px;
    }
    .separator {
        border: none;
        border-top: 2px solid var(--sep);
        margin: 16px 0;
    }
    """


def _render_game_slot(team, seed, game_id, round_key, show_seed=True):
    if not team or team == "TBD":
        display = "— Pending —"
        return f'<div class="ts unpicked"><span class="seed"></span>{display}</div>'
    status = get_team_status(team, game_id, round_key)
    seed_html = f'<span class="seed">{seed}&nbsp;</span>' if show_seed and seed else '<span class="seed"></span>'
    safe_team = team.replace("&", "&amp;").replace("<", "&lt;")
    return f'<div class="ts {status}">{seed_html}{safe_team}</div>'


def _build_region_bracket_html(region_key, resolved_regions):
    """Build SVG+HTML for one region's bracket (R64 → R32 → S16 → E8)."""
    SLOT_H = 24
    GAP = 3
    PAIR_H = SLOT_H * 2 + GAP
    GAME_H = 62
    H = 8 * GAME_H   # 496px
    COL_W = 150
    CONN_W = 20
    TOTAL_W = COL_W * 4 + CONN_W * 3  # 660px

    col_x = {
        0: 0,
        1: COL_W + CONN_W,
        2: (COL_W + CONN_W) * 2,
        3: (COL_W + CONN_W) * 3,
    }

    def cy(round_idx, game_idx):
        return (game_idx + 0.5) * GAME_H * (2 ** round_idx)

    region = resolved_regions[region_key]
    matchups_r64 = region["matchups"]

    slot_divs = []
    svg_lines = []

    # ── R64 slots ──
    for i, m in enumerate(matchups_r64):
        center = cy(0, i)
        top = center - PAIR_H / 2
        a = _render_game_slot(m["team_a"], m["seed_a"], m["game_id"], "picks_r64", show_seed=True)
        b = _render_game_slot(m["team_b"], m["seed_b"], m["game_id"], "picks_r64", show_seed=True)
        slot_divs.append(
            f'<div style="position:absolute;left:{col_x[0]}px;top:{top:.1f}px;">'
            f'{a}<div style="height:{GAP}px;"></div>{b}</div>'
        )

    # ── R32 matchups + slots ──
    r32 = get_r32_matchups(region_key)
    for i, m in enumerate(r32):
        center = cy(1, i)
        top = center - PAIR_H / 2
        a = _render_game_slot(m["team_a"], None, m["game_id"], "picks_r32", show_seed=False)
        b = _render_game_slot(m["team_b"], None, m["game_id"], "picks_r32", show_seed=False)
        slot_divs.append(
            f'<div style="position:absolute;left:{col_x[1]}px;top:{top:.1f}px;">'
            f'{a}<div style="height:{GAP}px;"></div>{b}</div>'
        )
        # SVG: R64→R32 connectors
        ca = cy(0, i * 2)
        cb = cy(0, i * 2 + 1)
        vx = col_x[0] + COL_W + CONN_W // 2
        svg_lines += [
            f'<line x1="{col_x[0]+COL_W}" y1="{ca:.1f}" x2="{vx}" y2="{ca:.1f}" stroke="var(--line)" stroke-width="1.5"/>',
            f'<line x1="{col_x[0]+COL_W}" y1="{cb:.1f}" x2="{vx}" y2="{cb:.1f}" stroke="var(--line)" stroke-width="1.5"/>',
            f'<line x1="{vx}" y1="{ca:.1f}" x2="{vx}" y2="{cb:.1f}" stroke="var(--line)" stroke-width="1.5"/>',
            f'<line x1="{vx}" y1="{center:.1f}" x2="{col_x[1]}" y2="{center:.1f}" stroke="var(--line)" stroke-width="1.5"/>',
        ]

    # ── S16 matchups + slots ──
    s16 = get_s16_matchups(region_key)
    for i, m in enumerate(s16):
        center = cy(2, i)
        top = center - PAIR_H / 2
        a = _render_game_slot(m["team_a"], None, m["game_id"], "picks_s16", show_seed=False)
        b = _render_game_slot(m["team_b"], None, m["game_id"], "picks_s16", show_seed=False)
        slot_divs.append(
            f'<div style="position:absolute;left:{col_x[2]}px;top:{top:.1f}px;">'
            f'{a}<div style="height:{GAP}px;"></div>{b}</div>'
        )
        # SVG: R32→S16 connectors
        ca = cy(1, i * 2)
        cb = cy(1, i * 2 + 1)
        vx = col_x[1] + COL_W + CONN_W // 2
        svg_lines += [
            f'<line x1="{col_x[1]+COL_W}" y1="{ca:.1f}" x2="{vx}" y2="{ca:.1f}" stroke="var(--line)" stroke-width="1.5"/>',
            f'<line x1="{col_x[1]+COL_W}" y1="{cb:.1f}" x2="{vx}" y2="{cb:.1f}" stroke="var(--line)" stroke-width="1.5"/>',
            f'<line x1="{vx}" y1="{ca:.1f}" x2="{vx}" y2="{cb:.1f}" stroke="var(--line)" stroke-width="1.5"/>',
            f'<line x1="{vx}" y1="{center:.1f}" x2="{col_x[2]}" y2="{center:.1f}" stroke="var(--line)" stroke-width="1.5"/>',
        ]

    # ── E8 matchup + slot ──
    e8 = get_e8_matchup(region_key)
    center = cy(3, 0)
    top = center - PAIR_H / 2
    a = _render_game_slot(e8["team_a"], None, e8["game_id"], "picks_e8", show_seed=False)
    b = _render_game_slot(e8["team_b"], None, e8["game_id"], "picks_e8", show_seed=False)
    slot_divs.append(
        f'<div style="position:absolute;left:{col_x[3]}px;top:{top:.1f}px;">'
        f'{a}<div style="height:{GAP}px;"></div>{b}</div>'
    )
    # SVG: S16→E8 connectors
    ca = cy(2, 0)
    cb = cy(2, 1)
    vx = col_x[2] + COL_W + CONN_W // 2
    svg_lines += [
        f'<line x1="{col_x[2]+COL_W}" y1="{ca:.1f}" x2="{vx}" y2="{ca:.1f}" stroke="var(--line)" stroke-width="1.5"/>',
        f'<line x1="{col_x[2]+COL_W}" y1="{cb:.1f}" x2="{vx}" y2="{cb:.1f}" stroke="var(--line)" stroke-width="1.5"/>',
        f'<line x1="{vx}" y1="{ca:.1f}" x2="{vx}" y2="{cb:.1f}" stroke="var(--line)" stroke-width="1.5"/>',
        f'<line x1="{vx}" y1="{center:.1f}" x2="{col_x[3]}" y2="{center:.1f}" stroke="var(--line)" stroke-width="1.5"/>',
    ]

    round_headers = [
        (col_x[0], "Round of 64"),
        (col_x[1], "Round of 32"),
        (col_x[2], "Sweet 16"),
        (col_x[3], "Elite Eight"),
    ]
    header_html = "".join(
        f'<div style="position:absolute;left:{x}px;top:-22px;width:{COL_W}px;'
        f'font-size:9px;font-weight:700;letter-spacing:1px;text-transform:uppercase;'
        f'color:#888;text-align:center;">{lbl}</div>'
        for x, lbl in round_headers
    )

    return (
        f'<div class="region-label">{region["name"]}</div>'
        f'<div style="position:relative;width:{TOTAL_W}px;height:{H + 30}px;">'
        f'<div style="position:absolute;top:22px;left:0;width:{TOTAL_W}px;height:{H}px;">'
        f'{header_html}'
        f'<svg style="position:absolute;top:0;left:0;width:{TOTAL_W}px;height:{H}px;overflow:visible;"'
        f' xmlns="http://www.w3.org/2000/svg">{"".join(svg_lines)}</svg>'
        f'{"".join(slot_divs)}'
        f'</div>'
        f'</div>'
    )


def _build_ff_championship_html():
    ff = get_ff_matchups()
    champ = get_championship_matchup()
    champion = st.session_state.get("picks_championship", "")

    def ff_slot(team, game_id, rk):
        if not team:
            return '<div class="ts unpicked" style="width:160px;"><span class="seed"></span>— Pending —</div>'
        status = get_team_status(team, game_id, rk)
        safe = team.replace("&", "&amp;")
        return f'<div class="ts {status}" style="width:160px;"><span class="seed"></span>{safe}</div>'

    ff_html_parts = []
    for m in ff:
        a = ff_slot(m["team_a"], m["game_id"], "picks_ff")
        b = ff_slot(m["team_b"], m["game_id"], "picks_ff")
        ff_html_parts.append(
            f'<div class="ff-game">'
            f'<div class="ff-game-label">{m["label"]}</div>'
            f'{a}<div class="ff-vs">vs.</div>{b}'
            f'</div>'
        )

    if champion:
        champ_display = (
            f'<div class="champ-name">{champion.replace("&", "&amp;")}</div>'
        )
    else:
        ca = ff_slot(champ["team_a"], "championship", "picks_championship")
        cb = ff_slot(champ["team_b"], "championship", "picks_championship")
        champ_display = (
            f'{ca}<div class="ff-vs">vs.</div>{cb}'
            f'<div class="champ-pending">Champion TBD</div>'
        )

    return (
        f'<hr class="separator">'
        f'<div class="ff-section">'
        f'<div class="ff-title">Final Four</div>'
        f'<div>{"".join(ff_html_parts)}</div>'
        f'</div>'
        f'<hr class="separator">'
        f'<div class="champ-section">'
        f'<div class="champ-label">Championship</div>'
        f'{champ_display}'
        f'</div>'
    )


def build_bracket_html():
    resolved = resolve_tbd_teams()
    css = _bracket_css()

    region_blocks = []
    for rk in REGION_ORDER:
        region_blocks.append(_build_region_bracket_html(rk, resolved))

    ff_champ = _build_ff_championship_html()

    grid = (
        f'<div class="regions-grid">'
        f'<div>{region_blocks[0]}</div>'
        f'<div>{region_blocks[1]}</div>'
        f'<div>{region_blocks[2]}</div>'
        f'<div>{region_blocks[3]}</div>'
        f'</div>'
    )

    return (
        f'<!DOCTYPE html><html><head><meta charset="utf-8">'
        f'<style>{css}</style></head><body>'
        f'<div class="bracket-title">2026 NCAA March Madness Bracket</div>'
        f'{grid}'
        f'{ff_champ}'
        f'</body></html>'
    )

# ── SECTION 7: PDF Export ─────────────────────────────────────────────────────

def generate_pdf(user_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=0.4 * inch,
        leftMargin=0.4 * inch,
        topMargin=0.35 * inch,
        bottomMargin=0.35 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "BTitle", fontName="Helvetica-Bold", fontSize=15,
        alignment=TA_CENTER, spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "BSub", fontName="Helvetica", fontSize=8,
        alignment=TA_CENTER, spaceAfter=10,
        textColor=rl_colors.HexColor("#555555"),
    )
    region_hdr = ParagraphStyle(
        "RHdr", fontName="Helvetica-Bold", fontSize=9,
        spaceAfter=4, textColor=rl_colors.HexColor("#000000"),
    )
    round_hdr = ParagraphStyle(
        "RdHdr", fontName="Helvetica-BoldOblique", fontSize=7.5,
        spaceBefore=4, spaceAfter=2,
        textColor=rl_colors.HexColor("#333333"),
    )
    team_style = ParagraphStyle(
        "Team", fontName="Helvetica", fontSize=7.5,
        leftIndent=6, spaceAfter=1,
    )
    team_winner = ParagraphStyle(
        "Winner", fontName="Helvetica-Bold", fontSize=7.5,
        leftIndent=6, spaceAfter=1,
        textColor=rl_colors.HexColor("#6aaa64"),
    )
    champ_style = ParagraphStyle(
        "Champ", fontName="Helvetica-Bold", fontSize=14,
        alignment=TA_CENTER, spaceBefore=8, spaceAfter=4,
        textColor=rl_colors.HexColor("#6aaa64"),
    )
    champ_lbl = ParagraphStyle(
        "ChampLbl", fontName="Helvetica-Bold", fontSize=9,
        alignment=TA_CENTER, spaceBefore=6, spaceAfter=2,
        textColor=rl_colors.HexColor("#555555"),
    )

    def pick_para(team, game_id, round_key):
        if not team:
            return Paragraph("—", team_style)
        status = get_team_status(team, game_id, round_key)
        safe = team.replace("&", "&amp;")
        style = team_winner if status == "picked" else team_style
        prefix = "✓ " if status == "picked" else "  "
        return Paragraph(f"{prefix}{safe}", style)

    def build_region_col(region_key):
        items = []
        region = REGIONS[region_key]
        items.append(Paragraph(region["name"], region_hdr))

        # R64
        items.append(Paragraph("Round of 64", round_hdr))
        for m in region["matchups"]:
            items.append(pick_para(m["team_a"], m["game_id"], "picks_r64"))
            items.append(pick_para(m["team_b"], m["game_id"], "picks_r64"))
            items.append(Spacer(1, 2))

        # R32
        items.append(Paragraph("Round of 32", round_hdr))
        for i in range(4):
            gid = f"{region_key}_r32_{i}"
            winner = st.session_state["picks_r32"].get(gid, "—")
            safe = winner.replace("&", "&amp;") if winner and winner != "—" else "—"
            items.append(Paragraph(f"  {safe}", team_style))

        # S16
        items.append(Paragraph("Sweet 16", round_hdr))
        for i in range(2):
            gid = f"{region_key}_s16_{i}"
            winner = st.session_state["picks_s16"].get(gid, "—")
            safe = winner.replace("&", "&amp;") if winner and winner != "—" else "—"
            items.append(Paragraph(f"  {safe}", team_style))

        # E8
        items.append(Paragraph("Elite Eight", round_hdr))
        gid = f"{region_key}_e8_0"
        winner = st.session_state["picks_e8"].get(gid, "—")
        safe = winner.replace("&", "&amp;") if winner and winner != "—" else "—"
        items.append(Paragraph(f"  {safe}", team_winner if winner and winner != "—" else team_style))

        return items

    # Build 4-column region table
    col_data = [build_region_col(rk) for rk in REGION_ORDER]
    max_rows = max(len(c) for c in col_data)
    empty = Paragraph("", team_style)
    rows = []
    for i in range(max_rows):
        row = [col_data[r][i] if i < len(col_data[r]) else empty for r in range(4)]
        rows.append(row)

    avail_w = 10.2 * inch
    col_w = avail_w / 4
    region_table = Table(rows, colWidths=[col_w] * 4, repeatRows=0)
    region_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LINEAFTER", (0, 0), (2, -1), 0.5, rl_colors.HexColor("#cccccc")),
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#f0f0f0")),
    ]))

    # Final Four section
    ff_data = []
    for m in get_ff_matchups():
        a = m["team_a"] or "—"
        b = m["team_b"] or "—"
        w = st.session_state["picks_ff"].get(m["game_id"], "—")
        ff_data.append([
            Paragraph(m["label"], ParagraphStyle("ffl", fontName="Helvetica-Bold",
                fontSize=7.5, textColor=rl_colors.HexColor("#555"))),
            Paragraph(f"{a} vs. {b}", ParagraphStyle("ffm", fontName="Helvetica",
                fontSize=7.5)),
            Paragraph(f"Winner: {w}", ParagraphStyle("ffw", fontName="Helvetica-Bold",
                fontSize=7.5, textColor=rl_colors.HexColor("#6aaa64"))),
        ])

    champion = st.session_state.get("picks_championship") or "—"

    export_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story = [
        Paragraph(f"{user_name}'s 2026 March Madness Bracket", title_style),
        Paragraph(f"Exported {export_time}", sub_style),
        region_table,
        Spacer(1, 8),
        Paragraph("FINAL FOUR", ParagraphStyle("ffhdr", fontName="Helvetica-Bold",
            fontSize=9, alignment=TA_CENTER, textColor=rl_colors.HexColor("#555"), spaceBefore=4)),
    ]

    if ff_data:
        ff_table = Table(ff_data, colWidths=[avail_w * 0.35, avail_w * 0.40, avail_w * 0.25])
        ff_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("BOX", (0, 0), (-1, -1), 0.5, rl_colors.HexColor("#cccccc")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, rl_colors.HexColor("#cccccc")),
        ]))
        story.append(ff_table)

    story += [
        Paragraph("2026 NCAA CHAMPION", champ_lbl),
        Paragraph(champion.replace("&", "&amp;"), champ_style),
    ]

    doc.build(story)
    return buffer.getvalue()

# ── SECTION 8: CSS Injection (light + dark adaptive) ─────────────────────────

def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:ital,wght@0,300;0,400;0,600;0,700;1,400&display=swap');

        /* ══════════════════════════════════════════════════════════════════
           DESIGN TOKENS — light defaults
           ══════════════════════════════════════════════════════════════════ */
        :root {
            --bg-app:      #FAFAF8;
            --bg-sidebar:  #F9FAFB;
            --bg-surface:  #FFFFFF;
            --bg-chip:     #F3F4F6;

            --txt-primary: #111827;
            --txt-body:    #374151;
            --txt-muted:   #6B7280;
            --txt-faint:   #9CA3AF;

            --bdr-strong:  #111827;
            --bdr-mid:     #D1D5DB;
            --bdr-light:   #E5E7EB;

            --accent:      #C84B31;
            --green:       #6aaa64;
            --green-dim:   #15803d;
        }

        /* ══════════════════════════════════════════════════════════════════
           DARK MODE — OS / browser preference
           ══════════════════════════════════════════════════════════════════ */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-app:      #0E1117;
                --bg-sidebar:  #161C2D;
                --bg-surface:  #1C2333;
                --bg-chip:     #252D42;

                --txt-primary: #F0F4FF;
                --txt-body:    #C8D4EC;
                --txt-muted:   #8899BB;
                --txt-faint:   #4D618A;

                --bdr-strong:  #E0E8FF;
                --bdr-mid:     #2D3D5A;
                --bdr-light:   #1A2540;

                --accent:      #FF6B4A;
                --green:       #4ade80;
                --green-dim:   #166534;
            }
        }

        /* ══════════════════════════════════════════════════════════════════
           DARK MODE — Streamlit's explicit theme toggle
           ══════════════════════════════════════════════════════════════════ */
        [data-theme="dark"],
        [data-theme="dark"] :root {
            --bg-app:      #0E1117;
            --bg-sidebar:  #161C2D;
            --bg-surface:  #1C2333;
            --bg-chip:     #252D42;
            --txt-primary: #F0F4FF;
            --txt-body:    #C8D4EC;
            --txt-muted:   #8899BB;
            --txt-faint:   #4D618A;
            --bdr-strong:  #E0E8FF;
            --bdr-mid:     #2D3D5A;
            --bdr-light:   #1A2540;
            --accent:      #FF6B4A;
            --green:       #4ade80;
            --green-dim:   #166534;
        }

        /* ══════════════════════════════════════════════════════════════════
           BASE RESETS
           ══════════════════════════════════════════════════════════════════ */
        html, body, [class*="css"] {
            font-family: 'Source Sans 3', 'Helvetica Neue', Arial, sans-serif;
        }
        .main .block-container {
            padding-top: 1.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
            padding-bottom: 3rem;
            max-width: 1300px;
        }
        .stApp {
            background-color: var(--bg-app) !important;
        }
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"],
        [data-testid="block-container"] {
            background-color: var(--bg-app) !important;
        }
        hr { border-color: var(--bdr-light) !important; }
        #MainMenu { visibility: hidden; }
        footer     { visibility: hidden; }

        /* ══════════════════════════════════════════════════════════════════
           TYPOGRAPHY
           ══════════════════════════════════════════════════════════════════ */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
            font-family: 'Playfair Display', Georgia, serif !important;
            color: var(--txt-primary) !important;
        }
        .stApp p, .stMarkdown p, .stMarkdown li {
            color: var(--txt-body) !important;
            font-family: 'Source Sans 3', 'Helvetica Neue', Arial, sans-serif !important;
        }

        /* ══════════════════════════════════════════════════════════════════
           PAGE HERO / PHASE HEADERS
           ══════════════════════════════════════════════════════════════════ */
        .app-hero {
            border-top: 4px solid var(--bdr-strong);
            border-bottom: 1px solid var(--bdr-mid);
            padding: 1.25rem 0 1.1rem;
            margin-bottom: 1.75rem;
        }
        .hero-eyebrow, .phase-eyebrow {
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--txt-muted);
            margin-bottom: 0.25rem;
        }
        .phase-eyebrow { color: var(--accent); }
        .hero-title {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: clamp(2rem, 4.5vw, 3rem);
            font-weight: 900;
            color: var(--txt-primary);
            line-height: 1.05;
            letter-spacing: -0.02em;
            margin-bottom: 0.4rem;
        }
        .phase-title {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 2rem;
            font-weight: 900;
            color: var(--txt-primary);
            line-height: 1.1;
            letter-spacing: -0.02em;
            margin-bottom: 0.3rem;
            border-bottom: 2px solid var(--bdr-mid);
            padding-bottom: 0.5rem;
        }
        .hero-sub, .phase-sub {
            font-family: 'Source Sans 3', sans-serif;
            font-size: 1rem;
            font-weight: 300;
            color: var(--txt-body);
            line-height: 1.6;
            max-width: 640px;
            margin: 0;
        }

        /* ══════════════════════════════════════════════════════════════════
           STAT CHIPS ROW
           ══════════════════════════════════════════════════════════════════ */
        .chips-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin: 1rem 0 1.5rem;
        }
        .stat-chip {
            flex: 1 1 140px;
            min-width: 120px;
            background: var(--bg-surface);
            border: 1px solid var(--bdr-mid);
            border-radius: 8px;
            padding: 0.65rem 1rem;
        }
        .chip-label {
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--txt-faint);
            margin-bottom: 0.15rem;
        }
        .chip-value {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.6rem;
            font-weight: 900;
            color: var(--txt-primary);
            line-height: 1.1;
        }
        .chip-value.accent { color: var(--accent); }
        .chip-value.green  { color: var(--green);  }
        .chip-sub {
            font-size: 0.72rem;
            color: var(--txt-muted);
            margin-top: 0.1rem;
        }

        /* ══════════════════════════════════════════════════════════════════
           SECTION HEAD
           ══════════════════════════════════════════════════════════════════ */
        .section-head {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--txt-primary);
            border-bottom: 2px solid var(--bdr-strong);
            padding-bottom: 0.3rem;
            margin-bottom: 1rem;
            margin-top: 0.5rem;
        }

        /* ══════════════════════════════════════════════════════════════════
           CHAMPION CARD
           ══════════════════════════════════════════════════════════════════ */
        .champion-card {
            border-left: 5px solid var(--green);
            background: var(--bg-surface);
            border: 1px solid var(--bdr-mid);
            border-left: 5px solid var(--green);
            border-radius: 0 8px 8px 0;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
        }
        .champion-label {
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--txt-muted);
            margin-bottom: 0.4rem;
        }
        .champion-name {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 2.75rem;
            font-weight: 900;
            color: var(--green);
            line-height: 1.05;
        }
        .champion-sub {
            font-size: 0.9rem;
            color: var(--txt-muted);
            margin-top: 0.3rem;
        }

        /* ══════════════════════════════════════════════════════════════════
           SIDEBAR
           ══════════════════════════════════════════════════════════════════ */
        [data-testid="stSidebar"] {
            background: var(--bg-sidebar) !important;
            border-right: 1px solid var(--bdr-light) !important;
        }
        .sidebar-brand {
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--txt-muted);
            margin-bottom: 0.25rem;
        }
        .sidebar-title {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.15rem;
            font-weight: 900;
            color: var(--txt-primary);
            line-height: 1.15;
            margin-bottom: 1rem;
        }
        .sidebar-row {
            font-size: 0.85rem;
            color: var(--txt-body);
            margin-bottom: 0.3rem;
        }
        .sidebar-row strong {
            color: var(--txt-primary);
            font-weight: 700;
        }
        .sidebar-champ {
            border-left: 4px solid var(--green);
            padding: 0.6rem 0.9rem;
            background: var(--bg-chip);
            border-radius: 0 6px 6px 0;
            margin: 0.75rem 0;
        }
        .sidebar-champ-label {
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--txt-muted);
        }
        .sidebar-champ-name {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1rem;
            font-weight: 700;
            color: var(--green);
        }
        .sidebar-footer {
            font-size: 0.72rem;
            color: var(--txt-faint);
            padding-top: 0.5rem;
            border-top: 1px solid var(--bdr-light);
            margin-top: 0.75rem;
        }

        /* ══════════════════════════════════════════════════════════════════
           EXPANDERS
           ══════════════════════════════════════════════════════════════════ */
        div[data-testid="stExpander"] {
            border: 1px solid var(--bdr-mid) !important;
            border-radius: 6px !important;
            background: var(--bg-surface) !important;
            margin-bottom: 10px !important;
        }
        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] > details > summary {
            background: var(--bg-chip) !important;
            border-radius: 6px 6px 0 0 !important;
        }
        /* Only target the text label (p) — NOT span, which carries Streamlit's
           Material Icons chevron glyph. Overriding font-family on that span
           breaks the icon and renders raw text like "arrow_down". */
        div[data-testid="stExpander"] summary p {
            color: var(--txt-primary) !important;
            font-weight: 600 !important;
            font-family: 'Source Sans 3', sans-serif !important;
        }
        /* Chevron icon span — preserve the icon font, just fix colour */
        div[data-testid="stExpander"] summary span {
            color: var(--txt-muted) !important;
        }
        div[data-testid="stExpander"] [data-testid="stExpanderDetails"],
        div[data-testid="stExpander"] details > div {
            background: var(--bg-surface) !important;
        }

        /* ══════════════════════════════════════════════════════════════════
           RADIO BUTTONS
           ══════════════════════════════════════════════════════════════════ */
        div[data-testid="stRadio"] label,
        div[data-testid="stRadio"] label span,
        div[data-testid="stRadio"] label p {
            color: var(--txt-body) !important;
            font-family: 'Source Sans 3', sans-serif !important;
            font-size: 14px !important;
        }
        div[data-testid="stRadio"] input[type="radio"] + div {
            border-color: var(--bdr-mid) !important;
        }
        div[data-testid="stRadio"] input[type="radio"]:checked + div {
            background-color: var(--accent) !important;
            border-color:     var(--accent) !important;
        }

        /* ══════════════════════════════════════════════════════════════════
           TEXT INPUT
           ══════════════════════════════════════════════════════════════════ */
        .stTextInput > div > div > input {
            background: var(--bg-surface) !important;
            color: var(--txt-primary) !important;
            border: 2px solid var(--bdr-mid) !important;
            border-radius: 6px !important;
            font-family: 'Source Sans 3', sans-serif !important;
            font-size: 15px !important;
            padding: 8px 12px !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px rgba(200,75,49,0.15) !important;
        }
        .stTextInput label, .stTextInput label span {
            color: var(--txt-muted) !important;
        }

        /* ══════════════════════════════════════════════════════════════════
           BUTTONS
           ══════════════════════════════════════════════════════════════════ */
        .stButton > button {
            background-color: var(--txt-primary) !important;
            color: var(--bg-app) !important;
            border: none !important;
            border-radius: 4px !important;
            font-family: 'Source Sans 3', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            font-size: 12px !important;
            padding: 8px 22px !important;
            transition: opacity 0.15s !important;
        }
        .stButton > button:hover { opacity: 0.82 !important; }
        .stButton > button[kind="secondary"],
        .stButton > button[data-testid="baseButton-secondary"] {
            background-color: transparent !important;
            color: var(--txt-primary) !important;
            border: 1.5px solid var(--bdr-mid) !important;
        }
        .stButton > button[kind="secondary"]:hover {
            background-color: var(--bg-chip) !important;
        }
        .stDownloadButton > button {
            background-color: var(--txt-primary) !important;
            color: var(--bg-app) !important;
            border: none !important;
            border-radius: 4px !important;
            font-weight: 700 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            font-size: 12px !important;
        }

        /* ══════════════════════════════════════════════════════════════════
           PROGRESS BAR
           ══════════════════════════════════════════════════════════════════ */
        [data-testid="stProgressBar"] > div,
        .stProgress > div > div > div > div {
            background-color: var(--green) !important;
        }
        [data-testid="stProgressBar"],
        .stProgress > div > div {
            background-color: var(--bdr-mid) !important;
        }

        /* ══════════════════════════════════════════════════════════════════
           ALERTS
           ══════════════════════════════════════════════════════════════════ */
        div[data-testid="stAlert"] {
            border-radius: 6px !important;
            background: var(--bg-chip) !important;
        }
        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] span {
            color: var(--txt-body) !important;
        }

        /* ══════════════════════════════════════════════════════════════════
           GAME DIVIDER
           ══════════════════════════════════════════════════════════════════ */
        .game-divider {
            border: none !important;
            border-top: 1px solid var(--bdr-light) !important;
            margin: 8px 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ── SECTION 9: Phase Renderers ────────────────────────────────────────────────

def render_phase_0():
    st.markdown(
        """
        <div class="app-hero">
          <div class="hero-eyebrow">2026 NCAA Tournament &nbsp;·&nbsp; Family Bracket Challenge</div>
          <div class="hero-title">March Madness 2026</div>
          <div class="hero-sub">
            Fill out all 63 games round by round, follow your picks on a live
            visual bracket, and export a shareable PDF when you're done.
          </div>
        </div>
        <div class="section-head">Enter Your Name to Begin</div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([2, 1])
    with col1:
        name = st.text_input(
            "Your name",
            value=st.session_state.get("user_name", ""),
            placeholder="e.g. Jane Smith",
            label_visibility="collapsed",
        )
    with col2:
        if st.button("Start Bracket", type="primary"):
            if name.strip():
                st.session_state["user_name"] = name.strip()
                st.session_state["current_phase"] = 1
                st.rerun()
            else:
                st.warning("Please enter your name to begin.")


def render_phase_1():
    st.markdown(
        """
        <div class="phase-eyebrow">Play-In Games</div>
        <div class="phase-title">First Four</div>
        <div class="phase-sub">Pick the winner of each play-in game. Winners advance to the Round of 64.</div>
        """,
        unsafe_allow_html=True,
    )

    for ff in FIRST_FOUR:
        with st.expander(f"**{ff['label']}**", expanded=True):
            opts = [ff["team_a"], ff["team_b"]]
            choice = st.radio(
                f"{ff['team_a']} vs. {ff['team_b']}",
                options=opts,
                index=None,
                key=f"w_{ff['id']}",
                horizontal=True,
                label_visibility="collapsed",
            )
            if choice:
                st.session_state["first_four_picks"][ff["id"]] = choice

    picks_done = len(st.session_state["first_four_picks"])
    st.markdown("---")
    if picks_done == 4:
        st.success("All First Four picks complete! Ready to continue.")
        if st.button("Continue to Round of 64", type="primary"):
            st.session_state["current_phase"] = 2
            st.rerun()
    else:
        st.info(f"{4 - picks_done} pick(s) remaining in First Four.")


def _render_round_picks(region_key, region_name, matchups, picks_key, show_seeds=False):
    """Generic round picker for one region. Returns True if all games in this region are picked."""
    with st.expander(f"**{region_name} Region**", expanded=True):
        for m in matchups:
            game_id = m["game_id"]
            team_a = m.get("team_a")
            team_b = m.get("team_b")

            if not team_a or not team_b:
                st.markdown(f"*Game pending: {team_a or '—'} vs. {team_b or '—'}*")
                continue

            if show_seeds:
                label_a = f"({m['seed_a']}) {team_a}"
                label_b = f"({m['seed_b']}) {team_b}"
            else:
                label_a = team_a
                label_b = team_b

            opts = [label_a, label_b]
            current = st.session_state[picks_key].get(game_id)
            if current == team_a:
                default_idx = 0
            elif current == team_b:
                default_idx = 1
            else:
                default_idx = None

            choice = st.radio(
                f"{label_a} vs. {label_b}",
                options=opts,
                index=default_idx,
                key=f"w_{game_id}",
                horizontal=True,
                label_visibility="visible",
            )
            if choice:
                # Extract raw team name (strip seed prefix if present)
                raw = choice.split(") ", 1)[-1] if ") " in choice else choice
                st.session_state[picks_key][game_id] = raw
            st.markdown('<hr class="game-divider">', unsafe_allow_html=True)


def render_phase_2():
    st.markdown(
        '<div class="phase-eyebrow">Round 1 of 6</div>'
        '<div class="phase-title">Round of 64</div>',
        unsafe_allow_html=True,
    )
    resolved = resolve_tbd_teams()

    col_left, col_right = st.columns(2)
    with col_left:
        for rk in ["east", "midwest"]:
            _render_round_picks(rk, REGIONS[rk]["name"],
                                resolved[rk]["matchups"], "picks_r64", show_seeds=True)
    with col_right:
        for rk in ["west", "south"]:
            _render_round_picks(rk, REGIONS[rk]["name"],
                                resolved[rk]["matchups"], "picks_r64", show_seeds=True)

    done = len(st.session_state["picks_r64"])
    st.markdown("---")
    if done == 32:
        st.success("All 32 Round of 64 games picked!")
        if st.button("Continue to Round of 32", type="primary"):
            st.session_state["current_phase"] = 3
            st.rerun()
    else:
        st.info(f"{32 - done} game(s) remaining in Round of 64.")

    st.markdown("---")
    st.markdown("### Live Bracket Preview")
    components.html(build_bracket_html(), height=1250, scrolling=True)


def render_phase_3():
    st.markdown(
        '<div class="phase-eyebrow">Round 2 of 6</div>'
        '<div class="phase-title">Round of 32</div>',
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns(2)
    with col_left:
        for rk in ["east", "midwest"]:
            _render_round_picks(rk, REGIONS[rk]["name"],
                                get_r32_matchups(rk), "picks_r32")
    with col_right:
        for rk in ["west", "south"]:
            _render_round_picks(rk, REGIONS[rk]["name"],
                                get_r32_matchups(rk), "picks_r32")

    done = len(st.session_state["picks_r32"])
    st.markdown("---")
    if done == 16:
        st.success("All 16 Round of 32 games picked!")
        if st.button("Continue to Sweet 16", type="primary"):
            st.session_state["current_phase"] = 4
            st.rerun()
    else:
        st.info(f"{16 - done} game(s) remaining in Round of 32.")

    st.markdown("---")
    st.markdown("### Live Bracket Preview")
    components.html(build_bracket_html(), height=1250, scrolling=True)


def render_phase_4():
    st.markdown(
        '<div class="phase-eyebrow">Round 3 of 6</div>'
        '<div class="phase-title">Sweet 16</div>',
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns(2)
    with col_left:
        for rk in ["east", "midwest"]:
            _render_round_picks(rk, REGIONS[rk]["name"],
                                get_s16_matchups(rk), "picks_s16")
    with col_right:
        for rk in ["west", "south"]:
            _render_round_picks(rk, REGIONS[rk]["name"],
                                get_s16_matchups(rk), "picks_s16")

    done = len(st.session_state["picks_s16"])
    st.markdown("---")
    if done == 8:
        st.success("All 8 Sweet 16 games picked!")
        if st.button("Continue to Elite Eight", type="primary"):
            st.session_state["current_phase"] = 5
            st.rerun()
    else:
        st.info(f"{8 - done} game(s) remaining in Sweet 16.")

    st.markdown("---")
    st.markdown("### Live Bracket Preview")
    components.html(build_bracket_html(), height=1250, scrolling=True)


def render_phase_5():
    st.markdown(
        '<div class="phase-eyebrow">Round 4 of 6</div>'
        '<div class="phase-title">Elite Eight</div>'
        '<div class="phase-sub">One game per region — the last stop before the Final Four.</div>',
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns(2)
    with col_left:
        for rk in ["east", "midwest"]:
            m = get_e8_matchup(rk)
            _render_round_picks(rk, REGIONS[rk]["name"], [m], "picks_e8")
    with col_right:
        for rk in ["west", "south"]:
            m = get_e8_matchup(rk)
            _render_round_picks(rk, REGIONS[rk]["name"], [m], "picks_e8")

    done = len(st.session_state["picks_e8"])
    st.markdown("---")
    if done == 4:
        st.success("All 4 Elite Eight games picked!")
        if st.button("Continue to Final Four", type="primary"):
            st.session_state["current_phase"] = 6
            st.rerun()
    else:
        st.info(f"{4 - done} game(s) remaining in Elite Eight.")

    st.markdown("---")
    st.markdown("### Live Bracket Preview")
    components.html(build_bracket_html(), height=1250, scrolling=True)


def render_phase_6():
    st.markdown(
        '<div class="phase-eyebrow">Round 5 of 6</div>'
        '<div class="phase-title">Final Four</div>'
        '<div class="phase-sub">Pick the two finalists competing for the national championship.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    ff_matchups = get_ff_matchups()
    col_left, col_right = st.columns(2)
    cols = [col_left, col_right]

    for idx, m in enumerate(ff_matchups):
        with cols[idx]:
            st.markdown(f"**{m['label']}**")
            team_a = m["team_a"]
            team_b = m["team_b"]
            if not team_a or not team_b:
                st.warning("Upstream picks missing — complete earlier rounds first.")
                continue

            current = st.session_state["picks_ff"].get(m["game_id"])
            default_idx = 0 if current == team_a else (1 if current == team_b else None)
            choice = st.radio(
                m["label"],
                options=[team_a, team_b],
                index=default_idx,
                key=f"w_{m['game_id']}",
                horizontal=True,
                label_visibility="collapsed",
            )
            if choice:
                st.session_state["picks_ff"][m["game_id"]] = choice

    done = len(st.session_state["picks_ff"])
    st.markdown("---")
    if done == 2:
        st.success("Final Four picks complete!")
        if st.button("Continue to Championship", type="primary"):
            st.session_state["current_phase"] = 7
            st.rerun()
    else:
        st.info(f"{2 - done} game(s) remaining in Final Four.")

    st.markdown("---")
    st.markdown("### Live Bracket Preview")
    components.html(build_bracket_html(), height=1250, scrolling=True)


def render_phase_7():
    st.markdown(
        '<div class="phase-eyebrow">Round 6 of 6</div>'
        '<div class="phase-title">National Championship</div>'
        '<div class="phase-sub">Pick your 2026 NCAA Men\'s Basketball National Champion.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    m = get_championship_matchup()
    team_a = m["team_a"]
    team_b = m["team_b"]

    if not team_a or not team_b:
        st.warning("Final Four picks are required before choosing a champion.")
        return

    current = st.session_state.get("picks_championship")
    default_idx = 0 if current == team_a else (1 if current == team_b else None)

    col1, col2 = st.columns([2, 1])
    with col1:
        choice = st.radio(
            "Pick the 2026 National Champion",
            options=[team_a, team_b],
            index=default_idx,
            key="w_championship",
            horizontal=False,
            label_visibility="visible",
        )
    if choice:
        st.session_state["picks_championship"] = choice

    st.markdown("---")
    if st.session_state.get("picks_championship"):
        st.success(f"Your champion: **{st.session_state['picks_championship']}**")
        if st.button("Complete My Bracket", type="primary"):
            st.session_state["current_phase"] = 8
            st.rerun()
    else:
        st.info("Select your champion to complete the bracket.")


def render_phase_8():
    champion = st.session_state.get("picks_championship", "Unknown")
    user = st.session_state.get("user_name", "")
    st.balloons()

    st.markdown(
        '<div class="phase-eyebrow">Bracket Complete</div>'
        '<div class="phase-title">Your 2026 Bracket</div>',
        unsafe_allow_html=True,
    )

    # Champion card — uses CSS variables, fully dark-mode aware
    st.markdown(
        f"""
        <div class="champion-card">
          <div class="champion-label">2026 NCAA National Champion</div>
          <div class="champion-name">{champion}</div>
          <div class="champion-sub">Bracket by {user}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-head">Full Bracket</div>', unsafe_allow_html=True)
    components.html(build_bracket_html(), height=1300, scrolling=True)

    st.markdown('<div class="section-head" style="margin-top:1.5rem;">Export Your Bracket</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Generate PDF", type="primary"):
            with st.spinner("Generating PDF..."):
                pdf_bytes = generate_pdf(st.session_state["user_name"])
                safe_name = st.session_state["user_name"].replace(" ", "_")
                filename = f"{safe_name}_bracket_2026.pdf"
                st.download_button(
                    label="Download PDF Bracket",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    type="primary",
                )
    with col2:
        st.info("PDF includes all picks organized by region, Final Four, and your champion.")

# ── SECTION 10: Sidebar ───────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">McCall Family · 2026 Tournament</div>
            <div class="sidebar-title">March Madness<br>Bracket</div>
            """,
            unsafe_allow_html=True,
        )

        user = st.session_state.get("user_name") or "—"
        st.markdown(
            f'<div class="sidebar-row"><strong>Picker</strong><br>{user}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        total_picks = count_total_picks()
        pct = total_picks / 63

        # Progress chip
        st.markdown(
            f"""
            <div class="stat-chip">
              <div class="chip-label">Bracket Progress</div>
              <div class="chip-value">{total_picks}<span style="font-size:1rem;font-weight:400"> / 63</span></div>
              <div class="chip-sub">games picked</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(pct)

        champion = st.session_state.get("picks_championship")
        if champion:
            st.markdown(
                f"""
                <div class="sidebar-champ">
                  <div class="sidebar-champ-label">Champion Pick</div>
                  <div class="sidebar-champ-name">{champion}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        phase = st.session_state.get("current_phase", 0)
        phase_names = {
            0: "Name Entry", 1: "First Four", 2: "Round of 64",
            3: "Round of 32", 4: "Sweet 16",  5: "Elite Eight",
            6: "Final Four", 7: "Championship", 8: "Complete",
        }
        st.markdown(
            f'<div class="sidebar-row"><strong>Current Round</strong><br>{phase_names.get(phase, "—")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("")

        if st.button("Reset Bracket", type="secondary"):
            reset_session_state()

        st.markdown(
            '<div class="sidebar-footer">2026 Selection Sunday · March 15, 2026</div>',
            unsafe_allow_html=True,
        )

# ── SECTION 11: Main Entry Point ─────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="2026 March Madness Bracket",
        page_icon="🏀",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    init_session_state()
    render_sidebar()

    phase = st.session_state.get("current_phase", 0)
    renderers = {
        0: render_phase_0,
        1: render_phase_1,
        2: render_phase_2,
        3: render_phase_3,
        4: render_phase_4,
        5: render_phase_5,
        6: render_phase_6,
        7: render_phase_7,
        8: render_phase_8,
    }
    renderers.get(phase, render_phase_0)()


main()
