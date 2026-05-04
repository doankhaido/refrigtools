import streamlit as st

st.set_page_config(
    page_title="Refrigtools",
    page_icon="❄️",
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

# --- Hero -----------------------------------------------------------------
st.title("❄️ Refrigtools")
st.subheader("Refrigerant tools for engineers and technicians")

st.markdown(
    """
A free toolkit for refrigeration work — accurate thermodynamic properties
plus the compliance context (GWP, ASHRAE 34 safety class, phase-down status)
that turns a calculator into a decision tool.
"""
)

st.divider()

# --- Tool cards -----------------------------------------------------------
st.markdown("### Available tools")

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("#### 🧪 Refrigerant Properties")
    st.markdown(
        """
Property calculator for 16 refrigerants — saturation, single-phase, and
transcritical states. Each refrigerant comes with GWP, ASHRAE 34 safety
class, family, and phase-down status displayed alongside.

**Use it for:** sizing, design analysis, retrofit decisions,
transcritical CO2 systems, comparing refrigerants.
"""
    )
    st.page_link("pages/1_Refrigerant_Properties.py", label="Open tool →", icon="🧪")

with row1_col2:
    st.markdown("#### 🔧 Superheat / Subcooling")
    st.markdown(
        """
Field calculator for superheat (suction line) and subcooling (liquid line)
from measured pressure and temperature. Includes health-range diagnostics
and proper handling of zeotropic blend glide.

**Use it for:** charge verification, TXV adjustment, service troubleshooting,
diagnosing undercharge or overcharge conditions.
"""
    )
    st.page_link("pages/2_Superheat_and_Subcooling_Check.py", label="Open tool →", icon="🔧")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("#### 📋 P-T Table")
    # ... existing P-T content stays ...
    st.page_link("pages/3_PT_Table.py", label="Open tool →", icon="📋")

with row2_col2:
    st.markdown("#### 🔄 Cycle Calculator")
    st.markdown(
        """
Vapour-compression cycle analysis with state points, COP, mass flow,
and a labelled schematic. Configurable evap/cond temps, superheat,
subcooling, and isentropic efficiency.

**Use it for:** system design, performance estimation, comparing
operating conditions, training material.
"""
    )
    st.page_link("pages/4_Cycle_Calculator.py", label="Open tool →", icon="🔄")
    st.markdown("#### 📋 P-T Table")
    st.markdown(
        """
Pressure–temperature reference table for saturated refrigerants. Adjustable
range and step, CSV export. Zeotropic blends show bubble and dew points
separately with glide.

**Use it for:** field reference, superheat/subcooling lookups, design sizing,
manual calculations.
"""
    )
    st.page_link("pages/3_PT_Table.py", label="Open tool →", icon="📋")

st.divider()

# --- About / why this exists ---------------------------------------------
st.markdown("### Why refrigtools.app exists")

st.markdown(
    """
Most refrigerant calculators give you thermodynamic properties and stop
there. But practical refrigeration work needs more — what's the GWP, is
this refrigerant phasing down, what's the safety class, what's the
recommended retrofit?

Refrigtools combines accurate calculations (powered by CoolProp) with the
compliance context that engineers and technicians actually need —
in one place, free, with no signup required.

Built by a refrigeration engineer for refrigeration engineers.
"""
)

st.divider()

# --- Coverage -------------------------------------------------------------
with st.expander("Refrigerants supported"):
    st.markdown(
        """
**Pure compounds and azeotropes**  
R-22, R-23, R-32, R-134a, R-290, R-404A, R-407C, R-410A, R-507A,
R-717 (ammonia), R-744 (CO2), R-1234yf, R-1234ze(E)

**Zeotropic blends with proper mixture model**  
R-454B, R-454C, R-513A

**Coming with paid tier:** complex commercial blends (R-448A, R-449A,
R-452A, R-407F) requiring REFPROP-grade thermodynamic data.
"""
    )

with st.expander("Compliance data sources"):
    st.markdown(
        """
- **GWP values** from IPCC AR5 (primary) and AR4 (legacy reference)
- **Safety classifications** per ASHRAE Standard 34
- **Phase-down status** general indicator across major regulatory regimes
  (AU OPSGGM Act, EU F-gas Regulation, US AIM Act)
- **Application notes** drawn from industry practice

Data is for engineering reference. Always verify against current standards
before specifying refrigerants for installations.
"""
    )

st.divider()

st.caption("refrigtools.app · Built with CoolProp · v0.4")