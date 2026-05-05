import streamlit as st
from sidebar import render_handbook_link
from CoolProp.CoolProp import PropsSI

# --- Page config -----------------------------------------------------------
st.set_page_config(
    page_title="Superheat / Subcooling · Refrigtools",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed",
)
render_handbook_link()

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Refrigerant data ------------------------------------------------------
REFRIGERANTS = {
    "R22": "R22", "R23": "R23", "R32": "R32", "R134a": "R134a", "R290": "R290",
    "R404A": "R404A", "R407C": "R407C", "R410A": "R410A",
    "R454B": "HEOS::R32[0.689]&R1234yf[0.311]",
    "R454C": "HEOS::R32[0.215]&R1234yf[0.785]",
    "R507A": "R507A",
    "R513A": "HEOS::R1234yf[0.56]&R134a[0.44]",
    "R717": "R717", "R744": "R744", "R1234yf": "R1234yf", "R1234ze(E)": "R1234ze(E)",
}

def sort_key(name):
    digits = ""
    for ch in name[1:]:
        if ch.isdigit(): digits += ch
        else: break
    return (int(digits) if digits else 0, name)

sorted_names = sorted(REFRIGERANTS.keys(), key=sort_key)

PRESSURE_UNITS = {"kPa": 1.0, "bar": 100.0, "MPa": 1000.0, "psi": 6.89476}
def kpa_to_unit(kpa, unit): return kpa / PRESSURE_UNITS[unit] * PRESSURE_UNITS["kPa"]
def unit_to_kpa(value, unit): return value * PRESSURE_UNITS[unit] / PRESSURE_UNITS["kPa"]

def is_zeotropic(fluid_string):
    return fluid_string.startswith("HEOS::")

# --- Sidebar (units only) --------------------------------------------------
with st.sidebar:
    st.markdown("### Settings")
    pressure_unit = st.selectbox("Pressure units", list(PRESSURE_UNITS.keys()), index=1)

# --- Main panel ------------------------------------------------------------
st.title("Superheat / Subcooling")
st.caption("Field calculator for service techs")

# Primary inputs in main body
ic1, ic2 = st.columns([1, 1])
with ic1:
    display_name = st.selectbox("Refrigerant", sorted_names)
fluid = REFRIGERANTS[display_name]
with ic2:
    sh_sc_type = st.radio(
        "Calculation",
        ["Superheat", "Subcooling"],
        horizontal=True,
        help="Superheat: suction line. Subcooling: liquid line."
    )

vc1, vc2 = st.columns(2)
with vc1:
    sh_pressure = st.number_input(
        f"Pressure ({pressure_unit})",
        value=kpa_to_unit(800.0 if sh_sc_type == "Superheat" else 1500.0, pressure_unit),
        step=1.0 if pressure_unit == "bar" else 10.0,
        min_value=0.1,
        help="Absolute pressure. If reading from a service gauge (gauge pressure), add ~1 bar / 14.5 psi / 100 kPa.",
    )
with vc2:
    sh_temp = st.number_input(
        "Pipe temp (°C)",
        value=10.0 if sh_sc_type == "Superheat" else 35.0,
        step=0.1,
        min_value=-100.0, max_value=200.0,
        help="Pipe surface temperature from clamp probe or sensor.",
    )

st.divider()

# --- Calculation -----------------------------------------------------------
try:
    p_pa = unit_to_kpa(sh_pressure, pressure_unit) * 1000
    p_crit_pa = PropsSI("Pcrit", fluid)

    if p_pa >= p_crit_pa:
        st.warning(
            "Pressure at or above critical — superheat/subcooling are "
            "undefined in supercritical region."
        )
    else:
        t_bubble_k = PropsSI("T", "P", p_pa, "Q", 0, fluid)
        t_dew_k = PropsSI("T", "P", p_pa, "Q", 1, fluid)
        t_bubble_c = t_bubble_k - 273.15
        t_dew_c = t_dew_k - 273.15
        glide = t_dew_k - t_bubble_k

        if sh_sc_type == "Superheat":
            superheat = sh_temp - t_dew_c
            st.subheader(f"Superheat at {sh_pressure:.3f} {pressure_unit}, {sh_temp:.1f} °C")

            m1, m2 = st.columns(2)
            m1.metric("Saturation T (dew point)", f"{t_dew_c:.2f} °C")
            m2.metric("Measured T", f"{sh_temp:.2f} °C")
            st.metric(
                "Superheat",
                f"{superheat:.2f} K",
                delta_color="inverse" if superheat < 0 else "normal",
            )

            if superheat < 0:
                st.error(
                    f"⚠️ **Negative superheat ({superheat:.1f} K).** Suction is wet — "
                    f"refrigerant is below dew point at this pressure. Risk of liquid "
                    f"floodback to compressor. Check TXV setting, charge, and load conditions."
                )
            elif superheat < 5:
                st.warning(
                    f"Low superheat ({superheat:.1f} K). Acceptable for some flooded "
                    f"systems but typical DX systems target 5–12 K. Verify TXV operation."
                )
            elif superheat <= 12:
                st.success(
                    f"Superheat in typical range (5–12 K) for DX systems. Within normal "
                    f"operating envelope."
                )
            elif superheat <= 25:
                st.warning(
                    f"High superheat ({superheat:.1f} K). May indicate undercharge, "
                    f"restricted metering device, or low evaporator load."
                )
            else:
                st.error(
                    f"Very high superheat ({superheat:.1f} K). Strong indicator of "
                    f"undercharge or significant restriction. Investigate before "
                    f"continuing operation."
                )

            if is_zeotropic(fluid) and glide > 0.5:
                st.info(
                    f"ℹ️ **{display_name}** is a zeotropic blend with {glide:.1f} K glide. "
                    f"Superheat is calculated from the dew point ({t_dew_c:.2f} °C), "
                    f"per industry convention. Bubble point at this pressure: {t_bubble_c:.2f} °C."
                )

        else:  # Subcooling
            subcooling = t_bubble_c - sh_temp
            st.subheader(f"Subcooling at {sh_pressure:.3f} {pressure_unit}, {sh_temp:.1f} °C")

            m1, m2 = st.columns(2)
            m1.metric("Saturation T (bubble point)", f"{t_bubble_c:.2f} °C")
            m2.metric("Measured T", f"{sh_temp:.2f} °C")
            st.metric(
                "Subcooling",
                f"{subcooling:.2f} K",
                delta_color="inverse" if subcooling < 0 else "normal",
            )

            if subcooling < 0:
                st.error(
                    f"⚠️ **Negative subcooling ({subcooling:.1f} K).** Liquid line is "
                    f"above bubble point — flash gas in liquid line. Causes TXV hunting "
                    f"and reduced capacity. Check charge, condenser performance, and "
                    f"liquid line restrictions."
                )
            elif subcooling < 3:
                st.warning(
                    f"Low subcooling ({subcooling:.1f} K). May indicate undercharge or "
                    f"condenser issues. Most systems target 3–15 K."
                )
            elif subcooling <= 15:
                st.success(
                    f"Subcooling in typical range (3–15 K). Within normal operating envelope."
                )
            elif subcooling <= 25:
                st.warning(
                    f"High subcooling ({subcooling:.1f} K). May indicate overcharge, "
                    f"restricted condenser, or non-condensables in the system."
                )
            else:
                st.error(
                    f"Very high subcooling ({subcooling:.1f} K). Strong indicator of "
                    f"overcharge or condenser fault. Investigate before continuing."
                )

            if is_zeotropic(fluid) and glide > 0.5:
                st.info(
                    f"ℹ️ **{display_name}** is a zeotropic blend with {glide:.1f} K glide. "
                    f"Subcooling is calculated from the bubble point ({t_bubble_c:.2f} °C), "
                    f"per industry convention. Dew point at this pressure: {t_dew_c:.2f} °C."
                )

except Exception as e:
    st.error(f"Calculation failed.\n\n_{e}_")

st.divider()

with st.expander("Health range guidance"):
    st.markdown(
        """
**Superheat targets vary by system type.** General DX system rules of thumb:
- **Negative:** suction is wet — risk of liquid floodback
- **0–4 K:** low — verify TXV operation
- **5–12 K:** typical healthy range
- **13–25 K:** high — possible undercharge or restriction
- **>25 K:** very high — investigate before continuing

**Subcooling targets** for typical DX systems:
- **Negative:** flash gas in liquid line
- **0–2 K:** low — possible undercharge or condenser issues
- **3–15 K:** typical healthy range
- **16–25 K:** high — possible overcharge or condenser fault
- **>25 K:** very high — investigate

Specific manufacturer specs override these general ranges. Walk-in freezers,
flooded systems, and heat pumps may target different values. Always check
the system's design specifications when available.
"""
    )

st.caption("refrigtools.app · v0.5")