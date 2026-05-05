import streamlit as st
from sidebar import render_handbook_link
import pandas as pd
import math

# --- Page config -----------------------------------------------------------
st.set_page_config(
    page_title="Load Calculator · Refrigtools",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded",
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

# --- Header ----------------------------------------------------------------
st.title("❄️ Refrigeration load calculator")
st.caption("Preliminary load estimate · Transmission + Product + Infiltration + Internal")

st.info(
    "**Preliminary estimate for reference and learning.** "
    "Covers the four main load components per ASHRAE methodology. "
    "Floor heat gain uses simplified UA·Δt. "
    "Packaging moisture sorption and detailed defrost analysis not included. "
    "Final equipment sizing should use full ASHRAE Ch. 24 methodology."
)

# --- Sidebar: room geometry and design conditions -------------------------
with st.sidebar:
    st.markdown("### 🏗️ Room")
    length = st.number_input("Length (m)", value=40.5, step=0.5, min_value=1.0, max_value=200.0)
    width = st.number_input("Width (m)", value=67.7, step=0.5, min_value=1.0, max_value=200.0)
    height = st.number_input("Height (m)", value=9.0, step=0.5, min_value=2.0, max_value=20.0)

    st.divider()
    st.markdown("### 🌡️ Inside temperature")
    t_inside = st.number_input("Inside temp (°C)", value=-23.0, step=1.0, min_value=-40.0, max_value=20.0)

    st.divider()
    st.markdown("### ⚙️ Safety & diversity")
    safety_factor = st.slider("Safety factor (%)", min_value=0, max_value=30, value=10, step=5)
    diversity_factor = st.slider("Diversity factor", min_value=0.70, max_value=1.00, value=1.00, step=0.05)

# --- Psychrometric helpers (used by infiltration) -------------------------
def saturation_pressure_kpa(t_c):
    return 0.6108 * math.exp((17.27 * t_c) / (t_c + 237.3))

def humidity_ratio(t_c, rh_pct, p_atm_kpa=101.325):
    p_sat = saturation_pressure_kpa(t_c)
    p_w = (rh_pct / 100) * p_sat
    if p_atm_kpa - p_w <= 0:
        return 0
    return 0.622 * p_w / (p_atm_kpa - p_w)

def air_enthalpy_kj_per_kg(t_c, rh_pct):
    W = humidity_ratio(t_c, rh_pct)
    return 1.006 * t_c + W * (2501 + 1.86 * t_c)

def air_density_kg_per_m3(t_c, rh_pct, p_atm_kpa=101.325):
    T_k = t_c + 273.15
    W = humidity_ratio(t_c, rh_pct)
    rho_dry = (p_atm_kpa * 1000) / (287.05 * T_k)
    return rho_dry * (1 + W) / (1 + 1.6078 * W)

def calculate_door_load(door, t_inside, rh_inside=90.0):
    h_i = air_enthalpy_kj_per_kg(door["t_outside"], door["rh_outside"])
    h_r = air_enthalpy_kj_per_kg(t_inside, rh_inside)
    rho_i = air_density_kg_per_m3(door["t_outside"], door["rh_outside"])
    rho_r = air_density_kg_per_m3(t_inside, rh_inside)

    if rho_i > 0 and rho_r > 0 and rho_i < rho_r:
        Fm = (2 / (1 + (rho_r / rho_i) ** (1/3))) ** 1.5
    else:
        Fm = 1.0

    door_area = door["width"] * door["height"]
    delta_h = h_i - h_r
    g = 9.81

    if delta_h > 0 and rho_i < rho_r:
        q_full_open = (
            0.221 * door_area * delta_h * rho_r *
            (1 - rho_i / rho_r) ** 0.5 *
            (g * door["height"]) ** 0.5 * Fm
        )
    else:
        q_full_open = 0

    seconds_open = door["passages_per_hour"] * door["seconds_per_passage"]
    Dt = min(seconds_open / 3600.0, 1.0)

    load_kw = q_full_open * Dt * door["flow_factor"] * (1 - door["effectiveness"])

    return {
        "load_kw": load_kw,
        "q_full_open_kw": q_full_open,
        "Dt": Dt,
        "door_area": door_area,
        "delta_h": delta_h,
        "Fm": Fm,
    }

# --- Tabs ------------------------------------------------------------------
tab_trans, tab_prod, tab_inf, tab_int = st.tabs([
    "🧱 Transmission",
    "📦 Product",
    "🚪 Infiltration",
    "💡 Internal"
])

# =============================================================================
# TRANSMISSION
# =============================================================================
with tab_trans:
    st.subheader("Transmission load")
    st.caption("Heat through walls, ceiling, and floor. ASHRAE Eq. 1: q = U·A·Δt")

    surfaces_data = {
        "Roof":         {"u": 0.1344, "t_adj": 38.9, "sun": 5.5, "formula": "L × W"},
        "Floor":        {"u": 0.1779, "t_adj": 15.5, "sun": 0.0, "formula": "L × W"},
        "Wall (East)":  {"u": 0.1718, "t_adj": 33.3, "sun": 0.0, "formula": "W × H"},
        "Wall (North)": {"u": 0.1718, "t_adj": 33.3, "sun": 0.0, "formula": "L × H"},
        "Wall (West)":  {"u": 0.1718, "t_adj": -2.2, "sun": 0.0, "formula": "W × H"},
        "Wall (South)": {"u": 0.1718, "t_adj":  7.2, "sun": 0.0, "formula": "L × H"},
    }

    def get_area(formula, L, W, H):
        if formula == "L × W":
            return L * W
        elif formula == "W × H":
            return W * H
        elif formula == "L × H":
            return L * H
        return 0

    surface_inputs = {}
    for name, data in surfaces_data.items():
        with st.expander(f"{name}  ({data['formula']})", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                u = st.number_input("U (W/m²·K)", value=data["u"], step=0.01, min_value=0.01, max_value=5.0, key=f"u_{name}")
            with c2:
                t_adj = st.number_input("Adjacent T (°C)", value=data["t_adj"], step=1.0, min_value=-40.0, max_value=60.0, key=f"t_{name}")
            with c3:
                sun = st.number_input("Sun effect (K)", value=data["sun"], step=1.0, min_value=0.0, max_value=15.0, key=f"sun_{name}")
            surface_inputs[name] = {"u": u, "t_adj": t_adj, "sun": sun, "formula": data["formula"]}

    trans_results = []
    trans_total_w = 0
    for name, inputs in surface_inputs.items():
        area = get_area(inputs["formula"], length, width, height)
        delta_t = (inputs["t_adj"] + inputs["sun"]) - t_inside
        load_w = inputs["u"] * area * delta_t
        trans_total_w += load_w
        trans_results.append({
            "Surface": name,
            "Area (m²)": round(area, 1),
            "U (W/m²·K)": round(inputs["u"], 4),
            "Δt (K)": round(delta_t, 1),
            "Load (kW)": round(load_w / 1000, 2),
        })

    trans_total_kw = trans_total_w / 1000

    st.markdown("**Per-surface results**")
    df_trans = pd.DataFrame(trans_results)
    st.dataframe(df_trans, hide_index=True, use_container_width=True)
    st.metric("Transmission subtotal", f"{trans_total_kw:.2f} kW")

# =============================================================================
# PRODUCT
# =============================================================================
with tab_prod:
    st.subheader("Product load")
    st.caption("Heat removed from product. ASHRAE Eq. 5-9.")

    # Product database — typical values for common products
    # Reference: ASHRAE Handbook - Refrigeration, Ch. 19 Table 3 (verify before engineering use)
    PRODUCTS = {
        "Custom (manual entry)": None,
        "--- Meat & Poultry ---": None,
        "Beef, lean": {"cp_above": 3.52, "cp_below": 1.88, "t_freeze": -2.2, "water_pct": 70, "latent": 234},
        "Beef, fatty": {"cp_above": 2.89, "cp_below": 1.68, "t_freeze": -2.2, "water_pct": 49, "latent": 164},
        "Pork, lean": {"cp_above": 2.85, "cp_below": 1.59, "t_freeze": -2.2, "water_pct": 57, "latent": 191},
        "Lamb": {"cp_above": 3.18, "cp_below": 1.68, "t_freeze": -1.7, "water_pct": 61, "latent": 204},
        "Chicken": {"cp_above": 3.32, "cp_below": 1.77, "t_freeze": -2.8, "water_pct": 66, "latent": 220},
        "Fish, white (lean)": {"cp_above": 3.60, "cp_below": 1.93, "t_freeze": -2.2, "water_pct": 80, "latent": 267},
        "Fish, fatty (salmon)": {"cp_above": 3.18, "cp_below": 1.74, "t_freeze": -2.2, "water_pct": 64, "latent": 214},
        "--- Dairy ---": None,
        "Milk, whole": {"cp_above": 3.85, "cp_below": 2.04, "t_freeze": -0.6, "water_pct": 87, "latent": 290},
        "Cheese, hard": {"cp_above": 2.10, "cp_below": 1.34, "t_freeze": -8.3, "water_pct": 37, "latent": 124},
        "Butter": {"cp_above": 1.51, "cp_below": 1.05, "t_freeze": -1.1, "water_pct": 16, "latent": 53},
        "Ice cream": {"cp_above": 3.18, "cp_below": 1.88, "t_freeze": -5.6, "water_pct": 63, "latent": 210},
        "--- Fruits & Vegetables ---": None,
        "Apples": {"cp_above": 3.81, "cp_below": 1.93, "t_freeze": -1.1, "water_pct": 84, "latent": 281},
        "Bananas": {"cp_above": 3.35, "cp_below": 1.76, "t_freeze": -0.8, "water_pct": 75, "latent": 251},
        "Oranges": {"cp_above": 3.81, "cp_below": 1.93, "t_freeze": -0.8, "water_pct": 87, "latent": 291},
        "Strawberries": {"cp_above": 3.89, "cp_below": 1.93, "t_freeze": -0.8, "water_pct": 90, "latent": 301},
        "Tomatoes": {"cp_above": 3.98, "cp_below": 1.97, "t_freeze": -0.5, "water_pct": 94, "latent": 314},
        "Potatoes": {"cp_above": 3.43, "cp_below": 1.80, "t_freeze": -1.7, "water_pct": 78, "latent": 261},
        "Lettuce": {"cp_above": 4.02, "cp_below": 1.97, "t_freeze": -0.2, "water_pct": 95, "latent": 317},
        "Carrots": {"cp_above": 3.77, "cp_below": 1.89, "t_freeze": -1.4, "water_pct": 88, "latent": 294},
        "--- Seafood ---": None,
        "Prawns/shrimp": {"cp_above": 3.64, "cp_below": 1.93, "t_freeze": -2.2, "water_pct": 76, "latent": 254},
        "--- Bakery ---": None,
        "Bread, white": {"cp_above": 2.93, "cp_below": 1.42, "t_freeze": -7.2, "water_pct": 36, "latent": 121},
        "--- Other ---": None,
        "Water (reference)": {"cp_above": 4.18, "cp_below": 2.10, "t_freeze": 0.0, "water_pct": 100, "latent": 334},
    }

    selected_product = st.selectbox(
        "Product type",
        options=list(PRODUCTS.keys()),
        index=list(PRODUCTS.keys()).index("Beef, lean"),
        help="Select a product to auto-fill properties, or 'Custom' to enter manually. "
             "Values are typical reference data — verify against ASHRAE Ch. 19 for engineering use.",
    )

    # Get preset values if available
    preset = PRODUCTS.get(selected_product)
    is_preset = preset is not None

    c1, c2 = st.columns(2)
    with c1:
        product_name = st.text_input(
            "Product description",
            value=selected_product if is_preset else "Custom product",
        )
        mass_per_pallet = st.number_input("Mass per pallet (kg)", value=1134.0, step=10.0, min_value=1.0, max_value=10000.0)
        pallets_per_day = st.number_input("Pallets per day", value=420.0, step=10.0, min_value=0.0, max_value=10000.0)
        pulldown_hours = st.number_input("Pull-down time (h)", value=24.0, step=1.0, min_value=0.5, max_value=72.0)
    with c2:
        t_entry = st.number_input("Entry temperature (°C)", value=-15.0, step=1.0, min_value=-40.0, max_value=60.0)
        t_target = st.number_input("Target temperature (°C)", value=-23.0, step=1.0, min_value=-40.0, max_value=20.0)
        c1_specific = st.number_input(
            "Cp above freezing (kJ/kg·K)",
            value=preset["cp_above"] if is_preset else 3.52,
            step=0.05,
            min_value=0.5,
            max_value=5.0,
            help="Specific heat of unfrozen product. Auto-filled from product selection.",
        )
        c2_specific = st.number_input(
            "Cp below freezing (kJ/kg·K)",
            value=preset["cp_below"] if is_preset else 1.88,
            step=0.05,
            min_value=0.5,
            max_value=5.0,
            help="Specific heat of frozen product. Roughly half of Cp above freezing for most foods.",
        )

    c3, c4 = st.columns(2)
    with c3:
        t_freeze = st.number_input(
            "Freezing temperature (°C)",
            value=preset["t_freeze"] if is_preset else -2.0,
            step=0.5,
            min_value=-30.0,
            max_value=10.0,
            help="Most foods freeze between -3 and -0.5 °C. Auto-filled from product selection.",
        )
    with c4:
        latent_heat = st.number_input(
            "Latent heat of fusion (kJ/kg)",
            value=float(preset["latent"]) if is_preset else 233.0,
            step=5.0,
            min_value=0.0,
            max_value=400.0,
            help="Water content × 334 kJ/kg. Auto-filled from product water content.",
        )

    if is_preset:
        st.caption(
            f"📊 Reference values for **{selected_product}**: water content ≈ {preset['water_pct']}%. "
            f"Verify against ASHRAE Ch. 19 Table 3 for engineering use."
        )

    mass_total_per_day = mass_per_pallet * pallets_per_day
    mass_per_hour = mass_total_per_day / pulldown_hours

    if t_entry > t_freeze and t_target < t_freeze:
        q1_per_kg = c1_specific * (t_entry - t_freeze)
        q2_per_kg = latent_heat
        q3_per_kg = c2_specific * (t_freeze - t_target)
    elif t_entry > t_freeze and t_target >= t_freeze:
        q1_per_kg = c1_specific * (t_entry - t_target)
        q2_per_kg = 0
        q3_per_kg = 0
    elif t_entry <= t_freeze and t_target < t_freeze:
        q1_per_kg = 0
        q2_per_kg = 0
        q3_per_kg = c2_specific * (t_entry - t_target)
    else:
        q1_per_kg = 0
        q2_per_kg = 0
        q3_per_kg = 0

    total_per_kg = q1_per_kg + q2_per_kg + q3_per_kg
    product_load_kw = (mass_per_hour * total_per_kg) / 3600

    st.markdown("**Calculation breakdown**")
    breakdown = pd.DataFrame([
        {"Stage": "Cool to freezing point", "Per kg (kJ/kg)": round(q1_per_kg, 2)},
        {"Stage": "Latent heat (freezing)", "Per kg (kJ/kg)": round(q2_per_kg, 2)},
        {"Stage": "Cool below freezing", "Per kg (kJ/kg)": round(q3_per_kg, 2)},
        {"Stage": "Total per kg", "Per kg (kJ/kg)": round(total_per_kg, 2)},
    ])
    st.dataframe(breakdown, hide_index=True, use_container_width=True)
    st.caption(f"Mass flow: {mass_per_hour:.0f} kg/h ({mass_total_per_day:.0f} kg/day)")
    st.metric("Product subtotal", f"{product_load_kw:.2f} kW")

# =============================================================================
# INFILTRATION (multi-door)
# =============================================================================
with tab_inf:
    st.subheader("Infiltration load")
    st.caption("Heat from door air exchange. Gosney-Olama (ASHRAE Eq. 15) per door.")

    if "doors" not in st.session_state:
        st.session_state.doors = [
            {
                "name": "Loading dock door",
                "width": 2.4, "height": 3.0,
                "t_outside": 33.0, "rh_outside": 50.0,
                "passages_per_hour": 26.0, "seconds_per_passage": 20.0,
                "flow_factor": 0.7, "effectiveness": 0.0,
            }
        ]

    col_add, col_count, _ = st.columns([1, 1, 3])
    with col_add:
        if st.button("➕ Add door", use_container_width=True):
            st.session_state.doors.append({
                "name": f"Door {len(st.session_state.doors) + 1}",
                "width": 1.5, "height": 2.4,
                "t_outside": 25.0, "rh_outside": 50.0,
                "passages_per_hour": 4.0, "seconds_per_passage": 20.0,
                "flow_factor": 0.8, "effectiveness": 0.85,
            })
            st.rerun()
    with col_count:
        st.markdown(f"**{len(st.session_state.doors)} door(s)**")

    door_results = []
    doors_to_remove = []

    for idx, door in enumerate(st.session_state.doors):
        with st.expander(f"🚪 {door['name']}", expanded=(idx == 0)):
            c_name, c_remove = st.columns([4, 1])
            with c_name:
                door["name"] = st.text_input(
                    "Door name", value=door["name"], key=f"door_name_{idx}",
                    label_visibility="collapsed",
                )
            with c_remove:
                if len(st.session_state.doors) > 1:
                    if st.button("🗑️", key=f"remove_{idx}", help="Remove this door"):
                        doors_to_remove.append(idx)

            c1, c2, c3 = st.columns(3)
            with c1:
                door["width"] = st.number_input("Width (m)", value=door["width"], step=0.1, min_value=0.5, max_value=10.0, key=f"w_{idx}")
                door["height"] = st.number_input("Height (m)", value=door["height"], step=0.1, min_value=1.0, max_value=10.0, key=f"h_{idx}")
            with c2:
                door["t_outside"] = st.number_input("Outside T (°C)", value=door["t_outside"], step=1.0, min_value=-30.0, max_value=60.0, key=f"to_{idx}")
                door["rh_outside"] = st.number_input("Outside RH (%)", value=door["rh_outside"], step=5.0, min_value=0.0, max_value=100.0, key=f"rh_{idx}")
            with c3:
                door["passages_per_hour"] = st.number_input("Passages/hour", value=door["passages_per_hour"], step=1.0, min_value=0.0, max_value=200.0, key=f"p_{idx}")
                door["seconds_per_passage"] = st.number_input("Sec/passage", value=door["seconds_per_passage"], step=1.0, min_value=3.0, max_value=120.0, key=f"s_{idx}")

            c4, c5 = st.columns(2)
            with c4:
                door["flow_factor"] = st.slider("Flow factor Df", min_value=0.5, max_value=1.2, value=door["flow_factor"], step=0.1, key=f"ff_{idx}")
            with c5:
                door["effectiveness"] = st.slider("Effectiveness E", min_value=0.0, max_value=1.0, value=door["effectiveness"], step=0.05, key=f"e_{idx}")

            result = calculate_door_load(door, t_inside)
            door_results.append({
                "name": door["name"],
                "load_kw": result["load_kw"],
                "door_area": result["door_area"],
                "Dt": result["Dt"],
                "q_full_open_kw": result["q_full_open_kw"],
            })

            st.metric(f"{door['name']} load", f"{result['load_kw']:.2f} kW")

    if doors_to_remove:
        for idx in sorted(doors_to_remove, reverse=True):
            st.session_state.doors.pop(idx)
        st.rerun()

    st.markdown("**Per-door breakdown**")
    door_table = pd.DataFrame([
        {
            "Door": r["name"],
            "Area (m²)": round(r["door_area"], 2),
            "Peak (kW)": round(r["q_full_open_kw"], 1),
            "Open fraction": round(r["Dt"], 4),
            "Load (kW)": round(r["load_kw"], 2),
        }
        for r in door_results
    ])
    st.dataframe(door_table, hide_index=True, use_container_width=True)

    infil_load_kw = sum(r["load_kw"] for r in door_results)
    st.metric("Infiltration subtotal (all doors)", f"{infil_load_kw:.2f} kW")

# =============================================================================
# INTERNAL
# =============================================================================
with tab_int:
    st.subheader("Internal load")
    st.caption("Lights, motors, people, equipment. ASHRAE Eq. 10 for people.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Lighting**")
        lighting_w_per_m2 = st.number_input("Lighting (W/m²)", value=10.8, step=0.5, min_value=0.0, max_value=50.0)
        floor_area = length * width
        lighting_kw = (lighting_w_per_m2 * floor_area) / 1000

        st.markdown("**People**")
        num_people = st.number_input("Number of people", value=3, step=1, min_value=0, max_value=100)
        heat_per_person = max(272 - 6 * t_inside, 0)
        people_kw = (num_people * heat_per_person) / 1000

    with c2:
        st.markdown("**Fan motors**")
        num_fans = st.number_input("Number of fan motors", value=15, step=1, min_value=0, max_value=200)
        kw_per_fan = st.number_input("Heat gain per fan (kW)", value=1.296, step=0.1, min_value=0.0, max_value=20.0)
        fans_kw = num_fans * kw_per_fan

        st.markdown("**Forklifts/equipment**")
        num_trucks = st.number_input("Number of forklifts", value=3, step=1, min_value=0, max_value=50)
        kw_per_truck = st.number_input("Heat gain per forklift (kW)", value=5.6, step=0.5, min_value=0.0, max_value=30.0)
        trucks_kw = num_trucks * kw_per_truck

    internal_total_kw = lighting_kw + people_kw + fans_kw + trucks_kw

    st.markdown("**Calculation breakdown**")
    int_breakdown = pd.DataFrame([
        {"Source": "Lighting", "Load (kW)": round(lighting_kw, 2)},
        {"Source": f"People ({num_people} × {heat_per_person:.0f} W)", "Load (kW)": round(people_kw, 2)},
        {"Source": f"Fans ({num_fans} × {kw_per_fan:.2f} kW)", "Load (kW)": round(fans_kw, 2)},
        {"Source": f"Forklifts ({num_trucks} × {kw_per_truck:.1f} kW)", "Load (kW)": round(trucks_kw, 2)},
    ])
    st.dataframe(int_breakdown, hide_index=True, use_container_width=True)
    st.metric("Internal subtotal", f"{internal_total_kw:.2f} kW")

# =============================================================================
# TOTAL LOAD SUMMARY
# =============================================================================
st.divider()
st.subheader("📊 Total refrigeration load")

subtotal_kw = trans_total_kw + product_load_kw + infil_load_kw + internal_total_kw
safety_kw = subtotal_kw * (safety_factor / 100)
total_with_safety = subtotal_kw + safety_kw
total_with_diversity = total_with_safety * diversity_factor

m1, m2, m3, m4 = st.columns(4)
m1.metric("Transmission", f"{trans_total_kw:.1f} kW")
m2.metric("Product", f"{product_load_kw:.1f} kW")
m3.metric("Infiltration", f"{infil_load_kw:.1f} kW")
m4.metric("Internal", f"{internal_total_kw:.1f} kW")

st.markdown("---")

m5, m6, m7 = st.columns(3)
m5.metric("Subtotal", f"{subtotal_kw:.1f} kW")
m6.metric(f"+ Safety ({safety_factor}%)", f"{total_with_safety:.1f} kW")
m7.metric(f"× Diversity ({diversity_factor:.2f})", f"{total_with_diversity:.1f} kW")

summary_df = pd.DataFrame([
    {"Component": "Transmission", "Load (kW)": round(trans_total_kw, 2)},
    {"Component": "Product", "Load (kW)": round(product_load_kw, 2)},
    {"Component": "Infiltration", "Load (kW)": round(infil_load_kw, 2)},
    {"Component": "Internal", "Load (kW)": round(internal_total_kw, 2)},
    {"Component": "Subtotal", "Load (kW)": round(subtotal_kw, 2)},
    {"Component": f"Safety factor ({safety_factor}%)", "Load (kW)": round(safety_kw, 2)},
    {"Component": "With safety", "Load (kW)": round(total_with_safety, 2)},
    {"Component": f"After diversity ({diversity_factor:.2f})", "Load (kW)": round(total_with_diversity, 2)},
])

left, mid, right = st.columns([1, 4, 1])
with mid:
    st.dataframe(summary_df, hide_index=True, use_container_width=True)

csv = summary_df.to_csv(index=False)
st.download_button(
    label="📥 Download summary as CSV",
    data=csv,
    file_name="refrigeration_load_summary.csv",
    mime="text/csv",
)

st.divider()

with st.expander("Methodology and limitations"):
    st.markdown(
        """
**Equations implemented (ASHRAE Handbook — Refrigeration, Ch. 24, 2022):**

- Transmission (Eq. 1): q = U·A·Δt per surface, summed
- Product (Eq. 5-9): Heat to cool above freezing, freeze, cool below freezing
- Infiltration (Eq. 15 Gosney-Olama, Eq. 14 with open-time and effectiveness factors)
- People (Eq. 10): q_p = 272 − 6t W per person

**Simplifications (not included in this version):**

- Floor heat gain uses simple UA·Δt rather than Chuangchid-Krarti method
- Packaging moisture sorption (Eq. 11-12) not included
- Defrost heat (Eq. 21-22) not separately calculated
- Single product type only

**Validation:** Default values approximate ASHRAE Example 2 (Ch. 24).

**For final equipment sizing:** Use full ASHRAE Ch. 24 methodology, AIRAH DA17 for AU-specific guidance, or commercial software with engineering review.
"""
    )
# =============================================================================
# PDF EXPORT
# =============================================================================
st.divider()
st.subheader("📄 Export report")

c_proj, c_eng = st.columns(2)
with c_proj:
    project_name = st.text_input("Project name", value="Cold storage facility")
with c_eng:
    engineer_name = st.text_input("Designed by", value="")

if st.button("📄 Generate PDF report", use_container_width=True):
    from fpdf import FPDF
    from datetime import datetime

    class LoadReport(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 14)
            self.cell(0, 8, "Refrigeration Load Estimate", ln=True, align="C")
            self.set_font("Helvetica", "I", 9)
            self.cell(0, 5, "Preliminary estimate - refrigtools.app", ln=True, align="C")
            self.ln(3)
            self.set_draw_color(180, 180, 180)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 5,
                "Preliminary estimate. For final sizing use full ASHRAE Ch. 24 methodology.",
                ln=True, align="C")
            self.cell(0, 5, f"Page {self.page_no()}", align="C")

        def section_heading(self, text):
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(0, 0, 0)
            self.set_fill_color(230, 230, 230)
            self.cell(0, 7, f"  {text}", ln=True, fill=True)
            self.ln(2)

        def kv_row(self, key, value, key_w=70):
            self.set_font("Helvetica", "", 10)
            self.set_text_color(0, 0, 0)
            self.cell(key_w, 6, key)
            self.cell(0, 6, str(value), ln=True)

        def table_header(self, headers, widths):
            self.set_font("Helvetica", "B", 10)
            self.set_fill_color(50, 50, 50)
            self.set_text_color(255, 255, 255)
            for h, w in zip(headers, widths):
                self.cell(w, 7, h, border=0, fill=True, align="L")
            self.ln()

        def table_row(self, cells, widths, fill=False):
            self.set_font("Helvetica", "", 10)
            self.set_text_color(0, 0, 0)
            if fill:
                self.set_fill_color(245, 245, 245)
            for c, w in zip(cells, widths):
                self.cell(w, 6, str(c), border="B", fill=fill, align="L")
            self.ln()

    pdf = LoadReport()
    pdf.add_page()

    # Project info
    pdf.section_heading("Project Information")
    pdf.kv_row("Project name:", project_name)
    if engineer_name:
        pdf.kv_row("Designed by:", engineer_name)
    pdf.kv_row("Date:", datetime.now().strftime("%d %B %Y"))
    pdf.kv_row("Generated by:", "refrigtools.app load calculator v0.3")
    pdf.ln(4)

    # Design conditions
    pdf.section_heading("Design Conditions")
    pdf.kv_row("Room dimensions (L x W x H):", f"{length:.1f} x {width:.1f} x {height:.1f} m")
    pdf.kv_row("Floor area:", f"{length * width:.1f} m^2")
    pdf.kv_row("Inside design temperature:", f"{t_inside:.1f} deg C")
    pdf.kv_row("Safety factor:", f"{safety_factor}%")
    pdf.kv_row("Diversity factor:", f"{diversity_factor:.2f}")
    pdf.ln(4)

    # Summary
    pdf.section_heading("Load Summary")
    pdf.table_header(["Component", "Load (kW)"], [120, 50])
    pdf.table_row(["Transmission", f"{trans_total_kw:.2f}"], [120, 50])
    pdf.table_row(["Product", f"{product_load_kw:.2f}"], [120, 50], fill=True)
    pdf.table_row(["Infiltration", f"{infil_load_kw:.2f}"], [120, 50])
    pdf.table_row(["Internal", f"{internal_total_kw:.2f}"], [120, 50], fill=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(120, 6, "Subtotal", border="B")
    pdf.cell(50, 6, f"{subtotal_kw:.2f}", border="B", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.table_row([f"Safety factor ({safety_factor}%)", f"{safety_kw:.2f}"], [120, 50])
    pdf.table_row(["With safety", f"{total_with_safety:.2f}"], [120, 50], fill=True)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(0, 100, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(120, 8, "TOTAL REFRIGERATION LOAD", fill=True)
    pdf.cell(50, 8, f"{total_with_diversity:.2f} kW", fill=True, ln=True, align="L")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # Transmission detail
    pdf.section_heading("Transmission Detail (ASHRAE Eq. 1)")
    pdf.table_header(["Surface", "Area (m^2)", "U (W/m^2.K)", "dT (K)", "Load (kW)"], [50, 30, 35, 25, 30])
    for i, name in enumerate(surface_inputs):
        inputs = surface_inputs[name]
        area = get_area(inputs["formula"], length, width, height)
        delta_t_val = (inputs["t_adj"] + inputs["sun"]) - t_inside
        load_w = inputs["u"] * area * delta_t_val
        pdf.table_row(
            [name, f"{area:.1f}", f"{inputs['u']:.4f}",
             f"{delta_t_val:.1f}", f"{load_w/1000:.2f}"],
            [50, 30, 35, 25, 30],
            fill=(i % 2 == 0),
        )
    pdf.ln(4)

    # Product detail
    pdf.section_heading("Product Detail (ASHRAE Eq. 5-9)")
    pdf.kv_row("Product:", product_name)
    pdf.kv_row("Mass flow:", f"{mass_per_hour:.0f} kg/h ({mass_total_per_day:.0f} kg/day)")
    pdf.kv_row("Entry temperature:", f"{t_entry:.1f} deg C")
    pdf.kv_row("Target temperature:", f"{t_target:.1f} deg C")
    pdf.kv_row("Cool to freezing point:", f"{q1_per_kg:.1f} kJ/kg")
    pdf.kv_row("Latent heat (freezing):", f"{q2_per_kg:.1f} kJ/kg")
    pdf.kv_row("Cool below freezing:", f"{q3_per_kg:.1f} kJ/kg")
    pdf.kv_row("Total per kg:", f"{total_per_kg:.1f} kJ/kg")
    pdf.ln(4)

    # New page if needed
    if pdf.get_y() > 230:
        pdf.add_page()

    # Infiltration detail
    pdf.section_heading("Infiltration Detail (ASHRAE Eq. 14, 15)")
    pdf.kv_row("Number of doors:", str(len(door_results)))
    pdf.ln(2)
    pdf.table_header(["Door", "Area (m^2)", "Peak (kW)", "Open frac.", "Load (kW)"], [55, 30, 30, 30, 25])
    for i, r in enumerate(door_results):
        pdf.table_row(
            [r["name"][:30], f"{r['door_area']:.2f}", f"{r['q_full_open_kw']:.1f}",
             f"{r['Dt']:.4f}", f"{r['load_kw']:.2f}"],
            [55, 30, 30, 30, 25],
            fill=(i % 2 == 0),
        )
    pdf.ln(4)

    # Internal detail
    pdf.section_heading("Internal Detail (ASHRAE Eq. 10)")
    pdf.kv_row("Lighting:", f"{lighting_kw:.2f} kW ({lighting_w_per_m2:.1f} W/m^2 x {floor_area:.0f} m^2)")
    pdf.kv_row("People:", f"{people_kw:.2f} kW ({num_people} x {heat_per_person:.0f} W)")
    pdf.kv_row("Fan motors:", f"{fans_kw:.2f} kW ({num_fans} x {kw_per_fan:.2f} kW)")
    pdf.kv_row("Forklifts:", f"{trucks_kw:.2f} kW ({num_trucks} x {kw_per_truck:.1f} kW)")
    pdf.ln(4)

    # New page for methodology
    pdf.add_page()
    pdf.section_heading("Methodology and Limitations")
    pdf.set_font("Helvetica", "", 10)
    methodology_text = (
        "Equations from ASHRAE Handbook - Refrigeration, Chapter 24 (2022):\n\n"
        "  - Transmission (Eq. 1): q = U x A x dT per surface, summed\n"
        "  - Product (Eq. 5-9): Sensible + latent heat across freezing\n"
        "  - Infiltration (Eq. 15 Gosney-Olama with time and effectiveness factors)\n"
        "  - People (Eq. 10): q_p = 272 - 6t W per person\n\n"
        "Simplifications in this version:\n\n"
        "  - Floor heat gain uses simple UA*dT (Chuangchid-Krarti method not implemented)\n"
        "  - Packaging moisture sorption (Eq. 11-12) not included\n"
        "  - Defrost heat (Eq. 21-22) not separately calculated\n"
        "  - Single product type per calculation\n\n"
        "For final equipment sizing, use full ASHRAE Ch. 24 methodology, AIRAH DA17 for "
        "AU-specific guidance, or commercial software with proper engineering review."
    )
    pdf.multi_cell(0, 5, methodology_text)
    pdf.ln(4)

    pdf.section_heading("Disclaimer")
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 5,
        "This is a preliminary estimate intended for reference and learning. "
        "Final equipment sizing decisions should be based on full ASHRAE methodology with "
        "professional engineering review. refrigtools.app and its developers accept no "
        "liability for decisions made on the basis of this report."
    )

    pdf_bytes = bytes(pdf.output())

    st.success("PDF report generated.")
    st.download_button(
        label="📥 Download PDF report",
        data=pdf_bytes,
        file_name=f"refrigeration_load_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

st.caption("refrigtools.app · Load calculator v0.3 (multi-door, PDF export)")
st.caption("refrigtools.app · Load calculator v0.3 (multi-door)")