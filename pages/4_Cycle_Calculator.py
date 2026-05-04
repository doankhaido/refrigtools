import streamlit as st
import pandas as pd
from CoolProp.CoolProp import PropsSI

# --- Page config -----------------------------------------------------------
st.set_page_config(
    page_title="Cycle Calculator · Refrigtools",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

# --- Sidebar inputs --------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔄 Cycle Calculator")
    st.caption("Vapour-compression cycle analysis")
    st.divider()

    display_name = st.selectbox("Refrigerant", sorted_names, index=sorted_names.index("R134a"))
    fluid = REFRIGERANTS[display_name]

    pressure_unit = st.selectbox("Pressure units", list(PRESSURE_UNITS.keys()), index=1)

    st.divider()
    st.caption("Operating conditions")

    t_evap = st.number_input("Evap temperature (°C)", value=-10.0, step=1.0, min_value=-80.0, max_value=50.0)
    t_cond = st.number_input("Cond temperature (°C)", value=40.0, step=1.0, min_value=-30.0, max_value=120.0)
    superheat = st.number_input("Superheat (K)", value=5.0, step=1.0, min_value=0.0, max_value=50.0)
    subcooling = st.number_input("Subcooling (K)", value=3.0, step=1.0, min_value=0.0, max_value=30.0)

    st.divider()
    st.caption("Compressor & duty")

    eta_isen = st.slider("Isentropic efficiency", min_value=0.40, max_value=1.00, value=0.75, step=0.05)
    duty_kw = st.number_input("Cooling duty (kW)", value=10.0, step=1.0, min_value=0.1, max_value=10000.0)

# --- Header ----------------------------------------------------------------
st.title(f"🔄 Vapour-compression cycle — {display_name}")
st.caption(
    f"Evaporator: {t_evap:.1f} °C · Condenser: {t_cond:.1f} °C · "
    f"Superheat: {superheat:.0f} K · Subcooling: {subcooling:.0f} K · "
    f"η_isen = {eta_isen:.2f}"
)

# --- Validation ------------------------------------------------------------
if t_cond <= t_evap:
    st.error("Condenser temperature must be higher than evaporator temperature.")
    st.stop()

try:
    t_crit_k = PropsSI("Tcrit", fluid)
    t_crit_c = t_crit_k - 273.15
    if t_cond + 273.15 >= t_crit_k:
        st.error(
            f"Condenser temperature ({t_cond:.1f} °C) is at or above the critical "
            f"temperature of {display_name} ({t_crit_c:.1f} °C). Standard "
            f"vapour-compression cycle analysis doesn't apply — this would be "
            f"transcritical operation, which uses different assumptions."
        )
        st.stop()
except Exception:
    pass

# --- Cycle calculation -----------------------------------------------------
zeotropic = is_zeotropic(fluid)

try:
    # Saturation pressures
    t_evap_k = t_evap + 273.15
    t_cond_k = t_cond + 273.15

    # For zeotropic blends, use dew point at evap (matches superheat convention)
    # and bubble point at cond (matches subcooling convention)
    if zeotropic:
        p_evap = PropsSI("P", "T", t_evap_k, "Q", 1, fluid)  # dew point
        p_cond = PropsSI("P", "T", t_cond_k, "Q", 0, fluid)  # bubble point
        evap_glide = PropsSI("T", "P", p_evap, "Q", 1, fluid) - PropsSI("T", "P", p_evap, "Q", 0, fluid)
        cond_glide = PropsSI("T", "P", p_cond, "Q", 1, fluid) - PropsSI("T", "P", p_cond, "Q", 0, fluid)
    else:
        p_evap = PropsSI("P", "T", t_evap_k, "Q", 0, fluid)
        p_cond = PropsSI("P", "T", t_cond_k, "Q", 0, fluid)
        evap_glide = 0
        cond_glide = 0

    # Point 1 — compressor suction (saturated vapour at p_evap + superheat)
    if zeotropic:
        t1_k = PropsSI("T", "P", p_evap, "Q", 1, fluid) + superheat
    else:
        t1_k = t_evap_k + superheat
    h1 = PropsSI("H", "P", p_evap, "T", t1_k, fluid)
    s1 = PropsSI("S", "P", p_evap, "T", t1_k, fluid)
    rho1 = PropsSI("D", "P", p_evap, "T", t1_k, fluid)

    # Point 2s — isentropic discharge at p_cond
    h2s = PropsSI("H", "P", p_cond, "S", s1, fluid)
    # Point 2 — actual discharge (apply isentropic efficiency)
    h2 = h1 + (h2s - h1) / eta_isen
    t2_k = PropsSI("T", "P", p_cond, "H", h2, fluid)
    s2 = PropsSI("S", "P", p_cond, "H", h2, fluid)

    # Point 3 — condenser outlet (saturated liquid at p_cond minus subcooling)
    if zeotropic:
        t3_k = PropsSI("T", "P", p_cond, "Q", 0, fluid) - subcooling
    else:
        t3_k = t_cond_k - subcooling
    h3 = PropsSI("H", "P", p_cond, "T", t3_k, fluid)
    s3 = PropsSI("S", "P", p_cond, "T", t3_k, fluid)

    # Point 4 — expansion valve outlet (isenthalpic, h4 = h3)
    h4 = h3
    t4_k = PropsSI("T", "P", p_evap, "H", h4, fluid)
    s4 = PropsSI("S", "P", p_evap, "H", h4, fluid)
    x4 = PropsSI("Q", "P", p_evap, "H", h4, fluid)

    # Performance metrics
    q_evap = (h1 - h4) / 1000  # refrigeration effect, kJ/kg
    w_comp = (h2 - h1) / 1000  # compression work, kJ/kg
    q_cond = (h2 - h3) / 1000  # heat rejection, kJ/kg
    cop_cooling = q_evap / w_comp
    cop_heating = q_cond / w_comp
    pressure_ratio = p_cond / p_evap

    # Mass flow at specified duty
    mass_flow = duty_kw / q_evap  # kg/s
    vol_flow_suction = mass_flow / rho1  # m³/s

    # --- Display: Performance metrics --------------------------------------
    st.subheader("Performance")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("COP cooling", f"{cop_cooling:.2f}")
    m2.metric("COP heating", f"{cop_heating:.2f}")
    m3.metric("Pressure ratio", f"{pressure_ratio:.2f}")
    m4.metric("Discharge T", f"{t2_k - 273.15:.1f} °C")

    m5, m6, m7, m8 = st.columns(4)
    m5.metric("Refrigeration effect", f"{q_evap:.1f} kJ/kg")
    m6.metric("Compression work", f"{w_comp:.1f} kJ/kg")
    m7.metric("Heat rejection", f"{q_cond:.1f} kJ/kg")
    m8.metric("Mass flow", f"{mass_flow*1000:.2f} g/s")

    m9, m10, m11, m12 = st.columns(4)
    m9.metric("Mass flow", f"{mass_flow*3600:.1f} kg/h")
    m10.metric("Suction vol flow", f"{vol_flow_suction*3600:.2f} m³/h")
    m11.metric("Evap pressure", f"{kpa_to_unit(p_evap/1000, pressure_unit):.3f} {pressure_unit}")
    m12.metric("Cond pressure", f"{kpa_to_unit(p_cond/1000, pressure_unit):.3f} {pressure_unit}")

    st.divider()

    # --- Schematic (SVG) ---------------------------------------------------
    st.subheader("Cycle schematic")

    p_evap_disp = f"{kpa_to_unit(p_evap/1000, pressure_unit):.2f} {pressure_unit}"
    p_cond_disp = f"{kpa_to_unit(p_cond/1000, pressure_unit):.2f} {pressure_unit}"
    t_disch = t2_k - 273.15

    schematic_svg = f"""
    <div style="display: flex; justify-content: center; margin: 20px 0;">
    <svg viewBox="0 0 720 480" xmlns="http://www.w3.org/2000/svg" style="max-width: 720px; width: 100%; height: auto;">
      <!-- Condenser (top) -->
      <rect x="180" y="60" width="360" height="80" fill="#FEE2E2" stroke="#DC2626" stroke-width="2" rx="6"/>
      <text x="360" y="95" text-anchor="middle" font-family="sans-serif" font-size="18" font-weight="600" fill="#7F1D1D">Condenser</text>
      <text x="360" y="120" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#991B1B">{t_cond:.1f} °C · {p_cond_disp}</text>

      <!-- Evaporator (bottom) -->
      <rect x="180" y="340" width="360" height="80" fill="#DBEAFE" stroke="#2563EB" stroke-width="2" rx="6"/>
      <text x="360" y="375" text-anchor="middle" font-family="sans-serif" font-size="18" font-weight="600" fill="#1E3A8A">Evaporator</text>
      <text x="360" y="400" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#1E40AF">{t_evap:.1f} °C · {p_evap_disp}</text>

      <!-- Compressor (right) -->
      <rect x="560" y="200" width="120" height="80" fill="#FEF3C7" stroke="#D97706" stroke-width="2" rx="6"/>
      <text x="620" y="235" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600" fill="#78350F">Compressor</text>
      <text x="620" y="258" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#92400E">η = {eta_isen:.2f}</text>

      <!-- Expansion valve (left) -->
      <rect x="40" y="200" width="120" height="80" fill="#E0E7FF" stroke="#4F46E5" stroke-width="2" rx="6"/>
      <text x="100" y="235" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="600" fill="#312E81">Expansion</text>
      <text x="100" y="255" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="600" fill="#312E81">valve</text>

      <!-- Pipes connecting components -->
      <!-- Compressor outlet (2) → Condenser inlet -->
      <line x1="620" y1="200" x2="620" y2="100" stroke="#374151" stroke-width="2.5"/>
      <line x1="620" y1="100" x2="540" y2="100" stroke="#374151" stroke-width="2.5"/>
      <polygon points="540,100 550,95 550,105" fill="#374151"/>

      <!-- Condenser outlet → Expansion valve inlet (3) -->
      <line x1="180" y1="100" x2="100" y2="100" stroke="#374151" stroke-width="2.5"/>
      <line x1="100" y1="100" x2="100" y2="200" stroke="#374151" stroke-width="2.5"/>
      <polygon points="100,200 95,190 105,190" fill="#374151"/>

      <!-- Expansion valve outlet (4) → Evaporator inlet -->
      <line x1="100" y1="280" x2="100" y2="380" stroke="#374151" stroke-width="2.5"/>
      <line x1="100" y1="380" x2="180" y2="380" stroke="#374151" stroke-width="2.5"/>
      <polygon points="180,380 170,375 170,385" fill="#374151"/>

      <!-- Evaporator outlet → Compressor inlet (1) -->
      <line x1="540" y1="380" x2="620" y2="380" stroke="#374151" stroke-width="2.5"/>
      <line x1="620" y1="380" x2="620" y2="280" stroke="#374151" stroke-width="2.5"/>
      <polygon points="620,280 615,290 625,290" fill="#374151"/>

      <!-- State point markers -->
      <!-- Point 1: compressor inlet (top-right of evaporator → compressor) -->
      <circle cx="555" cy="380" r="14" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
      <text x="555" y="385" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#0F172A">1</text>
      <text x="555" y="350" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#374151">{t1_k - 273.15:.1f} °C</text>

      <!-- Point 2: compressor outlet (top side) -->
      <circle cx="555" cy="100" r="14" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
      <text x="555" y="105" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#0F172A">2</text>
      <text x="555" y="155" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#374151">{t_disch:.1f} °C</text>

      <!-- Point 3: condenser outlet -->
      <circle cx="165" cy="100" r="14" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
      <text x="165" y="105" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#0F172A">3</text>
      <text x="165" y="155" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#374151">{t3_k - 273.15:.1f} °C</text>

      <!-- Point 4: expansion valve outlet -->
      <circle cx="165" cy="380" r="14" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
      <text x="165" y="385" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#0F172A">4</text>
      <text x="165" y="350" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#374151">{t4_k - 273.15:.1f} °C · x={x4:.2f}</text>

      <!-- Title -->
      <text x="360" y="35" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600" fill="#0F172A">{display_name} · {duty_kw:.1f} kW cooling · COP = {cop_cooling:.2f}</text>
    </svg>
    </div>
    """

    st.markdown(schematic_svg, unsafe_allow_html=True)

    st.divider()

    # --- State point table -------------------------------------------------
    st.subheader("State points")

    state_table = pd.DataFrame({
        "Point": ["1 (Compressor inlet)", "2 (Compressor outlet)", "3 (Condenser outlet)", "4 (Expansion outlet)"],
        "T (°C)": [t1_k - 273.15, t2_k - 273.15, t3_k - 273.15, t4_k - 273.15],
        f"P ({pressure_unit})": [
            kpa_to_unit(p_evap/1000, pressure_unit),
            kpa_to_unit(p_cond/1000, pressure_unit),
            kpa_to_unit(p_cond/1000, pressure_unit),
            kpa_to_unit(p_evap/1000, pressure_unit),
        ],
        "h (kJ/kg)": [h1/1000, h2/1000, h3/1000, h4/1000],
        "s (kJ/kg·K)": [s1/1000, s2/1000, s3/1000, s4/1000],
        "Quality x": [
            "Superheated",
            "Superheated",
            "Subcooled",
            f"{x4:.3f}",
        ],
    })

    state_table = state_table.round(3)
    left, mid, right = st.columns([1, 4, 1])
    with mid:
        st.dataframe(state_table, hide_index=True)

    st.divider()

    # --- Warnings and notes ------------------------------------------------
    warnings = []

    if t_disch > 130:
        warnings.append(
            f"⚠️ **High discharge temperature ({t_disch:.0f} °C).** Risk of "
            f"compressor oil breakdown and valve damage above ~120-130 °C. "
            f"Consider lower compression ratio, vapour injection, or a different refrigerant."
        )

    if pressure_ratio > 8:
        warnings.append(
            f"⚠️ **High pressure ratio ({pressure_ratio:.1f}).** Single-stage "
            f"compression typically targets <8. Consider two-stage or cascade systems."
        )

    if pressure_ratio < 1.5:
        warnings.append(
            f"ℹ️ **Low pressure ratio ({pressure_ratio:.1f}).** Cycle may not "
            f"need significant compression — verify the operating conditions are realistic."
        )

    if zeotropic and (evap_glide > 1 or cond_glide > 1):
        warnings.append(
            f"ℹ️ **{display_name} is a zeotropic blend.** Evaporator glide: "
            f"{evap_glide:.1f} K. Condenser glide: {cond_glide:.1f} K. "
            f"Reference temperatures use the dew point at evap pressure and "
            f"the bubble point at cond pressure (industry convention)."
        )

    if cop_cooling < 1.5:
        warnings.append(
            f"ℹ️ **Low cooling COP ({cop_cooling:.2f}).** Cycle is operating "
            f"under demanding conditions. Verify evap/cond temperatures match design intent."
        )

    if warnings:
        st.subheader("Notes")
        for w in warnings:
            st.markdown(w)

except Exception as e:
    st.error(
        f"Calculation failed.\n\n_{e}_\n\n"
        f"Try less extreme operating conditions, or check the refrigerant supports "
        f"this temperature range."
    )

st.divider()

with st.expander("About this calculation"):
    st.markdown(
        """
**Standard vapour-compression cycle assumptions:**

- **Evaporator:** isobaric heat absorption from saturated state to superheated vapour at point 1
- **Compressor:** non-isentropic compression with the specified isentropic efficiency
- **Condenser:** isobaric heat rejection from superheated vapour at point 2 to subcooled liquid at point 3
- **Expansion valve:** isenthalpic throttling (h4 = h3)

**Assumptions:**
- No pressure drop in heat exchangers or piping
- No heat loss/gain in the compressor or piping
- Steady-state operation
- Single-stage cycle

**For zeotropic blends:**
- Evaporator pressure derived from dew point at the specified evap temperature
- Condenser pressure derived from bubble point at the specified cond temperature
- This matches the industry convention used in superheat (dew) and subcooling (bubble) measurements

**Real-world deviations:**
- Pressure drops typically reduce capacity by 2-5%
- Heat loss in the compressor reduces actual discharge temperature vs. ideal
- Volumetric efficiency of real compressors typically 60-90% — not modelled here
- This calculator gives ideal-cycle performance; manufacturer compressor maps give actual performance
"""
    )

st.caption("refrigtools.app · v0.6")