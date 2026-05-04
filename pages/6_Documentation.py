import streamlit as st

# --- Page config -----------------------------------------------------------
st.set_page_config(
    page_title="Documentation · Refrigtools",
    page_icon="📖",
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

# --- Header ----------------------------------------------------------------
st.title("📖 Documentation")
st.caption("Refrigtools v0.7 · How to use each tool")

st.markdown(
    """
This page documents the five tools available at refrigtools.app. Each tool is designed
to solve a specific problem in refrigeration engineering and HVAC work, with calculations
grounded in published methodology (CoolProp for thermodynamic properties, ASHRAE for
load calculations).

Tools are free to use, with no signup required. All calculations run client-side after
your inputs are submitted. We don't store calculation data.
"""
)

st.divider()

# --- Quick navigation ------------------------------------------------------
st.subheader("Tools at a glance")
st.markdown(
    """
| Tool | Purpose | Best for |
|------|---------|----------|
| **Refrigerant Properties** | Thermodynamic property lookup with compliance overlay | Property checks, refrigerant selection, GWP/safety reference |
| **Superheat & Subcooling** | Field diagnostic for refrigeration system performance | Service technicians, commissioning, troubleshooting |
| **P-T Table** | Saturation pressure-temperature tables | Quick reference, pressure-to-temperature conversion |
| **Cycle Calculator** | Vapour-compression cycle analysis with state points | System design, performance estimation, training |
| **Load Calculator** | Refrigeration load estimation per ASHRAE Ch. 24 | Preliminary equipment sizing, learning ASHRAE methodology |
"""
)

st.divider()

# =============================================================================
# REFRIGERANT PROPERTIES
# =============================================================================
with st.expander("🌡️ **Refrigerant Properties** — How to use", expanded=False):
    st.markdown(
        """
### What it does

Calculates thermodynamic properties of 16 refrigerants at any specified state, with
a compliance overlay showing GWP, ASHRAE 34 safety class, refrigerant family, and
HFC phase-down status.

### Supported refrigerants

**Pure fluids and azeotropes:** R-22, R-23, R-32, R-134a, R-290 (propane), R-404A,
R-407C, R-410A, R-507A, R-717 (ammonia), R-744 (CO₂), R-1234yf, R-1234ze(E)

**Zeotropic blends:** R-454B, R-454C, R-513A, R-407F

R-448A, R-449A, and R-452A are not currently supported due to gaps in CoolProp's
binary interaction parameters. This is a known limitation; supporting them requires
REFPROP licensing.

### How to use it

1. Select a refrigerant from the dropdown
2. Choose your input pair (e.g., temperature and pressure, pressure and quality)
3. Enter the input values
4. The tool returns enthalpy, entropy, density, internal energy, and other properties

### Inputs and outputs

**Pressure inputs are absolute pressure**, not gauge pressure. Field service
technicians reading manifold gauges should add atmospheric pressure (101.325 kPa
or 14.7 psi) to convert gauge to absolute.

**Temperature** is in degrees Celsius by default, with options for Fahrenheit.

**Quality (vapour fraction)**: 0 = saturated liquid, 1 = saturated vapour, values
between 0 and 1 indicate two-phase mixture. Single-phase states return "Superheated"
or "Subcooled" rather than a numeric quality.

### Compliance overlay

Each refrigerant displays:

- **GWP (AR4 and AR5)**: Global warming potential per IPCC assessment reports
- **ASHRAE 34 safety class**: A1 (low toxicity, no flame propagation), A2L (mildly
  flammable), A2 (flammable), A3 (highly flammable), B-class for higher toxicity
- **Family**: HFC, HFO, HCFC, HC, Natural, or blend
- **Phase-down status**: Australian and global HFC phase-down implications

### Known limitations

- Compliance data is based on publicly available references; verify against current
  AS/NZS, EN, or ASHRAE standards for regulatory work
- Some property pairs (e.g., temperature and enthalpy) are not supported by CoolProp
  for all fluids and may return errors
- Critical point handling for pseudo-pure fluids uses an averaging approximation
"""
    )

# =============================================================================
# SUPERHEAT & SUBCOOLING
# =============================================================================
with st.expander("🔧 **Superheat & Subcooling** — How to use", expanded=False):
    st.markdown(
        """
### What it does

Calculates superheat and subcooling values from measured pressures and temperatures,
with diagnostic ranges to indicate whether values are within typical healthy ranges
for refrigeration systems.

### When to use it

This tool is primarily for service technicians and commissioning engineers who need
to verify system performance from field measurements. Typical use cases:

- Charging or topping up a system
- Troubleshooting capacity or temperature problems
- Verifying TXV or EXV operation
- Commissioning new installations

### How to use it

1. Select the refrigerant in the system
2. Enter the measured suction pressure (low side)
3. Enter the measured suction line temperature (at compressor inlet, or where superheat is measured)
4. Enter the measured liquid line pressure (high side)
5. Enter the measured liquid line temperature (at receiver outlet, or where subcooling is measured)
6. The tool calculates superheat and subcooling and indicates whether values are healthy

### How it handles zeotropic blends

For zeotropic blends (R-454B, R-454C, R-513A, R-407F):

- **Superheat** is calculated from the dew point at the suction pressure (vapour
  side of the saturation dome). This matches industry convention for measuring
  superheat in systems with zeotropic blends.
- **Subcooling** is calculated from the bubble point at the liquid line pressure
  (liquid side of the saturation dome). This matches industry convention for
  measuring subcooling.

The tool also displays the temperature glide for each blend at the operating pressures.

### Diagnostic ranges

The healthy ranges shown in the tool are general guidelines and may not match
specific system requirements. Application-specific targets often differ:

- **Residential air conditioning**: typically 5-15 K superheat, 8-15 K subcooling
- **Walk-in coolers/freezers**: typically 5-10 K superheat, 3-8 K subcooling
- **Heat pump heating mode**: superheat targets vary widely by manufacturer

Always consult the equipment manufacturer's commissioning documentation for
authoritative targets.

### Known limitations

- Pressure inputs are absolute. Service technicians using gauge pressures must
  convert (gauge + atmospheric pressure)
- Diagnostic ranges are generic, not application-specific
- The tool assumes steady-state operation; transient conditions during defrost or
  startup will produce misleading values
"""
    )

# =============================================================================
# P-T TABLE
# =============================================================================
with st.expander("📋 **P-T Table** — How to use", expanded=False):
    st.markdown(
        """
### What it does

Generates a saturation pressure-temperature reference table for any supported
refrigerant across a user-defined temperature range, with optional bubble and dew
point columns for zeotropic blends.

### When to use it

This is a quick-reference tool, not a calculator. Typical use cases:

- Field reference when manufacturer P-T charts are unavailable
- Comparing saturation curves of different refrigerants
- Generating reference data for technical documentation
- Training and education

### How to use it

1. Select a refrigerant
2. Set the minimum and maximum temperatures
3. Set the temperature step size (e.g., 5 °C)
4. Choose pressure units (kPa, bar, MPa, or psi)
5. The table displays saturation pressures for each temperature

### Zeotropic blends

For zeotropic blends, the table shows two pressure columns:

- **Bubble pressure**: pressure at which the liquid begins to vaporise (Q=0)
- **Dew pressure**: pressure at which the vapour finishes condensing (Q=1)

The difference between these two pressures at a given temperature represents the
glide. For pure refrigerants and azeotropes, both columns show the same value.

### Export

Tables can be downloaded as CSV for use in spreadsheets or other tools.

### Known limitations

- Some refrigerants have limited valid temperature ranges in CoolProp; values
  outside the valid range will return errors
- The table is based on equation-of-state data, which may differ slightly from
  manufacturer charts based on different reference data
"""
    )

# =============================================================================
# CYCLE CALCULATOR
# =============================================================================
with st.expander("🔄 **Cycle Calculator** — How to use", expanded=False):
    st.markdown(
        """
### What it does

Calculates the four state points of an ideal vapour-compression refrigeration cycle
with user-specified evaporator/condenser temperatures, superheat, subcooling, and
isentropic compressor efficiency. Returns COP, mass flow, refrigeration effect,
heat rejection, compression work, and other performance metrics. Includes a system
schematic and pressure-enthalpy diagram.

### When to use it

- System design and sizing
- Performance estimation under different operating conditions
- Comparing refrigerants for a given application
- Training and education
- Quick check of supplier-quoted performance data

### How to use it

1. Select a refrigerant
2. Choose pressure units
3. Enter operating conditions:
   - Evaporator temperature (saturation temperature on low side)
   - Condenser temperature (saturation temperature on high side)
   - Superheat (degrees above saturation at compressor inlet)
   - Subcooling (degrees below saturation at condenser outlet)
4. Enter compressor parameters:
   - Isentropic efficiency (default 0.65)
   - Cooling duty (kW)
5. The tool calculates all state points and performance metrics

### Outputs

**Performance metrics**:

- COP cooling and COP heating (heat pump operation)
- Pressure ratio (P_cond / P_evap)
- Discharge temperature
- Refrigeration effect (kJ/kg of refrigerant)
- Compression work (kJ/kg)
- Heat rejection (kJ/kg)
- Mass flow rate (in g/s and kg/h)
- Suction volumetric flow (m³/h)

**Visualisations**:

- System schematic with state points 1-4 labelled
- Pressure-enthalpy diagram with saturation dome and cycle overlay (logarithmic
  pressure axis, standard convention)

**State point table**: temperature, pressure, enthalpy, entropy, and quality at
each of the four states.

### Isentropic efficiency guidance

Typical values for selecting isentropic efficiency:

- Reciprocating compressors: 0.55-0.70
- Scroll compressors: 0.65-0.80
- Screw compressors: 0.70-0.85
- Centrifugal compressors: 0.75-0.85

Values drop at off-design conditions. For preliminary calculations without specific
compressor data, 0.65 is a reasonable starting assumption.

### Known limitations

- The compression line on the P-h diagram is a linear approximation in enthalpy;
  the true polytropic path is slightly curved
- The cycle assumes no pressure drop in heat exchangers or piping
- Real compressor performance varies with operating conditions in ways the
  isentropic efficiency parameter cannot fully capture
- Volumetric efficiency (typical 60-90% for real compressors) is not modelled;
  use manufacturer compressor maps for actual capacity calculations
- Transcritical cycles (e.g., R-744 above critical temperature) are not supported;
  the tool flags these conditions and stops
"""
    )

# =============================================================================
# LOAD CALCULATOR
# =============================================================================
with st.expander("❄️ **Load Calculator** — How to use", expanded=False):
    st.markdown(
        """
### What it does

Estimates the total refrigeration load for a cold storage facility based on the
methodology in ASHRAE Handbook — Refrigeration, Chapter 24 (2022). Calculates
transmission load, product load, infiltration load (with multi-door support), and
internal load, then applies safety and diversity factors.

### When to use it

- Preliminary equipment sizing for cold rooms and freezers
- Sanity-checking load calculations from other sources
- Learning ASHRAE Chapter 24 methodology
- Educational reference

**Important**: This is a preliminary estimate, not a substitute for full ASHRAE
methodology. Several load components are simplified (see Limitations below). Final
equipment sizing should use full ASHRAE methodology, AIRAH DA17 for AU-specific
guidance, or commercial software with proper engineering review.

### How to use it

The tool is organised into four tabs covering the four major load components:

**1. Transmission tab**

Heat transferred through walls, ceiling, and floor. For each surface, enter:

- U-value (W/m²·K) — heat transfer coefficient of the construction
- Adjacent temperature (°C) — outdoor air or temperature of adjacent space
- Sun effect (K) — additional ΔT to account for solar gain (per ASHRAE Table 3)

Sun-effect typical values:

- Flat dark roof: up to 11 K
- East/west dark walls: up to 5 K
- North/south dark walls: up to 3 K
- Light-coloured surfaces: half these values
- Internal walls and floors: 0 K

**2. Product tab**

Heat removed from product as it cools and freezes. Select a product from the
preset database (covers common meats, dairy, fruits, vegetables, seafood, bakery)
or enter custom values. Specify:

- Mass per pallet and pallets per day (gives mass flow)
- Pull-down time (hours allowed for heat removal)
- Entry and target temperatures
- Specific heat above and below freezing (auto-filled from preset)
- Freezing temperature and latent heat of fusion (auto-filled from preset)

**3. Infiltration tab**

Heat from air exchange through doorways. Multi-door support — add as many doors
as the facility has. For each door, enter:

- Width and height
- Outside air temperature and relative humidity
- Door passages per hour and seconds per passage
- Flow factor (Df, typically 0.7-1.1)
- Door device effectiveness (E, 0 = no device, 0.85 = strip curtain, 0.95 = airlock)

The calculation uses the Gosney-Olama equation (ASHRAE Eq. 15) with full
psychrometric properties for moist air enthalpy and density.

**4. Internal tab**

Heat from lights, motors, people, and equipment:

- Lighting power per square metre
- Number of people (people heat is calculated per ASHRAE Eq. 10: 272 - 6t W per person)
- Number and power rating of fan motors
- Number and heat output of forklifts

### Outputs

- Per-component subtotals (transmission, product, infiltration, internal)
- Per-surface, per-door, and per-source breakdowns
- Subtotal, with-safety, and after-diversity totals
- CSV export of summary table
- PDF report generation with project name, designed-by name, and full breakdown

### Validation

Default values approximately match ASHRAE Example 2 (Chapter 24, 2022 edition):

- Freezer storage facility, 40.5 × 67.7 × 9 m
- Inside temperature -23 °C, outside 33 °C / 50% RH
- 420 pallets/day at 1134 kg, lean beef
- Three loading dock doors plus two interior doors

With these inputs and 10% safety factor, the tool produces a total load of
approximately 290-310 kW, comparing to ASHRAE Example 2's 305 kW (within typical
engineering tolerances).

### Known limitations

This version simplifies several load components compared to full ASHRAE methodology:

- **Floor heat gain** uses simple UA·Δt rather than the Chuangchid-Krarti
  ground-coupled method
- **Packaging moisture sorption** (ASHRAE Eq. 11-12) is not included; this can
  add 1-5% latent load for facilities with significant cardboard/wood packaging
- **Defrost heat** is not separately calculated using the Love et al. method
  (ASHRAE Eq. 21-22); for low-temperature freezers, this can add 5-15% to the load
- **Single product type** per calculation; real facilities with multiple product
  types would sum the loads
- **Respiration heat** for fresh produce (ASHRAE Ch. 19, Table 9) is not included

For final equipment sizing decisions, consult full ASHRAE Handbook — Refrigeration,
Chapter 24, or AIRAH DA17 for AU-specific guidance, with proper engineering review.

### PDF report

The tool generates a downloadable PDF report containing:

- Project information (name, engineer, date)
- Design conditions
- Load summary with all subtotals and final total
- Per-component detail tables
- Methodology references
- Disclaimer regarding preliminary nature of the estimate
"""
    )

st.divider()

# =============================================================================
# FAQ
# =============================================================================
st.subheader("Frequently Asked Questions")

with st.expander("Are pressure inputs absolute or gauge?"):
    st.markdown(
        """
**All pressure inputs are absolute pressure.**

Service technicians reading manifold gauges measure gauge pressure. To convert to
absolute pressure, add the local atmospheric pressure:

- Standard atmospheric pressure at sea level: **101.325 kPa** (or 14.696 psi, 1.01325 bar)
- High altitude or low pressure systems: subtract approximately 1 kPa per 100 m elevation

Example: gauge reading of 250 kPa corresponds to absolute pressure of 351.325 kPa.
"""
    )

with st.expander("Why are R-448A, R-449A, and R-452A not supported?"):
    st.markdown(
        """
These commercial refrigerants are widely used in supermarket refrigeration but are
not currently supported in refrigtools.app due to a gap in CoolProp's binary
interaction parameters (specifically the R-1234yf ↔ R-125 pair).

Supporting these refrigerants requires REFPROP, the National Institute of Standards
and Technology reference database, which has licensing costs (~$325 USD/year for
single-user licenses).

Adding these refrigerants is on the planned feature list. In the meantime, use
manufacturer P-T charts or licensed software (Cool-Calc, BizziSelect, etc.) for
work involving these refrigerants.
"""
    )

with st.expander("How accurate are the calculations?"):
    st.markdown(
        """
**Thermodynamic property calculations** use CoolProp, an open-source thermophysical
property library based on equation-of-state data published by NIST and other
authoritative sources. Accuracy is generally within 0.1-1% of REFPROP for fluids
with full equation-of-state coverage.

**Cycle calculations** assume an ideal vapour-compression cycle with isentropic
efficiency applied to the compressor. Real-world performance differs due to
pressure drops, heat losses, volumetric efficiency, and off-design operation.
Treat cycle outputs as design-point estimates.

**Load calculations** are validated against ASHRAE Example 2 (Chapter 24, 2022)
within typical engineering tolerances. The tool uses simplified methodology for
some components (see Load Calculator documentation above for details).

For all tools: results are intended for preliminary engineering work, education,
and reference. Critical equipment sizing decisions should be verified against
manufacturer data, full standards methodology, and engineering judgement.
"""
    )

with st.expander("Can I use this for regulatory compliance?"):
    st.markdown(
        """
**No.** Refrigtools.app is for preliminary calculations and reference. Regulatory
compliance work (AS/NZS 5149, ASHRAE Standard 15, EN 378, F-Gas Regulation, etc.)
requires:

- Full standard methodology, not simplified versions
- Documentation of input data sources
- Professional engineering review
- Where applicable, a registered or chartered engineer's sign-off

Use refrigtools.app to inform your work, not to replace authoritative compliance
calculations.
"""
    )

with st.expander("How is data handled?"):
    st.markdown(
        """
**No personal data is collected** by the tools themselves. Calculations are
processed and discarded — refrigtools.app does not store input values, results,
or any record of your usage.

**Anonymous traffic analytics** may be used to understand which tools are used
most. These do not identify individual users.

**Email signups** (where present) are stored only with the email service provider
(Formspree). We use these to send product updates if and when there are any. We
don't sell email lists or share data with third parties.
"""
    )

with st.expander("Is there a paid version?"):
    st.markdown(
        """
Refrigtools.app is currently free with no paid tier. A paid tier is being
considered for the future to support continued development and to access licensed
data sources (REFPROP for additional refrigerants, ASHRAE methodology details,
AS/NZS standards data).

If a paid tier launches, the existing free tools will remain free.
"""
    )

with st.expander("How do I report bugs or request features?"):
    st.markdown(
        """
Refrigtools.app is actively developed and feedback is genuinely valuable. To report
a bug or suggest a feature, contact through the email signup form on the home page,
or via the contact information on the GitHub repository.

When reporting bugs, please include:

- Which tool and what inputs caused the issue
- What you expected to see versus what happened
- Any error messages displayed
"""
    )

st.divider()

# =============================================================================
# ABOUT
# =============================================================================
st.subheader("About refrigtools.app")

st.markdown(
    """
Refrigtools.app is built and maintained by a refrigeration engineer in Australia.
The tool started as a personal project to consolidate routine refrigeration
calculations into a single fast, free, no-signup web tool.

**Built with**: Python, Streamlit, CoolProp, Plotly, fpdf2

**Methodology references**:

- Thermodynamic properties: CoolProp (Bell, Wronski, Quoilin, Lemort, 2014)
- Refrigeration cycle: Standard vapour-compression cycle analysis
- Load calculations: ASHRAE Handbook — Refrigeration, Chapter 24 (2022)
- Compliance data: ASHRAE Standard 34, IPCC AR4/AR5, regional HFC phase-down policies

**Limitations and disclaimer**:

This tool is provided as-is for educational and preliminary engineering work.
Results have not been independently verified for regulatory or safety-critical
applications. Use of refrigtools.app does not constitute engineering advice.
Final design and equipment sizing decisions should be made by qualified engineers
using authoritative standards and manufacturer data.

For comments, corrections, or contributions, see the contact information on the
home page.
"""
)

st.caption("refrigtools.app · Documentation v1.0 · Last updated for tool version v0.7")