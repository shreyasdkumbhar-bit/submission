import pandas as pd
import streamlit as st

from core import state, ui
from core.io import DEMO_INPUT

ui.hero("CM 617 · Topic 6 · Life Cycle Cost Analysis",
        "Reach your IGBC target at the lowest lifetime cost",
        "Most Indian projects pick green credits by cheapest upfront price. GreenLCC costs every measure over "
        "25 years of energy, maintenance, replacement and tariff risk, then finds the mix that earns the [[igbc|IGBC rating]] for the least money overall. "
        "Hover over any dotted term to see what it means and why we use it.")

ds = state.get_ds()
left, right = st.columns([1, 1.5], gap="large")
with left:
    st.subheader("Start here")
    if st.button("Try the Pune demo", type="primary", icon=":material/rocket_launch:", width="stretch"):
        errs = state.load_demo()
        if errs:
            st.error("Could not load the demo data:\n\n" + "\n".join(f"- {e}" for e in errs))
        else:
            st.rerun()
    up = st.file_uploader("…or open your input workbook (.xlsx)", type="xlsx",
                          help="The input workbook (Project, Measures, IGBC sheets). A results workbook from the Report page opens too.")
    if up is not None and st.session_state.get("_opened") != up.file_id:
        errs = state.open_workbook(up.getvalue())
        if errs:
            st.error("Could not open that file:\n\n" + "\n".join(f"- {e}" for e in errs))
        else:
            st.session_state["_opened"] = up.file_id
            st.rerun()
    if DEMO_INPUT.exists():
        st.download_button("Download the input workbook to fill in", DEMO_INPUT.read_bytes(), file_name="greenlcc_input.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", icon=":material/download:",
                           width="stretch", help="The demo's inputs with units, meanings and sources. Overwrite the values, then open it above.")
    st.caption("Demo prices and tariffs are **sourced estimates** for a Pune office; the IGBC point tables are **illustrative**.")

with right:
    if ds is None:
        st.subheader("How it works")
        ui.md("""
1. **Set up**: the building, tariffs, [[marr|MARR]] and a library of green measures, all from one Excel input workbook.
2. **Recommendation**: the cheapest-over-its-life way to reach Silver, Gold or Platinum, next to the [[cheapest|cheapest-upfront]] way.
3. **Can we trust it?**: [[break_even|break-even points]], [[tornado|sensitivity]] and [[mc|Monte Carlo]]: does the answer survive a higher MARR or slower tariff growth?
4. **Report**: one PDF for the owner, one Excel for the details, and the input workbook to reopen later.
""")
    else:
        target, df, rec, cheap = state.recommendation(ds)
        st.subheader(ds.project.name)
        if rec is None:
            ui.verdict("The answer", f"{target} is not reachable with this library",
                       "Pick a lower target in the sidebar or add measures on the Set up page.", bad=True)
        else:
            gain = cheap["lcc"] - rec["lcc"]
            if tuple(rec["selection"]) == tuple(cheap["selection"]):
                head = f"{rec['level']} with {rec['points']:g} points, and the cheapest route is also the best one"
                sub = f"Life-cycle cost {ui.inr(rec['lcc'])} (present worth) over {ds.project.study_period} years."
            else:
                head = f"{rec['level']} for {ui.inr(gain)} less over {ds.project.study_period} years"
                sub = (f"Spend {ui.inr(rec['capex'] - cheap['capex'])} more upfront than the cheapest {target} route; "
                       f"electricity savings repay it with interest above the MARR. {rec['points']:g} points, {rec['co2_t']:,.0f} t CO₂ avoided.")
            ui.verdict("The answer", head, sub)
        st.page_link(ui.PAGES["rec"][0], label="See why →", icon=":material/workspace_premium:")
        with st.expander("Things to try (a 5-minute tour)", expanded=True):
            ui.md("""
- **Change the target** in the sidebar (Certified to Platinum) and watch the recommendation, cost and points update on every page.
- **Recommendation**: drag the *electricity price growth* and *MARR* sliders to see when the ranking flips.
- **Recommendation → Compare measures**: pick two measures (e.g. VRF vs chiller) to see [[lcc|PW]], [[eac|EUAC]], [[bcr|BCR]], [[irr|IRR]] and the [[cfd|cash flow diagram]].
- **Recommendation → How it works**: the five steps behind the answer, and the same answer rebuilt by hand ([[hand_check|hand-check]]).
- **Can we trust it?**: break-even points, tornado and Monte Carlo.
- **Report**: preview and download the PDF decision report and the Excel workbook.
""")
        if st.button("Clear the project and start over", icon=":material/restart_alt:"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

st.write("")
st.markdown("##### What goes in: one Excel input workbook")
ui.caption("Everything the tool needs is in a single `.xlsx` file with four sheets (plus a README sheet that explains every column). "
           "The tabs below show the real demo file. Download it on the left, edit the values, and open it again.")
_SHEETS = [
    ("Project", "Project", "One row per input: the value, its unit, its meaning and its source. Building size, [[marr|MARR]], [[inflation|inflation]], "
     "[[tariff_esc|tariff escalation]], [[study_period|study period]], solar assumptions and the target level."),
    ("Measures", "Measures", "One row per green option, entered as the difference from the [[baseline|code-minimum option]]: upfront cost ([[capex|capex]]), life, "
     "[[om|O&M]], energy and water saved, [[kwp|solar size]], [[degradation|degradation]], one [[part|replaceable part]], its IGBC [[credit|credit]] and [[group|group]]."),
    ("IGBC_credits", "IGBC credits", "How each [[credit|credit]] earns [[points|points]]: a fixed number, or in steps by the % of energy or water saved. "
     "Flags the [[mandatory|mandatory credits]]."),
    ("IGBC_levels", "IGBC levels", "The points needed for Certified, Silver, Gold and Platinum."),
]


@st.cache_data
def _sheet(name: str) -> pd.DataFrame:
    return pd.read_excel(DEMO_INPUT, sheet_name=name)


if DEMO_INPUT.exists():
    for tab, (sheet, title, blurb) in zip(st.tabs([f"{t[1]}" for t in _SHEETS]), _SHEETS):
        with tab:
            ui.md(blurb)
            st.dataframe(_sheet(sheet), width="stretch", hide_index=True, height=250)

st.write("")
st.markdown("##### Why this tool exists")
c1, c2, c3 = st.columns(3)
c1.markdown(ui.card("First-cost bias", "Green buildings cost 2–17% more upfront, yet lifetime savings often exceed 20% of construction cost. Lowest-price (L1) tendering hides this.", "L1"), unsafe_allow_html=True)
c2.markdown(ui.card("Tariff & policy risk", "Commercial tariffs keep rising while the solar [[export|export credit]] sits near ₹2.82/kWh in Maharashtra. One payback number hides that risk.", "₹ risk"), unsafe_allow_html=True)
c3.markdown(ui.card("Credits chased blindly", "An [[igbc|IGBC rating]] has marketing and compliance value, but the cheapest [[credit|credits]] to buy are rarely the cheapest to own over the building's life.", "IGBC"), unsafe_allow_html=True)

if ds is not None:
    ui.next_step("setup", "Check or change the assumptions first, or skip straight to the recommendation from the sidebar.")
