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
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: 'Clear Sans', 'Helvetica Neue', Arial, sans-serif;
        background: #f7f7f7;
        padding: 16px;
        color: #000;
    }
    .bracket-title {
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 16px;
        color: #000;
    }
    .region-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 6px;
        color: #555;
    }
    .ts {
        height: 24px;
        width: 148px;
        border: 1.5px solid #d3d6da;
        display: flex;
        align-items: center;
        padding: 0 5px;
        font-size: 10.5px;
        font-weight: 500;
        background: #fff;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        border-radius: 2px;
        color: #000;
    }
    .ts.picked {
        background: #6aaa64;
        border-color: #6aaa64;
        color: #fff;
        font-weight: 700;
    }
    .ts.eliminated {
        background: #787c7e;
        border-color: #787c7e;
        color: #fff;
        text-decoration: line-through;
        opacity: 0.8;
    }
    .ts.unpicked {
        background: #fff;
        color: #000;
    }
    .ts .seed {
        font-size: 9px;
        font-weight: 700;
        min-width: 16px;
        color: inherit;
        opacity: 0.75;
    }
    .ts.picked .seed, .ts.eliminated .seed {
        color: #fff;
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
        color: #555;
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
        color: #888;
        text-align: center;
        margin-bottom: 4px;
    }
    .ff-vs {
        font-size: 9px;
        text-align: center;
        color: #888;
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
        color: #555;
        margin-bottom: 8px;
    }
    .champ-name {
        font-size: 22px;
        font-weight: 900;
        color: #6aaa64;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .champ-pending {
        font-size: 18px;
        font-weight: 700;
        color: #d3d6da;
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
        border-top: 2px solid #d3d6da;
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
            f'<line x1="{col_x[0]+COL_W}" y1="{ca:.1f}" x2="{vx}" y2="{ca:.1f}" stroke="#d3d6da" stroke-width="1.5"/>',
            f'<line x1="{col_x[0]+COL_W}" y1="{cb:.1f}" x2="{vx}" y2="{cb:.1f}" stroke="#d3d6da" stroke-width="1.5"/>',
            f'<line x1="{vx}" y1="{ca:.1f}" x2="{vx}" y2="{cb:.1f}" stroke="#d3d6da" stroke-width="1.5"/>',
            f'<line x1="{vx}" y1="{center:.1f}" x2="{col_x[1]}" y2="{center:.1f}" stroke="#d3d6da" stroke-width="1.5"/>',
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
            f'<line x1="{col_x[1]+COL_W}" y1="{ca:.1f}" x2="{vx}" y2="{ca:.1f}" stroke="#d3d6da" stroke-width="1.5"/>',
            f'<line x1="{col_x[1]+COL_W}" y1="{cb:.1f}" x2="{vx}" y2="{cb:.1f}" stroke="#d3d6da" stroke-width="1.5"/>',
            f'<line x1="{vx}" y1="{ca:.1f}" x2="{vx}" y2="{cb:.1f}" stroke="#d3d6da" stroke-width="1.5"/>',
            f'<line x1="{vx}" y1="{center:.1f}" x2="{col_x[2]}" y2="{center:.1f}" stroke="#d3d6da" stroke-width="1.5"/>',
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
        f'<line x1="{col_x[2]+COL_W}" y1="{ca:.1f}" x2="{vx}" y2="{ca:.1f}" stroke="#d3d6da" stroke-width="1.5"/>',
        f'<line x1="{col_x[2]+COL_W}" y1="{cb:.1f}" x2="{vx}" y2="{cb:.1f}" stroke="#d3d6da" stroke-width="1.5"/>',
        f'<line x1="{vx}" y1="{ca:.1f}" x2="{vx}" y2="{cb:.1f}" stroke="#d3d6da" stroke-width="1.5"/>',
        f'<line x1="{vx}" y1="{center:.1f}" x2="{col_x[3]}" y2="{center:.1f}" stroke="#d3d6da" stroke-width="1.5"/>',
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

# ── SECTION 8: NYT-Style CSS Injection ───────────────────────────────────────

def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&display=swap');

        /* ── Force light-mode palette on every Streamlit container ───────────
           These overrides beat Streamlit's CSS variables in both light AND
           dark OS/browser modes, so the app always looks intentional.       */

        /* Root colour tokens – overwrite Streamlit's dark-mode variables */
        :root, [data-theme="dark"], [data-theme="light"] {
            --background-color:           #ffffff !important;
            --secondary-background-color: #f7f7f7 !important;
            --text-color:                 #000000 !important;
            --font:                       'Inter', 'Helvetica Neue', Arial, sans-serif !important;
        }

        /* Main app shell */
        .stApp,
        .stApp > header,
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"],
        [data-testid="block-container"],
        .main .block-container {
            background-color: #ffffff !important;
            color: #000000 !important;
            font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif !important;
        }

        /* Every generic element inside the app */
        .stApp p,
        .stApp span,
        .stApp div,
        .stApp li,
        .stApp label,
        .stApp small,
        .stApp strong,
        .stApp em,
        .element-container,
        .stMarkdown,
        .stMarkdown p,
        .stMarkdown li {
            color: #000000 !important;
        }

        /* Headings */
        .stApp h1 {
            font-weight: 900 !important;
            font-size: 2rem !important;
            letter-spacing: -1px !important;
            color: #000000 !important;
        }
        .stApp h2,
        .stApp h3,
        .stApp h4 {
            font-weight: 800 !important;
            color: #000000 !important;
            letter-spacing: -0.5px !important;
        }

        /* Horizontal rule */
        hr {
            border-color: #d3d6da !important;
        }

        /* ── Sidebar ──────────────────────────────────────────────────────── */
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            background-color: #f7f7f7 !important;
            color: #000000 !important;
            border-right: 2px solid #d3d6da !important;
        }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] small {
            color: #000000 !important;
        }

        /* ── Expanders ────────────────────────────────────────────────────── */
        div[data-testid="stExpander"] {
            border: 1.5px solid #d3d6da !important;
            border-radius: 4px !important;
            background-color: #ffffff !important;
            margin-bottom: 8px !important;
        }
        /* Header row (collapsed/expanded toggle) */
        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] > details > summary,
        div[data-testid="stExpander"] [data-testid="stExpanderToggleIcon"],
        div[data-testid="stExpander"] > div:first-child {
            background-color: #f7f7f7 !important;
            color: #000000 !important;
        }
        div[data-testid="stExpander"] summary span,
        div[data-testid="stExpander"] summary p,
        div[data-testid="stExpander"] summary div {
            color: #000000 !important;
        }
        /* Body of open expander */
        div[data-testid="stExpander"] [data-testid="stExpanderDetails"],
        div[data-testid="stExpander"] details > div {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* ── Radio buttons ────────────────────────────────────────────────── */
        div[data-testid="stRadio"] {
            background-color: transparent !important;
        }
        div[data-testid="stRadio"] label,
        div[data-testid="stRadio"] label span,
        div[data-testid="stRadio"] label p,
        div[data-testid="stRadio"] > label {
            color: #000000 !important;
            font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif !important;
            font-size: 14px !important;
        }
        /* The radio circle itself – keep it visible */
        div[data-testid="stRadio"] input[type="radio"] + div {
            border-color: #000000 !important;
        }
        div[data-testid="stRadio"] input[type="radio"]:checked + div {
            background-color: #000000 !important;
            border-color:     #000000 !important;
        }

        /* ── Text inputs ──────────────────────────────────────────────────── */
        .stTextInput > div > div,
        .stTextInput > div > div > input {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #000000 !important;
            border-radius: 4px !important;
            font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif !important;
            font-size: 15px !important;
            padding: 8px 12px !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #6aaa64 !important;
            box-shadow: 0 0 0 2px rgba(106, 170, 100, 0.25) !important;
        }
        .stTextInput label,
        .stTextInput label span {
            color: #000000 !important;
        }

        /* ── Buttons ──────────────────────────────────────────────────────── */
        .stButton > button {
            background-color: #000000 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 4px !important;
            font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            font-size: 13px !important;
            padding: 8px 20px !important;
        }
        .stButton > button:hover {
            background-color: #222222 !important;
        }
        /* Secondary / Reset button */
        .stButton > button[kind="secondary"],
        .stButton > button[data-testid="baseButton-secondary"] {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #000000 !important;
        }
        .stButton > button[kind="secondary"]:hover,
        .stButton > button[data-testid="baseButton-secondary"]:hover {
            background-color: #f0f0f0 !important;
        }

        /* ── Download button ──────────────────────────────────────────────── */
        .stDownloadButton > button {
            background-color: #000000 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 4px !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            font-size: 13px !important;
        }

        /* ── Progress bar ─────────────────────────────────────────────────── */
        [data-testid="stProgressBar"] > div,
        .stProgress > div > div > div > div {
            background-color: #6aaa64 !important;
        }
        [data-testid="stProgressBar"],
        .stProgress > div > div {
            background-color: #e0e0e0 !important;
        }

        /* ── Alert / info / success / warning boxes ───────────────────────── */
        div[data-testid="stAlert"],
        .stAlert {
            border-radius: 4px !important;
            background-color: #f7f7f7 !important;
            color: #000000 !important;
        }
        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] span {
            color: #000000 !important;
        }
        /* Keep Streamlit's coloured left-border for success/info/warning */
        div[data-testid="stAlert"][data-baseweb="notification"] {
            background-color: #f7f7f7 !important;
        }

        /* ── Spinner / status widget ──────────────────────────────────────── */
        [data-testid="stStatusWidget"] span,
        [data-testid="stSpinner"] span {
            color: #000000 !important;
        }

        /* ── Info callout text (st.info) ──────────────────────────────────── */
        .stInfo, .stInfo p, .stInfo span { color: #000000 !important; }
        .stSuccess, .stSuccess p, .stSuccess span { color: #000000 !important; }
        .stWarning, .stWarning p, .stWarning span { color: #000000 !important; }

        /* ── Custom component helpers ─────────────────────────────────────── */
        .nyt-badge {
            display: inline-block;
            background: #000000;
            color: #ffffff !important;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
            padding: 3px 8px;
            border-radius: 2px;
            margin-bottom: 8px;
        }
        .round-header {
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #555555 !important;
            padding: 8px 0 4px;
            border-bottom: 2px solid #000000;
            margin-bottom: 12px;
        }
        .game-divider {
            border: none !important;
            border-top: 1px solid #e0e0e0 !important;
            margin: 6px 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ── SECTION 9: Phase Renderers ────────────────────────────────────────────────

def render_phase_0():
    st.markdown('<div class="nyt-badge">McCall Family Bracket Challenge</div>', unsafe_allow_html=True)
    st.title("2026 March Madness Bracket")
    st.markdown("---")
    st.markdown("### Enter Your Name to Begin")
    st.markdown("Your name will appear on your bracket and exported PDF.")
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
    st.markdown('<div class="nyt-badge">Play-In Games</div>', unsafe_allow_html=True)
    st.title("First Four")
    st.markdown("Pick the winner of each play-in game. These teams advance to the Round of 64.")
    st.markdown("---")

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
    st.markdown('<div class="nyt-badge">Round 1</div>', unsafe_allow_html=True)
    st.title("Round of 64")
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
    st.markdown('<div class="nyt-badge">Round 2</div>', unsafe_allow_html=True)
    st.title("Round of 32")

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
    st.markdown('<div class="nyt-badge">Sweet 16</div>', unsafe_allow_html=True)
    st.title("Sweet 16")

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
    st.markdown('<div class="nyt-badge">Elite Eight</div>', unsafe_allow_html=True)
    st.title("Elite Eight")
    st.markdown("The final four games before the Final Four — one per region.")

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
    st.markdown('<div class="nyt-badge">Final Four</div>', unsafe_allow_html=True)
    st.title("Final Four")
    st.markdown("Pick the two finalists who will compete for the national championship.")
    st.markdown("---")

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
    st.markdown('<div class="nyt-badge">Championship</div>', unsafe_allow_html=True)
    st.title("National Championship")
    st.markdown("Pick your 2026 NCAA Men's Basketball National Champion.")
    st.markdown("---")

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
    st.balloons()

    st.markdown('<div class="nyt-badge">Bracket Complete</div>', unsafe_allow_html=True)
    st.title(f"Your 2026 Champion: {champion}")

    st.markdown(
        f"""
        <div style="background:#000;color:#6aaa64;padding:24px;border-radius:6px;
        text-align:center;margin-bottom:24px;">
          <div style="font-size:13px;font-weight:800;letter-spacing:3px;
          text-transform:uppercase;color:#fff;margin-bottom:8px;">
            2026 NCAA National Champion
          </div>
          <div style="font-size:32px;font-weight:900;letter-spacing:1px;">
            {champion.upper()}
          </div>
          <div style="font-size:12px;color:#6aaa64;margin-top:8px;">
            Bracket by {st.session_state.get('user_name', '')}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Full Bracket Summary")
    components.html(build_bracket_html(), height=1300, scrolling=True)

    st.markdown("---")
    st.markdown("### Export Your Bracket")
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
            <div style="font-size:11px;font-weight:800;letter-spacing:2px;
            text-transform:uppercase;color:#555;margin-bottom:4px;">
            McCall Family Bracket Challenge
            </div>
            <div style="font-size:20px;font-weight:900;color:#000;line-height:1.1;
            margin-bottom:16px;">
            2026 March Madness
            </div>
            """,
            unsafe_allow_html=True,
        )

        user = st.session_state.get("user_name") or "Not set"
        st.markdown(f"**Picker:** {user}")
        st.markdown("---")

        total_picks = count_total_picks()
        pct = total_picks / 63
        st.markdown(f"**Progress:** {total_picks} / 63 games")
        st.progress(pct)

        champion = st.session_state.get("picks_championship")
        if champion:
            st.markdown("---")
            st.markdown(
                f'<div style="background:#6aaa64;color:#fff;padding:8px;'
                f'border-radius:4px;text-align:center;">'
                f'<div style="font-size:10px;font-weight:700;letter-spacing:1px;'
                f'text-transform:uppercase;">Champion Pick</div>'
                f'<div style="font-size:15px;font-weight:900;">{champion}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        phase = st.session_state.get("current_phase", 0)
        phase_names = {
            0: "Name Entry",
            1: "First Four",
            2: "Round of 64",
            3: "Round of 32",
            4: "Sweet 16",
            5: "Elite Eight",
            6: "Final Four",
            7: "Championship",
            8: "Complete",
        }
        st.markdown(f"**Current Round:** {phase_names.get(phase, '—')}")
        st.markdown("---")

        if st.button("Reset Bracket", type="secondary"):
            reset_session_state()

        st.markdown("---")
        st.markdown(
            '<div style="font-size:10px;color:#888;">2026 Selection Sunday: March 15, 2026</div>',
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
