"""Shared Streamlit UI pieces: styling, KPI cards, banners, formatting."""
from __future__ import annotations

import html

import streamlit as st

from . import hover, state

GREEN, DEEP, MINT, INK, INK2, BORDER = "#1E7B4F", "#0f4d33", "#e3f1e8", "#0b0b0b", "#52514e", "#e1e0d9"

CSS = f"""
<style>
:root {{ --green:{GREEN}; --deep:{DEEP}; --mint:{MINT}; --ink:{INK}; --ink2:{INK2}; --border:{BORDER}; }}
.block-container {{ padding-top: 2.2rem; padding-bottom: 4rem; max-width: 1280px; }}
h1, h2, h3 {{ letter-spacing: -0.01em; }}
[data-testid="stSidebar"] {{ border-right: 1px solid var(--border); }}
[data-testid="stSidebarNav"] a {{ border-radius: 10px; }}
.brand {{ display:flex; align-items:center; gap:.6rem; padding:.2rem 0 .8rem 0; }}
.brand .logo {{ width:34px; height:34px; border-radius:10px; background:linear-gradient(135deg,var(--green),#2fa36b);
  display:flex; align-items:center; justify-content:center; color:white; font-weight:700; }}
.brand .name {{ font-weight:700; font-size:1.05rem; line-height:1.1; }}
.brand .sub {{ font-size:.72rem; color:var(--ink2); }}
.hero {{ background: linear-gradient(120deg, var(--deep) 0%, var(--green) 55%, #38b27a 100%); color:white;
  padding: 2.2rem 2.4rem; border-radius: 20px; margin-bottom: 1.4rem; box-shadow: 0 10px 30px rgba(15,77,51,.18); }}
.hero .kicker {{ text-transform:uppercase; letter-spacing:.14em; font-size:.72rem; opacity:.85; margin-bottom:.5rem; }}
.hero h1 {{ color:white; font-size:2.3rem; margin:0 0 .6rem 0; line-height:1.15; }}
.hero p {{ font-size:1.05rem; color:rgba(255,255,255,.93); margin:0; max-width:780px; }}
.hero .term {{ border-bottom-color:rgba(255,255,255,.9); }}
.hero .term:hover, .hero .term:focus-visible {{ background:rgba(255,255,255,.22); }}
.pagehead {{ margin-bottom:1.1rem; }}
.pagehead .step {{ display:inline-block; background:var(--mint); color:var(--deep); border-radius:999px; padding:.15rem .7rem;
  font-size:.74rem; font-weight:700; letter-spacing:.04em; margin-bottom:.4rem; }}
.pagehead h2 {{ margin:0; font-size:1.7rem; }}
.pagehead p {{ margin:.25rem 0 0 0; color:var(--ink2); }}
.card {{ background:white; border:1px solid var(--border); border-radius:16px; padding:1.1rem 1.3rem; height:100%;
  box-shadow: 0 1px 2px rgba(0,0,0,.03); }}
.card h4 {{ margin:0 0 .35rem 0; font-size:1rem; }}
.card p {{ margin:0; color:var(--ink2); font-size:.92rem; line-height:1.45; }}
.card .big {{ font-size:1.7rem; font-weight:700; color:var(--deep); margin-bottom:.15rem; }}
.kpi {{ background:white; border:1px solid var(--border); border-radius:16px; padding:.95rem 1.15rem;
  box-shadow: 0 1px 2px rgba(0,0,0,.03); height:100%; }}
.kpi .l {{ font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; color:var(--ink2); font-weight:600; }}
.kpi .v {{ font-size:1.65rem; font-weight:700; margin-top:.15rem; line-height:1.15; }}
.kpi .s {{ font-size:.82rem; color:var(--ink2); margin-top:.2rem; }}
.kpi .q {{ cursor:help; color:var(--green); font-size:.8rem; }}
.verdict {{ background:linear-gradient(180deg,#ffffff,var(--mint)); border:1px solid #bfdcca; border-radius:18px; padding:1.1rem 1.4rem;
  margin:.2rem 0 1rem 0; }}
.verdict .t {{ font-size:.72rem; text-transform:uppercase; letter-spacing:.1em; color:var(--deep); font-weight:700; }}
.verdict .h {{ font-size:1.35rem; font-weight:700; color:var(--ink); line-height:1.3; margin:.25rem 0; }}
.verdict .s {{ color:var(--ink2); font-size:.95rem; }}
.verdict.bad {{ background:#fff6f4; border-color:#f1c6bd; }}
.kpi.good .v {{ color:#006300; }} .kpi.bad .v {{ color:#b03030; }} .kpi.brand .v {{ color:var(--deep); }}
.kpi.brand {{ display:block; padding:.95rem 1.15rem; background:linear-gradient(180deg,#ffffff,var(--mint)); border-color:#bfdcca; }}
.chip {{ display:inline-block; padding:.22rem .65rem; margin:.15rem .25rem .15rem 0; border-radius:999px; font-size:.82rem;
  background:var(--mint); color:var(--deep); border:1px solid #bfdcca; }}
.chip.alt {{ background:#fdeee8; color:#8a3a18; border-color:#f4cdbd; }}
.callout {{ border-left:4px solid var(--green); background:white; border-radius:10px; padding:.8rem 1.1rem; margin:.6rem 0;
  border:1px solid var(--border); border-left-width:4px; }}
.callout.warn {{ border-left-color:#eda100; }} .callout.bad {{ border-left-color:#d03b3b; }} .callout.good {{ border-left-color:#0ca30c; }}
.callout b {{ color:var(--ink); }}
.sidefoot {{ background:white; border:1px solid var(--border); border-radius:14px; padding:.7rem .9rem; font-size:.84rem; margin-top:.6rem; }}
.sidefoot .t {{ font-size:.68rem; text-transform:uppercase; letter-spacing:.08em; color:var(--ink2); font-weight:600; }}
.sidefoot .ok {{ color:#006300; font-weight:700; }} .sidefoot .no {{ color:#b03030; font-weight:700; }}
.stTabs [data-baseweb="tab-list"] {{ gap:.3rem; }}
.stTabs [data-baseweb="tab"] {{ border-radius:10px 10px 0 0; padding:.45rem .9rem; }}
div[data-testid="stDataFrame"] {{ border:1px solid var(--border); border-radius:12px; }}
.stButton > button[kind="primary"] {{ border-radius:12px; font-weight:600; padding:.55rem 1.3rem; }}
.stButton > button {{ border-radius:12px; }}
.term {{ position:relative; border-bottom:1px dotted var(--green); cursor:help; white-space:normal; }}
.term:hover {{ background:var(--mint); border-radius:3px; }}
.term:focus-visible {{ outline:2px solid var(--green); outline-offset:2px; border-radius:3px; background:var(--mint); }}
.term .pop {{ display:none; position:absolute; z-index:99999; left:0; top:1.6em; width:310px; max-width:80vw; padding:.7rem .85rem;
  background:white; color:var(--ink); border:1px solid #bfdcca; border-radius:12px; box-shadow:0 10px 28px rgba(0,0,0,.18);
  font-size:.82rem; font-weight:400; line-height:1.4; letter-spacing:0; text-transform:none; text-align:left; }}
.term .pop b {{ display:block; color:var(--deep); font-size:.9rem; margin-bottom:.25rem; }}
.term .pop i {{ display:block; font-style:normal; font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; color:var(--deep);
  font-weight:700; margin-top:.4rem; }}
.term:hover .pop, .term:focus .pop {{ display:block; }}
.term.r .pop {{ left:auto; right:0; }}
[data-testid="stElementContainer"]:has(.term:hover), [data-testid="stElementContainer"]:has(.term:focus) {{ position:relative; z-index:99999; }}
[data-testid="stColumn"]:has(.term:hover) {{ position:relative; z-index:99999; }}
.kpi .l .term {{ border-bottom:1px dotted var(--green); }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ color:var(--ink2); }}
@media (prefers-reduced-motion: reduce) {{ * {{ transition:none !important; animation:none !important; }} }}
footer {{ visibility:hidden; }}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def pct(x: float | None) -> str:
    return "–" if x is None else f"{x*100:.1f}%"


def inr(x: float | None, digits: int = 2) -> str:
    """Rupees in Indian units: Cr / L / plain."""
    if x is None:
        return "–"
    s, a = ("−" if x < 0 else ""), abs(float(x))
    if a >= 1e7:
        return f"{s}₹{a/1e7:.{digits}f} Cr"
    if a >= 1e5:
        return f"{s}₹{a/1e5:.1f} L"
    return f"{s}₹{a:,.0f}"


def hero(kicker: str, title: str, text: str) -> None:
    st.markdown(f'<div class="hero"><div class="kicker">{html.escape(kicker)}</div><h1>{html.escape(title)}</h1>'
                f'<p>{hover.rich(text)}</p></div>', unsafe_allow_html=True)


# Plain-language names on screen; the textbook term (CE 725) lives in the tooltip so the course vocabulary stays visible.
LABELS = {
    "lcc": ("Life-cycle cost (PW)", "Present worth at the MARR of capex + O&M + replacements − salvage − energy and water savings, "
            "over the study period (Ch 5, planning-horizon method). Negative = pays for itself."),
    "eac": ("Cost per year (EUAC)", "Equivalent uniform annual cost = PW × (A/P, MARR, N): the life-cycle cost spread evenly over the years (Ch 6)."),
    "capex": ("Upfront cost", "Capital expenditure at year 0, incremental to the code-minimum option it replaces."),
    "bcr": ("Benefit-cost ratio", "BCR = PW of savings ÷ PW of costs. Above 1 = the measure is worth more than it costs at the MARR."),
    "ror": ("Rate of return", "IRR: the rate at which PW = 0 (Ch 7). When the cash flow changes sign more than once the IRR is not unique, "
            "so MIRR is shown instead, with finance and reinvestment rate = MARR (Ch 8). Compare with the MARR."),
    "inc": ("Return on the extra capex", "Incremental IRR (or MIRR) of the recommended mix over the cheapest-upfront mix. "
            "Ch 7 rule: if it is at least the MARR, the extra money is well spent."),
    "payback": ("Discounted payback", "Years until the cumulative present worth turns in your favour. Unlike simple payback it respects the time value of money."),
    "marr": ("MARR", "Minimum attractive rate of return: the discount rate every cash flow is brought back to year 0 with (nominal)."),
    "co2": ("CO₂ avoided", "Lifetime tonnes of CO₂ avoided = kWh saved × grid emission factor."),
}

PAGES = {
    "home": ("pages/0_home.py", "Home", ":material/home:"),
    "setup": ("pages/1_setup.py", "Set up the project", ":material/tune:"),
    "rec": ("pages/2_recommendation.py", "See the recommendation", ":material/workspace_premium:"),
    "trust": ("pages/3_trust.py", "Check the risk", ":material/verified:"),
    "report": ("pages/4_report.py", "Get the report", ":material/description:"),
}


def label(key: str) -> str:
    return LABELS[key][0]


HOVER_KEY = {"ror": "irr"}  # screen label key -> hover key when they differ


def tip(key: str) -> str:
    """Markdown tooltip for widgets and table columns (Streamlit help=)."""
    k = HOVER_KEY.get(key, key)
    return hover.tip(k) if k in hover.HOVER else LABELS[key][1]


def term(key: str, text: str | None = None) -> str:
    return hover.term(key, text)


def md(text: str) -> None:
    """Markdown with [[key|shown]] hover terms."""
    st.markdown(hover.expand(text), unsafe_allow_html=True)


def caption(text: str) -> None:
    st.caption(hover.expand(text), unsafe_allow_html=True)


def next_step(key: str, text: str = "") -> None:
    """A clear 'Next' button at the bottom of a page, so the demo flows without the sidebar."""
    path, title, icon = PAGES[key]
    st.write("")
    st.divider()
    l, r = st.columns([3, 1.2])
    l.caption(text)
    r.page_link(path, label=f"Next: {title} →", icon=icon, width="stretch")


def page_header(step: int | None, title: str, subtitle: str = "") -> None:
    chip = f'<span class="step">STEP {step} OF 4</span><br>' if step else ""
    st.markdown(f'<div class="pagehead">{chip}<h2>{html.escape(title)}</h2><p>{hover.rich(subtitle)}</p></div>', unsafe_allow_html=True)


def kpis(items: list[tuple], cols: int | None = None) -> None:
    """items: (label, value, sub, tone[, help]). help is "@key" (a hover term), a plain sentence, or empty; it opens as a popup."""
    n = cols or len(items)
    cs = st.columns(n)
    for idx, (c, it) in enumerate(zip(cs, items)):
        name, value, sub, tone, hlp = (list(it) + ["", "", ""])[:5]
        side = " r" if n > 1 and idx >= n / 2 else ""
        if hlp.startswith("@") and hlp[1:] in hover.HOVER:
            lab = f'<span class="term{side}" tabindex="0">{html.escape(name)} ⓘ{hover.popup_html(hlp[1:])}</span>'
        elif hlp:
            lab = f'<span class="term{side}" tabindex="0">{html.escape(name)} ⓘ<span class="pop">{html.escape(hlp)}</span></span>'
        else:
            lab = html.escape(name)
        c.markdown(f'<div class="kpi {tone}"><div class="l">{lab}</div><div class="v">{html.escape(str(value))}</div>'
                   f'<div class="s">{html.escape(str(sub))}</div></div>', unsafe_allow_html=True)


def card(title: str, text: str, big: str = "") -> str:
    b = f'<div class="big">{html.escape(big)}</div>' if big else ""
    return f'<div class="card">{b}<h4>{html.escape(title)}</h4><p>{hover.rich(text)}</p></div>'


def chips(items: list[str], alt: bool = False) -> None:
    cls = "chip alt" if alt else "chip"
    st.markdown("".join(f'<span class="{cls}">{html.escape(i)}</span>' for i in items) or "<i>none</i>", unsafe_allow_html=True)


def callout(text: str, kind: str = "") -> None:
    st.markdown(f'<div class="callout {kind}">{hover.expand(text)}</div>', unsafe_allow_html=True)


def verdict(kicker: str, headline: str, sub: str = "", bad: bool = False) -> None:
    """The one-sentence answer at the top of a page."""
    st.markdown(f'<div class="verdict{" bad" if bad else ""}"><div class="t">{html.escape(kicker)}</div><div class="h">{hover.expand(headline)}</div>'
                f'<div class="s">{hover.expand(sub)}</div></div>', unsafe_allow_html=True)


def unreachable(ds, df, target: str) -> None:
    """Friendly stop when the target cannot be met, with a one-click fix."""
    from . import optimizer

    callout(f"<b>{target} is not reachable.</b> {optimizer.infeasible_message(df, ds, target)}", "bad")
    top = state.highest_reachable(ds, df)
    if top:
        st.button(f"Switch target to {top}", type="primary", icon=":material/swap_vert:",
                  on_click=lambda: st.session_state.update(target=top))
    st.stop()


def require_ds():
    ds = state.get_ds()
    if ds is None:
        st.info("No project loaded yet. Open **Home** and click **Try the Pune demo**, or open a saved project file.")
        st.page_link("pages/0_home.py", label="Go to Home", icon=":material/home:")
        st.stop()
    return ds


def sidebar_brand() -> None:
    st.sidebar.markdown('<div class="brand"><div class="logo">G</div><div><div class="name">GreenLCC India</div>'
                        '<div class="sub">IGBC credit optimizer · CM 617</div></div></div>', unsafe_allow_html=True)


def sidebar_controls() -> None:
    """The one choice that drives every page lives in one place: the target IGBC level."""
    ds = state.get_ds()
    if ds is None:
        return
    levels = [lv.level for lv in sorted(ds.levels, key=lambda x: x.rank)]
    if st.session_state.get("target") not in levels:
        st.session_state["target"] = ds.project.target_level if ds.project.target_level in levels else levels[-1]
    with st.sidebar:
        st.selectbox("Target IGBC level", levels, key="target", help="Applies to every page and to the report.")


def sidebar_footer() -> None:
    ds = state.get_ds()
    if ds is None:
        return
    try:
        target, df, rec, _ = state.recommendation(ds)
    except Exception:
        return
    if rec is None:
        body = f'<span class="no">{target} not reachable</span>'
    else:
        body = (f'<span class="ok">{rec["level"]} · {rec["points"]:g} pts ✓</span><br>'
                f'Life-cycle cost {inr(rec["lcc"])}<br>Upfront {inr(rec["capex"])}')
    st.sidebar.markdown(f'<div class="sidefoot"><div class="t">{html.escape(ds.project.name)}</div>'
                        f'{body}</div>', unsafe_allow_html=True)
