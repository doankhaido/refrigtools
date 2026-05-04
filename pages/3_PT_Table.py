import streamlit as st
import pandas as pd
from CoolProp.CoolProp import PropsSI

# --- Page config -----------------------------------------------------------
st.set_page_config(
    page_title="P-T Table · Refrigtools",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hide Streamlit branding
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
    "R22": "R22",
    "R23": "R23",
    "R32": "R32",
    "R134a": "R134a",
    "R290": "R290",
    "R404A": "R404A",
    "R407C": "R407C",
    "R410A": "R410A",
    "R454B": "HEOS::R32[0.689]&R1234yf[0.311]",
    "R454C": "HEOS::R32[0.215]&R1234yf[0.785]",
    "R507A": "R507A",
    "R513A": "HEOS::R1234yf[0.56]&R134a[0.44]",
    "R717": "R717",
    "R744": "R744",
    "R1234yf": "R1234yf",
    "R1234ze(E)": "R1234ze(E)",
}

def sort_key(name):
    digits = ""
    for ch in name[1:]:
        if ch.isdigit():
            digits += ch
        else:
            break
    return (int(digits) if digits else 0, name)

sorted_names = sorted(REFRIGERANTS.keys(), key=sort_key)

PRESSURE_UNITS = {"kPa": 1.0, "bar": 100.0, "MPa": 1000.0, "psi": 6.89476}

def kpa_to_unit(kpa, unit):
    return kpa / PRESSURE_UNITS[unit] * PRESSURE_UNITS["kPa"]

def is_zeotropic(fluid_string):
    return fluid_string.startswith("HEOS::")

# --- Sidebar ---------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📋 P-T Table")
    st.caption("Pressure-temperature reference for refrigerants")
    st.divider()

    display_name = st.selectbox("Refrigerant", sorted_names)
    fluid = REFRIGERANTS[display_name]

    pressure_unit = st.selectbox("Pressure units", list(PRESSURE_UNITS.keys()), index=1)

    st.divider()
    st.caption("Range")

    if display_name == "R744":
        default_min, default_max = -50, 30
    elif display_name == "R717":
        default_min, default_max = -40, 50
    else:
        default_min, default_max = -40, 60

    t_min = st.number_input("Min temperature (°C)", value=default_min, step=5, min_value=-100, max_value=150)
    t_max = st.number_input("Max temperature (°C)", value=default_max, step=5, min_value=-100, max_value=150)
    t_step = st.selectbox("Step (°C)", [0.5, 1, 2, 5, 10], index=1)

    if t_min >= t_max:
        st.error("Min temperature must be less than max temperature.")
        st.stop()

# --- Main panel: header ---------------------------------------------------
st.title(f"📋 P-T Table — {display_name}")
st.caption(
    f"Saturation pressure of {display_name} from {t_min} °C to {t_max} °C "
    f"in {t_step} °C steps."
)

try:
    t_crit_k = PropsSI("Tcrit", fluid)
    t_crit_c = t_crit_k - 273.15
    p_crit_pa = PropsSI("Pcrit", fluid)
    p_crit_unit = kpa_to_unit(p_crit_pa / 1000, pressure_unit)

    c1, c2 = st.columns(2)
    c1.metric("Critical temperature", f"{t_crit_c:.1f} °C")
    c2.metric("Critical pressure", f"{p_crit_unit:.2f} {pressure_unit}")

    if t_max > t_crit_c:
        st.info(
            f"Above {t_crit_c:.1f} °C, **{display_name}** is supercritical. "
            f"Table values stop at the critical point."
        )
except Exception:
    t_crit_c = None

st.divider()

# --- Build the table ------------------------------------------------------
zeotropic = is_zeotropic(fluid)

temps = []
t = t_min
while t <= t_max + 0.0001:
    temps.append(round(t, 2))
    t += t_step

rows = []
for temp_c in temps:
    temp_k = temp_c + 273.15

    if t_crit_c is not None and temp_c >= t_crit_c:
        break

    try:
        if zeotropic:
            p_bubble = PropsSI("P", "T", temp_k, "Q", 0, fluid) / 1000
            p_dew = PropsSI("P", "T", temp_k, "Q", 1, fluid) / 1000
            t_bubble = PropsSI("T", "P", p_bubble * 1000, "Q", 0, fluid)
            t_dew = PropsSI("T", "P", p_dew * 1000, "Q", 1, fluid)
            rows.append({
                "Temp (°C)": temp_c,
                f"Bubble P ({pressure_unit})": round(kpa_to_unit(p_bubble, pressure_unit), 3),
                f"Dew P ({pressure_unit})": round(kpa_to_unit(p_dew, pressure_unit), 3),
                "Glide (K)": round(t_dew - t_bubble, 2),
            })
        else:
            p_sat = PropsSI("P", "T", temp_k, "Q", 0, fluid) / 1000
            rows.append({
                "Temp (°C)": temp_c,
                f"Pressure ({pressure_unit})": round(kpa_to_unit(p_sat, pressure_unit), 3),
            })
    except Exception:
        continue

if not rows:
    st.warning("No valid saturation data in the selected range. Try adjusting the range.")
else:
    df = pd.DataFrame(rows)

    left, mid, right = st.columns([1, 2, 1])
    with mid:
        st.dataframe(
            df,
            hide_index=True,
            height=min(600, 35 * (len(df) + 1) + 3),
        )

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"PT_table_{display_name}_{t_min}to{t_max}C.csv",
            mime="text/csv",
        )

        if zeotropic:
            st.info(
                "**Zeotropic blend.** Bubble point is where liquid begins to "
                "vaporise; dew point is where the last vapour condenses. The "
                "temperature glide affects evaporator and condenser performance."
            )

st.divider()

with st.expander("How to use this table"):
    st.markdown(
        """
**For service techs:**

- **Suction-side superheat:** Read pressure off your gauge → find saturation
  temperature in this table → measure suction line temperature → subtract
  to get superheat.

- **Liquid-side subcooling:** Read liquid line pressure → find saturation
  temperature → subtract liquid line temperature from saturation temperature
  to get subcooling.

- For **zeotropic blends** (R-454B, R-454C, R-407C, R-513A): use **dew point**
  for superheat, use **bubble point** for subcooling. Industry convention.

**For design engineers:**

- Sizing condensers: look up pressure at design ambient + 5-10 K.
- Sizing evaporators: look up pressure at design evap temp.
- CSV download for spreadsheets and manual calculations.

**For everyone:**

- Pressures shown are absolute. To convert to gauge, subtract atmospheric
  pressure (~1 bar / 100 kPa / 14.5 psi at sea level).
"""
    )

st.caption("refrigtools.app · v0.5")