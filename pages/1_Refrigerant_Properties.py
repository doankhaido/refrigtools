import streamlit as st
from CoolProp.CoolProp import PropsSI

# --- Page config -----------------------------------------------------------
st.set_page_config(
    page_title="Refrigerant Properties · Refrigtools",
    page_icon="🧪",
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
    "R22": {"fluid": "R22", "gwp_ar5": 1760, "gwp_ar4": 1810, "safety": "A1", "family": "HCFC", "phasedown": "Banned / legacy", "notes": "HCFC, ozone-depleting. Phased out under Montreal Protocol. Service-only in most regions."},
    "R23": {"fluid": "R23", "gwp_ar5": 12400, "gwp_ar4": 14800, "safety": "A1", "family": "HFC", "phasedown": "Active phase-down (very high GWP)", "notes": "Used in cascade low-temperature systems. Very high GWP — under pressure to replace."},
    "R32": {"fluid": "R32", "gwp_ar5": 677, "gwp_ar4": 675, "safety": "A2L", "family": "HFC", "phasedown": "Moderate", "notes": "Mildly flammable (A2L). Common in residential AC. Lower GWP than R-410A."},
    "R134a": {"fluid": "R134a", "gwp_ar5": 1300, "gwp_ar4": 1430, "safety": "A1", "family": "HFC", "phasedown": "Active phase-down", "notes": "Widely used in MAC and medium-temp refrigeration. Being replaced by R-1234yf and R-513A."},
    "R290": {"fluid": "R290", "gwp_ar5": 0.02, "gwp_ar4": 3, "safety": "A3", "family": "HC", "phasedown": "Low GWP / not subject", "notes": "Propane. Highly flammable (A3). Excellent thermodynamics, charge-limited by safety codes."},
    "R404A": {"fluid": "R404A", "gwp_ar5": 3943, "gwp_ar4": 3922, "safety": "A1", "family": "HFC blend", "phasedown": "Active phase-down (very high GWP)", "notes": "Legacy commercial refrigerant. High GWP. Common retrofits: R-448A, R-449A, R-454C."},
    "R407C": {"fluid": "R407C", "gwp_ar5": 1624, "gwp_ar4": 1774, "safety": "A1", "family": "HFC blend", "phasedown": "Active phase-down", "notes": "Zeotropic blend with temperature glide ~5–7 K. Used as R-22 replacement."},
    "R410A": {"fluid": "R410A", "gwp_ar5": 1924, "gwp_ar4": 2088, "safety": "A1", "family": "HFC blend", "phasedown": "Active phase-down", "notes": "Dominant in residential AC since 2000s. Being replaced by R-32 and R-454B."},
    "R454B": {"fluid": "HEOS::R32[0.689]&R1234yf[0.311]", "gwp_ar5": 466, "gwp_ar4": 467, "safety": "A2L", "family": "HFC/HFO blend", "phasedown": "Low (target replacement)", "notes": "Designated R-410A replacement. Mildly flammable (A2L). Near-azeotropic."},
    "R454C": {"fluid": "HEOS::R32[0.215]&R1234yf[0.785]", "gwp_ar5": 148, "gwp_ar4": 146, "safety": "A2L", "family": "HFC/HFO blend", "phasedown": "Low (target replacement)", "notes": "R-404A replacement. Low GWP. A2L flammability. Glide ~7–8 K."},
    "R507A": {"fluid": "R507A", "gwp_ar5": 3985, "gwp_ar4": 3922, "safety": "A1", "family": "HFC blend", "phasedown": "Active phase-down (very high GWP)", "notes": "Azeotrope. Used in low/medium-temp commercial. Replacement candidates: R-448A, R-449A."},
    "R513A": {"fluid": "HEOS::R1234yf[0.56]&R134a[0.44]", "gwp_ar5": 573, "gwp_ar4": 631, "safety": "A1", "family": "HFC/HFO blend", "phasedown": "Moderate", "notes": "R-134a replacement. Non-flammable (A1). Near-azeotropic with low glide."},
    "R717": {"fluid": "R717", "gwp_ar5": 0, "gwp_ar4": 0, "safety": "B2L", "family": "Natural", "phasedown": "Low GWP / not subject", "notes": "Ammonia. Toxic (B), mildly flammable (2L). Industrial workhorse. Excellent efficiency."},
    "R744": {"fluid": "R744", "gwp_ar5": 1, "gwp_ar4": 1, "safety": "A1", "family": "Natural", "phasedown": "Low GWP / not subject", "notes": "CO2. Transcritical operation common above 31 °C. Dominant in commercial supermarket systems."},
    "R1234yf": {"fluid": "R1234yf", "gwp_ar5": 0.501, "gwp_ar4": 4, "safety": "A2L", "family": "HFO", "phasedown": "Low GWP / not subject", "notes": "Mobile AC standard. Mildly flammable (A2L). Component in many low-GWP blends."},
    "R1234ze(E)": {"fluid": "R1234ze(E)", "gwp_ar5": 1.37, "gwp_ar4": 6, "safety": "A2L", "family": "HFO", "phasedown": "Low GWP / not subject", "notes": "Used in chillers and high-temperature heat pumps. A2L. Component in some blends."},
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
def kpa_to_unit(kpa, unit): return kpa / PRESSURE_UNITS[unit] * PRESSURE_UNITS["kPa"]
def unit_to_kpa(value, unit): return value * PRESSURE_UNITS[unit] / PRESSURE_UNITS["kPa"]

INPUT_PAIRS = {
    "Temperature + Pressure": ("T", "P"),
    "Temperature + Quality (saturation)": ("T", "Q"),
    "Pressure + Quality (saturation)": ("P", "Q"),
    "Pressure + Enthalpy": ("P", "H"),
    "Pressure + Entropy": ("P", "S"),
}

def safety_color(s):
    if s.startswith("A1"): return "🟢"
    if s.startswith("A2L"): return "🟡"
    if s.startswith("A2"): return "🟠"
    if s.startswith("A3"): return "🔴"
    if s.startswith("B"): return "⚫"
    return "⚪"

def is_zeotropic(fluid_string):
    return fluid_string.startswith("HEOS::")

# --- Sidebar ---------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧪 Refrigerant Properties")
    st.caption("Property calculator with compliance overlay")
    st.divider()

    display_name = st.selectbox("Refrigerant", sorted_names)
    data = REFRIGERANTS[display_name]
    fluid = data["fluid"]

    pressure_unit = st.selectbox("Pressure units", list(PRESSURE_UNITS.keys()), index=1)

    mode = st.radio("Calculation mode", ["Saturation (quick)", "Two-property lookup"])

    st.divider()

    if mode == "Saturation (quick)":
        sat_input = st.radio("Specify by", ["Temperature", "Pressure"], horizontal=True)
        if sat_input == "Temperature":
            sat_temp_c = st.number_input("Temperature (°C)", value=0.0, step=1.0, min_value=-100.0, max_value=150.0)
            sat_pressure = None
        else:
            sat_temp_c = None
            sat_pressure = st.number_input(
                f"Pressure ({pressure_unit})",
                value=kpa_to_unit(500.0, pressure_unit),
                step=1.0 if pressure_unit == "bar" else 100.0,
                min_value=0.1,
            )
    else:
        pair_label = st.selectbox("Input properties", list(INPUT_PAIRS.keys()))
        prop1, prop2 = INPUT_PAIRS[pair_label]
        defaults = {
            "T": 38.0 if display_name == "R744" else 30.0,
            "P": kpa_to_unit(9200.0 if display_name == "R744" else 1000.0, pressure_unit),
            "Q": 0.0, "H": 250.0, "S": 1.0,
        }
        labels = {
            "T": "Temperature (°C)", "P": f"Pressure ({pressure_unit})",
            "Q": "Vapour quality (0=liquid, 1=vapour)",
            "H": "Enthalpy (kJ/kg)", "S": "Entropy (kJ/kg·K)",
        }
        val1 = st.number_input(labels[prop1], value=float(defaults[prop1]), step=1.0 if prop1 in ("T", "P", "H") else 0.05)
        val2 = st.number_input(labels[prop2], value=float(defaults[prop2]), step=1.0 if prop2 in ("T", "P", "H") else 0.05)

# --- Main panel: header ---------------------------------------------------
st.title(display_name)
st.caption(data["notes"])

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "GWP (AR5)",
    f"{data['gwp_ar5']:,.0f}" if data['gwp_ar5'] >= 1 else f"{data['gwp_ar5']:.2f}",
    help="100-year GWP, IPCC AR5. AR4 value: " + (f"{data['gwp_ar4']:,.0f}" if data['gwp_ar4'] >= 1 else f"{data['gwp_ar4']:.2f}"),
)
c2.metric("Safety class", f"{safety_color(data['safety'])} {data['safety']}",
          help="ASHRAE Standard 34. Letter = toxicity (A=lower, B=higher). Number = flammability (1=none, 2L=lower, 2=flammable, 3=higher).")
c3.metric("Family", data["family"])
c4.metric("Phase-down", data["phasedown"])

try:
    t_crit_k = PropsSI("Tcrit", fluid)
    p_crit_pa = PropsSI("Pcrit", fluid)
    t_crit_c = t_crit_k - 273.15
    p_crit_kpa = p_crit_pa / 1000
    crit_available = True

    cc1, cc2, cc3 = st.columns(3)
    cc1.metric("Critical T", f"{t_crit_c:.1f} °C")
    cc2.metric("Critical P", f"{kpa_to_unit(p_crit_kpa, pressure_unit):.2f} {pressure_unit}")
    cc3.metric("Mode", mode.split(" ")[0])
except Exception:
    crit_available = False
    t_crit_k = None
    p_crit_pa = None

st.divider()

def to_si(prop, val, p_unit):
    if prop == "T": return val + 273.15
    if prop == "P": return unit_to_kpa(val, p_unit) * 1000
    if prop == "H": return val * 1000
    if prop == "S": return val * 1000
    return val

# --- Calculation ----------------------------------------------------------
if mode == "Saturation (quick)":
    try:
        if sat_temp_c is not None:
            t_k = sat_temp_c + 273.15
            if crit_available and t_k >= t_crit_k:
                st.warning(f"**{display_name}** is supercritical above {t_crit_c:.1f} °C. Use Two-property lookup.")
            else:
                p = PropsSI("P", "T", t_k, "Q", 0, fluid)
                h_l = PropsSI("H", "T", t_k, "Q", 0, fluid) / 1000
                h_v = PropsSI("H", "T", t_k, "Q", 1, fluid) / 1000
                d_l = PropsSI("D", "T", t_k, "Q", 0, fluid)
                d_v = PropsSI("D", "T", t_k, "Q", 1, fluid)
                st.subheader(f"Saturation at {sat_temp_c:.1f} °C")
                m1, m2, m3 = st.columns(3)
                m1.metric("Pressure", f"{kpa_to_unit(p/1000, pressure_unit):.3f} {pressure_unit}")
                m2.metric("Latent heat", f"{h_v - h_l:.1f} kJ/kg")
                m3.metric("Liquid density", f"{d_l:.1f} kg/m³")
                m4, m5, m6 = st.columns(3)
                m4.metric("Vapour density", f"{d_v:.2f} kg/m³")
                m5.metric("Liquid enthalpy", f"{h_l:.1f} kJ/kg")
                m6.metric("Vapour enthalpy", f"{h_v:.1f} kJ/kg")
        else:
            p_pa = unit_to_kpa(sat_pressure, pressure_unit) * 1000
            if crit_available and p_pa >= p_crit_pa:
                st.warning("Pressure at or above critical. Use Two-property lookup.")
            else:
                t_l = PropsSI("T", "P", p_pa, "Q", 0, fluid)
                t_v = PropsSI("T", "P", p_pa, "Q", 1, fluid)
                h_l = PropsSI("H", "P", p_pa, "Q", 0, fluid) / 1000
                h_v = PropsSI("H", "P", p_pa, "Q", 1, fluid) / 1000
                d_l = PropsSI("D", "P", p_pa, "Q", 0, fluid)
                d_v = PropsSI("D", "P", p_pa, "Q", 1, fluid)
                st.subheader(f"Saturation at {sat_pressure:.3f} {pressure_unit}")
                m1, m2, m3 = st.columns(3)
                if is_zeotropic(fluid):
                    m1.metric("Bubble point T", f"{t_l - 273.15:.2f} °C", help=f"Glide: {t_v - t_l:.2f} K")
                else:
                    m1.metric("Saturation T", f"{t_l - 273.15:.2f} °C")
                m2.metric("Latent heat", f"{h_v - h_l:.1f} kJ/kg")
                m3.metric("Liquid density", f"{d_l:.1f} kg/m³")
                m4, m5, m6 = st.columns(3)
                m4.metric("Vapour density", f"{d_v:.2f} kg/m³")
                m5.metric("Liquid enthalpy", f"{h_l:.1f} kJ/kg")
                m6.metric("Vapour enthalpy", f"{h_v:.1f} kJ/kg")
    except Exception as e:
        st.error(f"Calculation failed.\n\n_{e}_")

else:  # Two-property lookup
    try:
        v1_si = to_si(prop1, val1, pressure_unit)
        v2_si = to_si(prop2, val2, pressure_unit)
        state = {
            "T": PropsSI("T", prop1, v1_si, prop2, v2_si, fluid),
            "P": PropsSI("P", prop1, v1_si, prop2, v2_si, fluid),
            "D": PropsSI("D", prop1, v1_si, prop2, v2_si, fluid),
            "H": PropsSI("H", prop1, v1_si, prop2, v2_si, fluid),
            "S": PropsSI("S", prop1, v1_si, prop2, v2_si, fluid),
        }
        try: state["C"] = PropsSI("C", prop1, v1_si, prop2, v2_si, fluid)
        except Exception: state["C"] = None
        try: state["Phase"] = PropsSI("Phase", prop1, v1_si, prop2, v2_si, fluid)
        except Exception: state["Phase"] = None

        PHASE_LABELS = {0: "Liquid", 1: "Supercritical", 2: "Supercritical gas",
                        3: "Supercritical liquid", 4: "Critical point", 5: "Vapour",
                        6: "Two-phase", 7: "Unknown", 8: "Not imposed"}
        phase_text = PHASE_LABELS.get(int(state["Phase"]), "Unknown") if state.get("Phase") is not None else "—"

        if crit_available:
            if state["T"] > t_crit_k and state["P"] > p_crit_pa: region = "🔴 Transcritical"
            elif state["T"] > t_crit_k: region = "🟠 Supercritical fluid"
            elif state["P"] > p_crit_pa: region = "🟡 Compressed liquid"
            else: region = "🟢 Subcritical"
        else:
            region = "—"

        st.subheader(f"State from {pair_label}")
        st.caption(f"{region} · Phase: **{phase_text}**")

        m1, m2, m3 = st.columns(3)
        m1.metric("Temperature", f"{state['T'] - 273.15:.2f} °C")
        m2.metric("Pressure", f"{kpa_to_unit(state['P']/1000, pressure_unit):.3f} {pressure_unit}")
        m3.metric("Density", f"{state['D']:.2f} kg/m³")
        m4, m5, m6 = st.columns(3)
        m4.metric("Enthalpy", f"{state['H']/1000:.2f} kJ/kg")
        m5.metric("Entropy", f"{state['S']/1000:.4f} kJ/kg·K")
        if state.get("C") is not None:
            m6.metric("Specific heat (cp)", f"{state['C']/1000:.3f} kJ/kg·K")
    except Exception as e:
        err_str = str(e)
        if "not yet supported" in err_str or "INPUTS" in err_str:
            st.error(
                "This combination of inputs isn't supported for this refrigerant. "
                "Try a different input pair — Pressure + Enthalpy or Pressure + "
                "Entropy are the most reliable for off-saturation states."
            )
        else:
            st.error(f"Calculation failed — inputs may be inconsistent or out of range.\n\n_{e}_")

st.divider()

with st.expander("About the compliance data"):
    st.markdown(
        """
- **GWP values:** 100-year Global Warming Potentials from IPCC AR5 (primary) and AR4 (legacy reference).
- **Safety class:** ASHRAE Standard 34. Letter is toxicity (A = lower, B = higher). Number is flammability (1 = none, 2L = lower, 2 = flammable, 3 = higher).
- **Phase-down status:** General indicator. Specific schedules vary by jurisdiction.
- **Notes:** Industry-standard application context.

Always verify against current standards before specifying refrigerants for installations.
"""
    )

st.caption("refrigtools.app · v0.4")