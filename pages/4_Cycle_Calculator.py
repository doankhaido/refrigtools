import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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

# --- Saturation dome computation ------------------------------------------
def compute_saturation_dome(fluid, n_points=80):
    """Return arrays of enthalpy (kJ/kg) and pressure (kPa) along
    saturated liquid (Q=0) and saturated vapour (Q=1) curves."""
    try:
        t_triple = PropsSI("Ttriple", fluid)
    except Exception:
        t_triple = PropsSI("Tmin", fluid)
    t_crit = PropsSI("Tcrit", fluid)

    # Sample more densely near the critical point
    temps = np.concatenate([
        np.linspace(t_triple + 1, t_crit * 0.95, int(n_points * 0.7)),
        np.linspace(t_crit * 0.95, t_crit * 0.999, int(n_points * 0.3)),
    ])

    h_liq, h_vap, p_sat = [], [], []
    for t in temps:
        try:
            h_l = PropsSI("H", "T", t, "Q", 0, fluid) / 1000
            h_v = PropsSI("H", "T", t, "Q", 1, fluid) / 1000
            p = PropsSI("P", "T", t, "Q", 0, fluid) / 1000
            h_liq.append(h_l)
            h_vap.append(h_v)
            p_sat.append(p)
        except Exception:
            continue

    return np.array(h_liq), np.array(h_vap), np.array(p_sat)

def compute_zeotropic_dome(fluid, n_points=80):
    """For zeotropic blends — bubble and dew curves at each pressure
    differ from each other along the dome. Return four arrays:
    h_liq (Q=0), h_vap (Q=1), p_bubble, p_dew."""
    try:
        t_triple = PropsSI("Ttriple", fluid)
    except Exception:
        t_triple = PropsSI("Tmin", fluid)
    t_crit = PropsSI("Tcrit", fluid)

    temps = np.concatenate([
        np.linspace(t_triple + 1, t_crit * 0.95, int(n_points * 0.7)),
        np.linspace(t_crit * 0.95, t_crit * 0.999, int(n_points * 0.3)),
    ])

    h_liq, h_vap, p_bubble, p_dew = [], [], [], []
    for t in temps:
        try:
            h_l = PropsSI("H", "T", t, "Q", 0, fluid) / 1000
            h_v = PropsSI("H", "T", t, "Q", 1, fluid) / 1000
            p_b = PropsSI("P", "T", t, "Q", 0, fluid) / 1000
            p_d = PropsSI("P", "T", t, "Q", 1, fluid) / 1000
            h_liq.append(h_l)
            h_vap.append(h_v)
            p_bubble.append(p_b)
            p_dew.append(p_d)
        except Exception:
            continue

    return np.array(h_liq), np.array(h_vap), np.array(p_bubble), np.array(p_dew)

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

    eta_isen = st.slider(
        "Isentropic efficiency",
        min_value=0.40, max_value=1.00, value=0.65, step=0.05,
        help=(
            "Typical ranges: reciprocating compressors 0.55-0.70, "
            "scroll 0.65-0.80, screw 0.70-0.85, centrifugal 0.75-0.85. "
            "Drops at off-design conditions."
        ),
    )
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
    t_evap_k = t_evap + 273.15
    t_cond_k = t_cond + 273.15

    if zeotropic:
        p_evap = PropsSI("P", "T", t_evap_k, "Q", 1, fluid)
        p_cond = PropsSI("P", "T", t_cond_k, "Q", 0, fluid)
        evap_glide = PropsSI("T", "P", p_evap, "Q", 1, fluid) - PropsSI("T", "P", p_evap, "Q", 0, fluid)
        cond_glide = PropsSI("T", "P", p_cond, "Q", 1, fluid) - PropsSI("T", "P", p_cond, "Q", 0, fluid)
    else:
        p_evap = PropsSI("P", "T", t_evap_k, "Q", 0, fluid)
        p_cond = PropsSI("P", "T", t_cond_k, "Q", 0, fluid)
        evap_glide = 0
        cond_glide = 0

    # Point 1: compressor suction
    if zeotropic:
        t1_k = PropsSI("T", "P", p_evap, "Q", 1, fluid) + superheat
    else:
        t1_k = t_evap_k + superheat
    h1 = PropsSI("H", "P", p_evap, "T", t1_k, fluid)
    s1 = PropsSI("S", "P", p_evap, "T", t1_k, fluid)
    rho1 = PropsSI("D", "P", p_evap, "T", t1_k, fluid)

    # Point 2s isentropic, then point 2 actual
    h2s = PropsSI("H", "P", p_cond, "S", s1, fluid)
    h2 = h1 + (h2s - h1) / eta_isen
    t2_k = PropsSI("T", "P", p_cond, "H", h2, fluid)
    s2 = PropsSI("S", "P", p_cond, "H", h2, fluid)

    # Point 3: condenser outlet
    if zeotropic:
        t3_k = PropsSI("T", "P", p_cond, "Q", 0, fluid) - subcooling
    else:
        t3_k = t_cond_k - subcooling
    h3 = PropsSI("H", "P", p_cond, "T", t3_k, fluid)
    s3 = PropsSI("S", "P", p_cond, "T", t3_k, fluid)

    # Point 4: throttle outlet (h4 = h3)
    h4 = h3
    t4_k = PropsSI("T", "P", p_evap, "H", h4, fluid)
    s4 = PropsSI("S", "P", p_evap, "H", h4, fluid)
    x4 = PropsSI("Q", "P", p_evap, "H", h4, fluid)

    # Performance metrics
    q_evap = (h1 - h4) / 1000
    w_comp = (h2 - h1) / 1000
    q_cond = (h2 - h3) / 1000
    cop_cooling = q_evap / w_comp
    cop_heating = q_cond / w_comp
    pressure_ratio = p_cond / p_evap
    mass_flow = duty_kw / q_evap
    vol_flow_suction = mass_flow / rho1

    # --- Performance metrics display ---------------------------------------
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

    # --- Schematic + P-h diagram side by side ------------------------------
    st.subheader("Cycle visualisation")

    p_evap_disp = f"{kpa_to_unit(p_evap/1000, pressure_unit):.2f} {pressure_unit}"
    p_cond_disp = f"{kpa_to_unit(p_cond/1000, pressure_unit):.2f} {pressure_unit}"
    t_disch = t2_k - 273.15

    schematic_svg = f"""
    <div style="display: flex; justify-content: center; margin: 0;">
    <svg viewBox="0 0 720 480" xmlns="http://www.w3.org/2000/svg" style="max-width: 720px; width: 100%; height: auto;">
      <rect x="180" y="60" width="360" height="80" fill="#FEE2E2" stroke="#DC2626" stroke-width="2" rx="6"/>
      <text x="360" y="95" text-anchor="middle" font-family="sans-serif" font-size="18" font-weight="600" fill="#7F1D1D">Condenser</text>
      <text x="360" y="120" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#991B1B">{t_cond:.1f} °C · {p_cond_disp}</text>

      <rect x="180" y="340" width="360" height="80" fill="#DBEAFE" stroke="#2563EB" stroke-width="2" rx="6"/>
      <text x="360" y="375" text-anchor="middle" font-family="sans-serif" font-size="18" font-weight="600" fill="#1E3A8A">Evaporator</text>
      <text x="360" y="400" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#1E40AF">{t_evap:.1f} °C · {p_evap_disp}</text>

      <rect x="560" y="200" width="120" height="80" fill="#FEF3C7" stroke="#D97706" stroke-width="2" rx="6"/>
      <text x="620" y="235" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600" fill="#78350F">Compressor</text>
      <text x="620" y="258" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#92400E">η = {eta_isen:.2f}</text>

      <rect x="40" y="200" width="120" height="80" fill="#E0E7FF" stroke="#4F46E5" stroke-width="2" rx="6"/>
      <text x="100" y="235" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="600" fill="#312E81">Expansion</text>
      <text x="100" y="255" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="600" fill="#312E81">valve</text>

      <line x1="620" y1="200" x2="620" y2="100" stroke="#374151" stroke-width="2.5"/>
      <line x1="620" y1="100" x2="540" y2="100" stroke="#374151" stroke-width="2.5"/>
      <polygon points="540,100 550,95 550,105" fill="#374151"/>

      <line x1="180" y1="100" x2="100" y2="100" stroke="#374151" stroke-width="2.5"/>
      <line x1="100" y1="100" x2="100" y2="200" stroke="#374151" stroke-width="2.5"/>
      <polygon points="100,200 95,190 105,190" fill="#374151"/>

      <line x1="100" y1="280" x2="100" y2="380" stroke="#374151" stroke-width="2.5"/>
      <line x1="100" y1="380" x2="180" y2="380" stroke="#374151" stroke-width="2.5"/>
      <polygon points="180,380 170,375 170,385" fill="#374151"/>

      <line x1="540" y1="380" x2="620" y2="380" stroke="#374151" stroke-width="2.5"/>
      <line x1="620" y1="380" x2="620" y2="280" stroke="#374151" stroke-width="2.5"/>
      <polygon points="620,280 615,290 625,290" fill="#374151"/>

      <circle cx="555" cy="380" r="14" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
      <text x="555" y="385" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#0F172A">1</text>
      <text x="555" y="350" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#374151">{t1_k - 273.15:.1f} °C</text>

      <circle cx="555" cy="100" r="14" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
      <text x="555" y="105" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#0F172A">2</text>
      <text x="555" y="155" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#374151">{t_disch:.1f} °C</text>

      <circle cx="165" cy="100" r="14" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
      <text x="165" y="105" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#0F172A">3</text>
      <text x="165" y="155" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#374151">{t3_k - 273.15:.1f} °C</text>

      <circle cx="165" cy="380" r="14" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
      <text x="165" y="385" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#0F172A">4</text>
      <text x="165" y="350" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#374151">{t4_k - 273.15:.1f} °C · x={x4:.2f}</text>

      <text x="360" y="35" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600" fill="#0F172A">{display_name} · {duty_kw:.1f} kW · COP = {cop_cooling:.2f}</text>
    </svg>
    </div>
    """

    # --- Build P-h diagram -------------------------------------------------
    fig = go.Figure()

    if zeotropic:
        h_liq_arr, h_vap_arr, p_bubble_arr, p_dew_arr = compute_zeotropic_dome(fluid)
        # Saturated liquid curve (Q=0, bubble line)
        fig.add_trace(go.Scatter(
            x=h_liq_arr, y=p_bubble_arr,
            mode="lines", name="Sat. liquid (bubble)",
            line=dict(color="#2563EB", width=2),
            hovertemplate="h = %{x:.1f} kJ/kg<br>P = %{y:.1f} kPa<extra></extra>",
        ))
        # Saturated vapour curve (Q=1, dew line)
        fig.add_trace(go.Scatter(
            x=h_vap_arr, y=p_dew_arr,
            mode="lines", name="Sat. vapour (dew)",
            line=dict(color="#DC2626", width=2),
            hovertemplate="h = %{x:.1f} kJ/kg<br>P = %{y:.1f} kPa<extra></extra>",
        ))
    else:
        h_liq_arr, h_vap_arr, p_sat_arr = compute_saturation_dome(fluid)
        fig.add_trace(go.Scatter(
            x=h_liq_arr, y=p_sat_arr,
            mode="lines", name="Saturated liquid",
            line=dict(color="#2563EB", width=2),
            hovertemplate="h = %{x:.1f} kJ/kg<br>P = %{y:.1f} kPa<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=h_vap_arr, y=p_sat_arr,
            mode="lines", name="Saturated vapour",
            line=dict(color="#DC2626", width=2),
            hovertemplate="h = %{x:.1f} kJ/kg<br>P = %{y:.1f} kPa<extra></extra>",
        ))

# Critical point — average of saturated liquid and vapour enthalpy near critical
    p_crit_kpa = PropsSI("Pcrit", fluid) / 1000
    try:
        t_near_crit = t_crit_k * 0.999
        h_l_crit = PropsSI("H", "T", t_near_crit, "Q", 0, fluid) / 1000
        h_v_crit = PropsSI("H", "T", t_near_crit, "Q", 1, fluid) / 1000
        h_crit = (h_l_crit + h_v_crit) / 2
        fig.add_trace(go.Scatter(
            x=[h_crit], y=[p_crit_kpa],
            mode="markers", name="Critical point",
            marker=dict(color="#000000", size=8, symbol="x"),
            hovertemplate=f"Critical point<br>h = {h_crit:.1f} kJ/kg<br>P = {p_crit_kpa:.1f} kPa<extra></extra>",
        ))
    except Exception:
        pass

    # Cycle overlay
    # Process 1→2: compression (interpolate between p_evap and p_cond at constant s_actual)
    n_int = 30
    p_compression = np.linspace(p_evap, p_cond, n_int)
    h_compression = []
    for p in p_compression:
        # Linear interpolation in h between h1 and h2 along pressure
        # (true compression path is curved; this approximates well for visualisation)
        frac = (p - p_evap) / (p_cond - p_evap)
        h_compression.append(h1 + frac * (h2 - h1))
    h_compression = np.array(h_compression) / 1000

    # Process 2→3: condensation (constant pressure at p_cond)
    h_condensation = np.linspace(h2, h3, n_int) / 1000
    p_condensation = np.full(n_int, p_cond / 1000)

    # Process 3→4: throttling (constant enthalpy, drop pressure)
    h_throttling = np.full(n_int, h3 / 1000)
    p_throttling = np.linspace(p_cond, p_evap, n_int) / 1000

    # Process 4→1: evaporation (constant pressure at p_evap)
    h_evaporation = np.linspace(h4, h1, n_int) / 1000
    p_evaporation = np.full(n_int, p_evap / 1000)

    cycle_h = np.concatenate([h_compression, h_condensation, h_throttling, h_evaporation])
    cycle_p = np.concatenate([
        p_compression / 1000, p_condensation, p_throttling, p_evaporation
    ])

    fig.add_trace(go.Scatter(
        x=cycle_h, y=cycle_p,
        mode="lines", name="Cycle",
        line=dict(color="#059669", width=3),
        hovertemplate="h = %{x:.1f} kJ/kg<br>P = %{y:.1f} kPa<extra></extra>",
    ))

    # State point markers
    state_h = [h1/1000, h2/1000, h3/1000, h4/1000]
    state_p = [p_evap/1000, p_cond/1000, p_cond/1000, p_evap/1000]
    state_labels = ["1", "2", "3", "4"]

    fig.add_trace(go.Scatter(
        x=state_h, y=state_p,
        mode="markers+text", name="State points",
        marker=dict(color="#0F172A", size=14, line=dict(color="white", width=2)),
        text=state_labels,
        textposition="top center",
        textfont=dict(color="#0F172A", size=14, family="sans-serif"),
        showlegend=False,
        hovertemplate="Point %{text}<br>h = %{x:.1f} kJ/kg<br>P = %{y:.1f} kPa<extra></extra>",
    ))

    fig.update_layout(
        xaxis_title="Specific enthalpy h (kJ/kg)",
        yaxis_title=f"Pressure P (kPa)",
        yaxis_type="log",
        height=500,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)"),
        hovermode="closest",
        plot_bgcolor="#FAFAFA",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#E5E7EB")
    fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB")

    # Layout: schematic on left, P-h on right
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("**System schematic**")
        st.markdown(schematic_svg, unsafe_allow_html=True)

    with col_right:
        st.markdown("**P-h diagram**")
        st.plotly_chart(fig, use_container_width=True)

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

    # --- Warnings ---------------------------------------------------------
    warnings = []

    if t_disch > 130:
        warnings.append(
            f"⚠️ **High discharge temperature ({t_disch:.0f} °C).** Risk of "
            f"compressor oil breakdown above ~120-130 °C. Consider lower "
            f"compression ratio, vapour injection, or different refrigerant."
        )

    if pressure_ratio > 8:
        warnings.append(
            f"⚠️ **High pressure ratio ({pressure_ratio:.1f}).** Single-stage "
            f"compression typically targets <8. Consider two-stage or cascade."
        )

    if pressure_ratio < 1.5:
        warnings.append(
            f"ℹ️ **Low pressure ratio ({pressure_ratio:.1f}).** Verify operating "
            f"conditions are realistic."
        )

    if zeotropic and (evap_glide > 1 or cond_glide > 1):
        warnings.append(
            f"ℹ️ **{display_name} is a zeotropic blend.** Evap glide: "
            f"{evap_glide:.1f} K, cond glide: {cond_glide:.1f} K. Reference "
            f"temps use dew point at evap pressure, bubble point at cond pressure."
        )

    if cop_cooling < 1.5:
        warnings.append(
            f"ℹ️ **Low cooling COP ({cop_cooling:.2f}).** Cycle is operating "
            f"under demanding conditions."
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
- This matches industry convention

**P-h diagram notes:**
- Pressure axis is logarithmic (standard convention)
- Compression line 1→2 is approximated as linear in h vs P; the true path is slightly curved but close for visualisation
- Throttling 3→4 is a vertical line at constant enthalpy
"""
    )

st.caption("refrigtools.app · v0.7")