import pandas as pd
import streamlit as st
from pydantic import ValidationError

from core import charts, state, ui
from core.finance import real_rate
from core.io import MEASURE_COLUMNS, cross_check, measures_to_df, rows_to_models
from core.schemas import Dataset, Measure, Project

ui.page_header(1, "Set up the project", "The building, the money assumptions ([[marr|MARR]], [[inflation|inflation]], tariffs) and the green measures you could build. "
               "The demo is already filled in; change anything and every result recomputes.")
ds = ui.require_ds()
p = ds.project
credit_ids = [""] + [c.credit_id for c in ds.credits]


def commit(measures: list[Measure]) -> list[str]:
    new = ds.model_copy(update={"measures": measures})
    errs = cross_check(new)
    if not errs:
        state.set_ds(new)
    return errs


t_proj, t_meas = st.tabs(["Building & money", "Measures"])

with t_proj:
    with st.form("project_form"):
        a, b, c = st.columns(3)
        with a:
            st.markdown("##### Building")
            name = st.text_input("Project name", p.name)
            city = st.text_input("City", p.city)
            roof = st.number_input("Usable roof area (m²)", 0.0, value=float(p.roof_area_m2), step=100.0, help="Caps rooftop solar at 10 m² per kWp.\n\n" + ui.tip("kwp"))
            en = st.number_input("Baseline electricity (kWh/yr)", 1.0, value=float(p.baseline_energy_kwh), step=50000.0,
                                 help="Code-minimum building; IGBC energy % are measured against it.")
            wa = st.number_input("Baseline water (kL/yr)", 0.0, value=float(p.baseline_water_kl), step=500.0)
            base = st.number_input("IGBC points already earned by the base design", 0.0, 100.0, float(p.base_points), 1.0)
        with b:
            st.markdown("##### Money")
            n = st.slider("Study period N (years)", 10, 40, int(p.study_period), help=ui.tip("study_period"))
            d = st.number_input("MARR, nominal (%)", 1.0, 25.0, p.discount_rate * 100, 0.5, help=ui.tip("marr"))
            inf = st.number_input("General inflation (%)", 0.0, 15.0, p.inflation * 100, 0.5,
                                  help=ui.tip("inflation"))
            ui.caption(f"[[real_marr|Real MARR (Fisher)]]: **{real_rate(p.discount_rate, p.inflation)*100:.2f}%** = (1 + MARR) ÷ (1 + inflation) − 1. "
                       "The model works in nominal ₹, so it discounts at the nominal MARR.")
        with c:
            st.markdown("##### Tariffs & solar")
            tar = st.number_input("Grid tariff, year 1 (₹/kWh)", 0.5, value=float(p.grid_tariff), step=0.5)
            esc = st.number_input("Tariff escalation (% / yr)", -3.0, 15.0, p.tariff_escalation * 100, 0.5, help=ui.tip("tariff_esc"))
            sd = st.number_input("Escalation uncertainty, 1 sd (pp)", 0.0, 8.0, p.tariff_escalation_sd * 100, 0.5,
                                 help="How uncertain the tariff growth is. Used by the Monte Carlo simulation on the risk page.\n\n" + ui.tip("mc"))
            exp = st.number_input("Solar export credit (₹/kWh)", 0.0, value=float(p.export_tariff), step=0.1, help=ui.tip("export"))
            wt = st.number_input("Water + sewage tariff (₹/kL)", 0.0, value=float(p.water_tariff), step=5.0)
            wesc = st.number_input("Water tariff escalation (% / yr)", 0.0, 15.0, p.water_escalation * 100, 0.5)
            yld = st.number_input("Solar yield (kWh/kWp/yr)", 100.0, value=float(p.pv_yield_kwh_per_kwp), step=50.0)
            selfc = st.slider("Solar self-consumption share", 0.0, 1.0, float(p.pv_self_consumption), 0.05, help=ui.tip("selfuse"))
            ef = st.number_input("Grid emission factor (tCO₂/MWh)", 0.0, 1.5, float(p.grid_emission_factor), 0.01, help=ui.tip("co2"))
        submitted = st.form_submit_button("Apply changes", type="primary", icon=":material/check:")

    if submitted:
        try:
            newp = Project(name=name, city=city, roof_area_m2=roof, baseline_energy_kwh=en, baseline_water_kl=wa, study_period=n,
                           discount_rate=d / 100, inflation=inf / 100, grid_tariff=tar, tariff_escalation=esc / 100,
                           tariff_escalation_sd=sd / 100, export_tariff=exp, water_tariff=wt, water_escalation=wesc / 100,
                           pv_yield_kwh_per_kwp=yld, pv_self_consumption=selfc, grid_emission_factor=ef,
                           target_level=p.target_level, base_points=base)
            state.set_ds(Dataset(**{**ds.model_dump(), "project": newp.model_dump()}))
            st.success("Project updated. All downstream results will recompute.")
            st.rerun()
        except ValidationError as e:
            st.error("Please fix:\n\n" + "\n".join(f"- **{'.'.join(map(str, x['loc']))}**: {x['msg']}" for x in e.errors()))

    st.write("")
    left, right = st.columns([1.3, 1])
    with left:
        st.plotly_chart(charts.tariff_preview(p.grid_tariff, p.tariff_escalation, p.tariff_escalation_sd, p.study_period),
                        width="stretch", config={"displayModeBar": False})
    with right:
        ui.kpis([("Electricity bill today", ui.inr(p.baseline_energy_kwh * p.grid_tariff), "per year: baseline kWh × tariff", "brand",
                  "The yearly electricity cost of the code-minimum building. Energy-saving measures cut this bill, which is where most of their value comes from."),
                 ("Roof allows up to", f"{p.roof_kwp_cap:,.0f} kWp", "of rooftop solar", "", "@kwp")], cols=1)
        st.write("")
        ui.callout("Percent inputs are annual rates. The <b>target [[igbc|IGBC level]]</b> is set in the sidebar. "
                   "Every input, its unit and its source is also in the input workbook (download it from Home).")

with t_meas:
    df = measures_to_df(ds.measures)
    help_of = {f: f"{mean}" + (f" ({u})" if u else "") for f, _, u, mean in MEASURE_COLUMNS}
    _extra = {"capex": "capex", "om_annual": "om", "kwp": "kwp", "degradation": "degradation", "exclusive_group": "group",
              "credit_id": "credit", "part_name": "part", "points_fixed": "points"}
    for f, k in _extra.items():
        if f in help_of:
            help_of[f] = help_of[f] + "\n\n" + ui.tip(k)
    num = lambda f, lab, fmt="%d": st.column_config.NumberColumn(lab, format=fmt, help=help_of[f])  # noqa: E731
    cfg = {
        "measure_id": st.column_config.TextColumn("ID", required=True, width="small", help=help_of["measure_id"]),
        "name": st.column_config.TextColumn("Name", required=True, width="medium"),
        "exclusive_group": st.column_config.TextColumn("Group", help=help_of["exclusive_group"]),
        "credit_id": st.column_config.SelectboxColumn("IGBC credit", options=credit_ids, help=help_of["credit_id"]),
        "points_fixed": num("points_fixed", "Fixed pts", "%g"),
        "capex": num("capex", "Capex (₹)"),
        "life_years": num("life_years", "Life (yrs)", "%g"),
        "om_annual": num("om_annual", "O&M / yr (₹)"),
        "energy_saving_kwh": num("energy_saving_kwh", "Energy saved (kWh/yr)"),
        "kwp": num("kwp", "Solar kWp", "%g"),
        "water_saving_kl": num("water_saving_kl", "Water saved (kL/yr)"),
        "degradation": num("degradation", "Degradation (fraction/yr)", "%.3f"),
        "part_name": st.column_config.TextColumn("Replaceable part", help=help_of["part_name"]),
        "part_cost": num("part_cost", "Part cost (₹)"),
        "part_life": num("part_life", "Part life (yrs)", "%g"),
        "description": st.column_config.TextColumn("Notes / basis", width="large"),
    }
    edited = st.data_editor(df, column_config=cfg, num_rows="dynamic", width="stretch", hide_index=True, key="lib_editor", height=440)
    c1, c2 = st.columns([1.3, 4])
    if c1.button("Apply measure changes", type="primary", icon=":material/check:"):
        ms, errs = rows_to_models(edited.dropna(how="all"), Measure, "Measures")
        if not errs:
            errs = commit(ms)
        if errs:
            st.error("Not applied:\n\n" + "\n".join(f"- {e}" for e in errs))
        else:
            st.success(f"Library updated: {len(ms)} measures.")
            st.rerun()
    with c2:
        ui.caption("Costs and savings are **incremental** to the [[baseline|code-minimum option]]: a VRF row holds *VRF price minus the split ACs it replaces*. "
                   "A measure is re-bought when its life ends inside the [[study_period|study period]]; its [[part|replaceable part]] every part life. "
                   "Unused life at the end comes back as [[salvage|salvage value]]. Hover any column title for its meaning.")
    with st.expander("IGBC credit tables (reference)"):
        ui.callout("<b>Illustrative [[points|point]] tables.</b> Replace the IGBC_credits and IGBC_levels sheets of the input workbook with values from "
                   "the official IGBC reference guide (see PROJECT_LOG Q-002).", "warn")
        st.dataframe(pd.DataFrame([{**c.model_dump(), "thresholds": " | ".join(f"≥{a:g}% → {b:g}" for a, b in c.thresholds)} for c in ds.credits]),
                     width="stretch", hide_index=True)
        st.dataframe(pd.DataFrame([lv.model_dump() for lv in ds.levels]), width="stretch", hide_index=True)

ui.next_step("rec", "Happy with the inputs? See which combination of measures wins.")
