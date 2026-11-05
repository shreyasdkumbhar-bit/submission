"""Hover popups: every technical term on screen explains itself (what it is, why we use it, how the tool uses it).

Use  [[key]]  or  [[key|text shown]]  inside any text passed to core/ui helpers, or ui.term("key") for raw HTML.
`tip(key)` gives the same text as markdown for Streamlit's native `help=` on widgets and table columns.
"""
from __future__ import annotations

import html
import re

# key: (name, what it is, why we use it, how GreenLCC uses it)
HOVER: dict[str, tuple[str, str, str, str]] = {
    "marr": ("MARR (required return)",
             "Minimum attractive rate of return: the least yearly return the owner will accept on money put into the building.",
             "Money today is worth more than money later, so future savings must be brought back to today at this rate before they are compared with the price paid now.",
             "Every cash flow is discounted at the MARR (demo: 10%). The 'extra spend' is worth it only if it earns at least the MARR."),
    "real_marr": ("Real MARR (Fisher)",
                  "The MARR with inflation taken out: (1 + MARR) ÷ (1 + inflation) − 1.",
                  "Shows how much the owner really gains in buying power, not just in rupees.",
                  "Shown for reference. The model uses rising rupee prices, so it discounts at the nominal MARR."),
    "lcc": ("Life-cycle cost (present worth)",
            "All costs minus all savings over the study period, each converted to today's rupees. Negative means the measure pays for itself.",
            "The price tag alone ignores years of electricity, maintenance and replacements. This one number puts every option on the same footing.",
            "Computed year by year for each measure and each combination. The lowest life-cycle cost is the recommendation."),
    "eac": ("Cost per year (EUAC)",
            "Equivalent uniform annual cost: the life-cycle cost spread evenly as a yearly amount.",
            "Easier to feel than one big present-worth figure, and fair when options have different lives.",
            "Life-cycle cost × the capital-recovery factor (A/P, MARR, N). It always ranks options in the same order as present worth."),
    "capex": ("Upfront cost (capex)",
              "Money spent at the start (year 0), extra to the code-minimum option it replaces.",
              "It is the figure most buyers look at, so we show it next to the whole-life cost to expose the first-cost trap.",
              "A VRF row holds the VRF price minus the split ACs it replaces."),
    "om": ("O&M (operation and maintenance)",
           "Yearly running and upkeep cost of a measure.",
           "Maintenance is part of what an option really costs over its life.",
           "Added every year and escalated with general inflation."),
    "bcr": ("Benefit-cost ratio (BCR)",
            "Present worth of the savings divided by the present worth of the costs.",
            "A quick test of value: above 1 means the measure returns more than it costs.",
            "Shown for each measure on Compare measures. Accept when above 1."),
    "irr": ("Rate of return (IRR)",
            "The yearly rate at which a measure's present worth is exactly zero.",
            "Lets you compare a measure against the MARR: if it earns more than the MARR it is worth buying.",
            "Shown per measure. If replacements make the cash flow change sign more than once, MIRR is shown instead."),
    "mirr": ("Modified rate of return (MIRR)",
             "A rate of return that assumes costs are financed and savings reinvested at the MARR.",
             "Ordinary IRR can give several answers or none when cash flows change sign more than once; MIRR always gives one.",
             "Used automatically for measures that are re-bought during their life."),
    "inc": ("Return on the extra capex (incremental rate of return)",
            "The rate of return earned only on the extra money spent by the costlier route compared with the cheaper one.",
            "Whether the costlier option is worth it depends on what the extra rupees earn, not on the totals.",
            "If it is at least the MARR, the extra upfront spend is justified (the headline on Recommendation)."),
    "payback": ("Discounted payback",
                "Years until the savings, discounted to today's money, have repaid the cost.",
                "Plain payback ignores the time value of money and can flatter slow-returning projects.",
                "Shown per measure on Compare measures."),
    "salvage": ("Salvage value",
                "The worth of any life still left in equipment at the end of the study period.",
                "Otherwise an option bought late in life would look unfairly expensive.",
                "Credited back at the last year in proportion to the life remaining."),
    "study_period": ("Study period (N)",
                     "The one time window, in years, used to compare every option.",
                     "Options with different lives (LED 12 years, chiller 25) need a common yardstick.",
                     "Demo uses 25 years. Anything re-bought inside it is counted; unused life at the end is credited as salvage."),
    "inflation": ("General inflation",
                  "The yearly rise in prices in general.",
                  "Maintenance and future replacements cost more rupees later.",
                  "Escalates O&M and re-purchase prices (demo 5%)."),
    "tariff_esc": ("Tariff escalation",
                   "How fast the electricity (or water) price rises each year.",
                   "Savings from energy-efficient measures grow as the tariff rises, so this is the most influential assumption.",
                   "Applied to the year-1 tariff each year. The risk page tests slower and faster growth."),
    "degradation": ("Degradation",
                    "The small yearly loss in output as equipment ages (for example solar panels).",
                    "Savings in later years are a little smaller than in year 1.",
                    "Reduces the yearly saving by this fraction each year."),
    "igbc": ("IGBC rating",
             "The Indian Green Building Council's rating: Certified, Silver, Gold or Platinum, earned by collecting points.",
             "Owners want a rating, so the question becomes the cheapest way to reach the points needed.",
             "The tool only considers combinations that reach your target level. Point tables here are illustrative."),
    "points": ("IGBC points",
               "Points earned from credits such as energy saving, renewable energy and water saving.",
               "Points decide which level you reach.",
               "Fixed credits give fixed points; energy and water credits depend on the % saved by the whole mix."),
    "credit": ("IGBC credit",
               "One scoring item in the IGBC checklist, such as energy efficiency or water saving.",
               "Each measure helps with one or more credits.",
               "Credits are scored from the combined savings of the chosen measures, so nothing is double counted."),
    "mandatory": ("Mandatory credits",
                  "Credits every rated building must meet whatever its points.",
                  "A mix that misses one cannot be certified.",
                  "Combinations missing a mandatory credit are discarded."),
    "baseline": ("Code-minimum baseline",
                 "The ordinary building that just meets the code, with no extra green measures.",
                 "Savings and costs only mean something compared with a reference.",
                 "Every measure is entered as the difference from this baseline."),
    "group": ("Group (alternatives)",
              "Measures in one group are alternatives, for example one HVAC system or one solar size.",
              "You can install only one of them.",
              "The optimizer picks at most one per group."),
    "cheapest": ("Cheapest-upfront route",
                 "The lowest-price combination that reaches your target IGBC level (today's usual choice).",
                 "It is the 'defender' we compare against.",
                 "Shown next to the recommended route throughout."),
    "recommended": ("Recommended route",
                    "The combination that reaches your target with the lowest life-cycle cost.",
                    "This is the answer the tool gives.",
                    "Found by checking every possible combination."),
    "break_even": ("Break-even point",
                   "The value of an assumption at which the two routes cost exactly the same.",
                   "It tells you how far an assumption can be wrong before the answer changes.",
                   "Found for the MARR, tariff growth and equipment price. Far from today's value means a safe answer."),
    "tornado": ("Sensitivity (tornado chart)",
                "Each assumption is moved up and down alone, and the effect on cost is drawn as a bar.",
                "Shows which inputs matter most and so deserve checking first.",
                "Longest bars at the top."),
    "mc": ("Monte Carlo simulation",
           "Thousands of random 'what if' futures, each with a different tariff growth, MARR, equipment price and solar output.",
           "One set of assumptions gives one answer; this shows how reliable that answer is.",
           "The share of futures where the recommendation wins is the 'win rate'."),
    "pct": ("P10 / P50 / P90",
            "P50 is the middle outcome. P10 and P90 are the low and high ends: 8 out of 10 futures fall between them.",
            "A range is more honest than one figure.",
            "Shown for both routes in the Monte Carlo results."),
    "winrate": ("Win rate",
                "The share of simulated futures in which the recommended route has the lower life-cycle cost.",
                "A direct measure of confidence in the recommendation.",
                "Close to 100% means the choice is robust."),
    "co2": ("CO₂ avoided",
            "Tonnes of carbon dioxide not emitted over the study period because less grid electricity is used.",
            "Green buildings have environmental value that money alone does not show.",
            "kWh saved × the grid emission factor, added up over the years."),
    "cfd": ("Cash flow diagram",
            "A timeline of one measure's money: payments pointing down, savings pointing up.",
            "It shows when money goes out and comes back.",
            "Shown for any measure on Compare measures."),
    "upgrade": ("Upgrade path",
                "The best mix at each IGBC level, from Certified to Platinum.",
                "Shows what the next level up really costs.",
                "Each step is a comparison of the next level with the previous one."),
    "part": ("Replaceable part",
             "A component that wears out sooner than the whole system, such as solar inverters.",
             "Its repurchase is a real future cost.",
             "Re-bought every part life, at an inflated price."),
    "kwp": ("kWp (solar size)",
            "Peak power rating of the solar panels, in kilowatts.",
            "Bigger systems save more but need roof space.",
            "Capped by the usable roof area (10 m² per kWp)."),
    "export": ("Solar export credit",
               "The price paid for solar electricity sent back to the grid.",
               "It is lower than the retail tariff, so used-on-site solar is worth more.",
               "Applied to the unused share of solar output."),
    "selfuse": ("Solar self-consumption",
                "The share of solar electricity the building uses itself.",
                "It saves the full tariff; the rest is exported at the lower credit.",
                "Splits solar output between the two values."),
    "hand_check": ("Hand-check",
                   "The same life-cycle cost rebuilt with textbook interest-factor formulas.",
                   "Proof that the tool's year-by-year engine agrees with the maths you would do on paper.",
                   "Compare the two totals below; they should match."),
    "feasible": ("Feasible combination",
                 "A combination that reaches the target points, meets every mandatory credit and fits on the roof.",
                 "Only these can be built and certified.",
                 "The optimizer searches all of them and keeps the best."),
}


def tip(key: str) -> str:
    """Markdown text for Streamlit's native help= tooltips."""
    n, what, why, how = HOVER[key]
    return f"**{n}**\n\n**What it is:** {what}\n\n**Why we use it:** {why}\n\n**How it is used here:** {how}"


def popup_html(key: str) -> str:
    n, what, why, how = HOVER[key]
    e = html.escape
    return (f'<span class="pop"><b>{e(n)}</b><i>What it is</i>{e(what)}<i>Why we use it</i>{e(why)}'
            f'<i>How it is used here</i>{e(how)}</span>')


def term(key: str, text: str | None = None, side: str = "") -> str:
    """Inline HTML: dotted-underlined text that opens a popup on hover or keyboard focus."""
    shown = html.escape(text if text is not None else HOVER[key][0].split(" (")[0])
    cls = "term" + (f" {side}" if side else "")
    return f'<span class="{cls}" tabindex="0">{shown}{popup_html(key)}</span>'


_TOKEN = re.compile(r"\[\[([a-z_]+)(?:\|([^\]]+))?\]\]")


def expand(text: str) -> str:
    """Replace [[key]] / [[key|shown]] tokens with hover spans. Unknown keys are left as plain words."""
    def sub(m: re.Match) -> str:
        key, shown = m.group(1), m.group(2)
        return term(key, shown) if key in HOVER else (shown or key)
    return _TOKEN.sub(sub, text)


def rich(text: str) -> str:
    """Like expand(), but HTML-escapes everything that is not a token (for plain-text inputs)."""
    out, last = [], 0
    for m in _TOKEN.finditer(text):
        out.append(html.escape(text[last:m.start()]))
        key, shown = m.group(1), m.group(2)
        out.append(term(key, shown) if key in HOVER else html.escape(shown or key))
        last = m.end()
    out.append(html.escape(text[last:]))
    return "".join(out)
