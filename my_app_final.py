import streamlit as st
import pandas as pd
import numpy as np

# --- APP CONFIGURATION ---
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .centered-company-name {
        text-align: center;
        font-size: 4em; 
        font-weight: 900;
        color: #FFFFFF; /* Dark color for prominence */
        padding-top: 10px;
        padding-bottom: 5px;
    }
    </style>
    <div class='centered-company-name'>KORTOBA ALUMINIUM</div>
    """,
    unsafe_allow_html=True
)

# 2. Main Application Title (Using st.title for the program name)
st.title("Chemical Stock & Solution Planner 🧪")

st.markdown("---")

# --- Define Constants ---

# Liquid Chemicals: Weight per container (KG/bucket) and density (KG/L)
LIQUID_WEIGHTS = {  # Bucket capacity in KG (Used for inventory input and purchasing list)
    "phosphoric acid": 35.0,
    "sulfuric acid": 46.0,
    "nitric acid": 34.0,
    "acetic acid": 30.0,
}

# 🛠️ CORRECTED DENSITIES: Using the fixed values provided (g/cm³ is equivalent to KG/L)
LIQUID_DENSITIES = {  # ACTUAL density (KG/L) (Used for volume-to-mass conversion)
    "phosphoric acid": 1.685,
    "sulfuric acid": 1.84,
    "nitric acid": 1.41,
    "acetic acid": 1.05,
}

# Powder Chemicals (Mass in Kilograms)
POWDER_MASSES = {
    "SLS powder(KG)": 20.0,  # 20 KG per bag
}

# Combine all chemicals for iteration
ALL_CHEMICALS = {**LIQUID_WEIGHTS, **POWDER_MASSES}

# --- HARDCODED FORMULA CONSTANTS ---
# Fixed concentration percentages (hidden from user)
FIXED_FACTOR_PHOS_1 = 10.0
FIXED_FACTOR_SULF_1 = 10.0
FIXED_FACTOR_NITR_1 = 10.0
FIXED_FACTOR_ACET_1 = 10.0

FIXED_FACTOR_PHOS_2 = 4.0
FIXED_FACTOR_NITR_2 = 1.2
FIXED_FACTOR_SLS_2 = 1.0

# --- 1. Current Stock Input ---

st.header("1. Current Chemical Inventory")
st.write("Enter the number of full containers currently in stock.")

# Create dictionaries to hold user input and total stock
bucket_input = {}
available_stock = {}  # This will hold mass (KG) for ALL products

with st.container(border=True):
    # --- Liquid Input ---
    st.subheader("Liquid Products (Buckets)")
    cols_l = st.columns(len(LIQUID_WEIGHTS))

    i = 0
    for chemical, weight in LIQUID_WEIGHTS.items():
        with cols_l[i]:
            bucket_input[chemical] = st.number_input(
                f"**{chemical}** (Buckets)",
                min_value=0,
                value=0,
                step=1,
                help=f"Each bucket weighs {weight} KG",  # Updated help text
                key=f'stock_{chemical}'
            )
        # Calculate available stock in KG (Mass available)
        available_stock[chemical] = bucket_input[chemical] * LIQUID_WEIGHTS[chemical]
        i += 1

with st.container(border=True):
    # --- Powder Input ---
    st.subheader("Powder Products (Bags)")
    cols_p = st.columns(len(POWDER_MASSES))

    j = 0
    for chemical, mass in POWDER_MASSES.items():
        with cols_p[j]:
            bucket_input[chemical] = st.number_input(
                f"**{chemical}** (KG)",
                min_value=0,
                value=0,
                step=1,
                help=f"Each bag is {mass} KG",
                key=f'stock_{chemical}'
            )
        # Calculate available stock in KG (Mass available)
        available_stock[chemical] = bucket_input[chemical] * POWDER_MASSES[chemical]
        j += 1

# Display the calculated total stock
st.subheader("Total Available Chemical Stock")
stock_df = pd.DataFrame(
    available_stock.items(),
    columns=['Chemical Product', 'Available Stock']
)

# Unit is KG for ALL chemicals now
stock_df['Unit'] = 'KG'
stock_df = stock_df.set_index('Chemical Product')

st.dataframe(stock_df, use_container_width=True)

st.markdown("---")

# --- 2. Required Solution Volumes ---

# Initialize required_volume using ALL_CHEMICALS.
# NOTE: This dict stores L required for liquids and KG required for powders.
required_volume = {chem: 0.0 for chem in ALL_CHEMICALS}

st.header("2. Required Solution Volumes")
st.write("Calculate the volume/mass of chemicals needed for your two different solutions.")

# --- Solution 1 Calculation (Etching) ---
with st.expander("Calculate Needs for **Solution 1 (Etching Recipe)**", expanded=True):
    batch_size_1 = st.number_input(
        "Enter the **Total Volume of Solution 1** to be prepared (L):",
        min_value=0.0,
        value=100.0,
        key='batch_1',
        help="This is the total volume of the finished solution batch."
    )

    # Calculation based on fixed factors (Liters needed for this solution)
    needed_phos_1 = batch_size_1 * (FIXED_FACTOR_PHOS_1 / 100)
    needed_sulf_1 = batch_size_1 * (FIXED_FACTOR_SULF_1 / 100)
    needed_nitr_1 = batch_size_1 * (FIXED_FACTOR_NITR_1 / 100)
    needed_acet_1 = batch_size_1 * (FIXED_FACTOR_ACET_1 / 100)

    st.markdown("##### Chemical Requirements (L)")
    st.markdown(f"**Phosphoric Acid Required:** `{needed_phos_1:,.2f} L`")
    st.markdown(f"**Sulfuric Acid Required:** `{needed_sulf_1:,.2f} L`")
    st.markdown(f"**Nitric Acid Required:** `{needed_nitr_1:,.2f} L`")
    st.markdown(f"**Acetic Acid Required:** `{needed_acet_1:,.2f} L`")

    # Accumulate the total required volume
    required_volume["phosphoric acid"] += needed_phos_1
    required_volume["sulfuric acid"] += needed_sulf_1
    required_volume["nitric acid"] += needed_nitr_1
    required_volume["acetic acid"] += needed_acet_1

# --- Solution 2 Calculation ---
with st.expander("Calculate Needs for **Solution 2**"):
    batch_size_2 = st.number_input(
        "Enter the **Total Volume of Solution 2** to be prepared (L):",
        min_value=0.0,
        value=50.0,
        key='batch_2',
        help="This is the total volume of the finished solution batch."
    )

    # Calculation based on fixed factors
    # Liquids (Liters needed)
    needed_phos_2 = batch_size_2 * (FIXED_FACTOR_PHOS_2 / 100)
    needed_nitr_2 = batch_size_2 * (FIXED_FACTOR_NITR_2 / 100)

    # Powder (Kilograms needed) - Assumes factor is KG/100L
    needed_sls_2 = batch_size_2 * (FIXED_FACTOR_SLS_2 / 100)

    st.markdown("##### Chemical Requirements")
    st.markdown(f"**Phosphoric Acid Required:** `{needed_phos_2:,.2f} L`")
    st.markdown(f"**Nitric Acid Required:** `{needed_nitr_2:,.2f} L`")
    st.markdown(f"**SLS Powder(KG) Required:** `{needed_sls_2:,.2f} KG`")

    # Accumulate the total required volume/mass
    required_volume["phosphoric acid"] += needed_phos_2
    required_volume["nitric acid"] += needed_nitr_2
    required_volume["SLS powder(KG)"] += needed_sls_2

st.markdown("---")

# Display the overall total required volume/mass (before comparison)
# Note: For liquids, this still shows the total Liters required.
st.subheader("Total Required for All Solutions (Liters/Kilograms)")
required_display_df = pd.DataFrame(
    required_volume.items(),
    columns=['Chemical Product', 'Total Required']
).set_index('Chemical Product')

# Add a unit column for display clarity (L for liquids, KG for powder)
required_display_df['Unit'] = required_display_df.index.to_series().apply(
    lambda x: 'KG' if x in POWDER_MASSES else 'L'
)
st.dataframe(required_display_df, use_container_width=True)

st.markdown("---")

# --- 3. Inventory Needs Assessment ---

st.header("3. Inventory Needs Assessment")
st.info("Compares total required mass (KG) with current stock (KG) to determine purchasing needs.")

results_list = []
for chemical in ALL_CHEMICALS:
    available_mass = available_stock.get(chemical, 0.0)
    required_liters_or_kg = required_volume.get(chemical, 0.0)

    is_liquid = chemical in LIQUID_WEIGHTS
    unit = 'KG'  # The unit of comparison and purchase is KG for all products

    # CONVERSION: Convert required Liters to required Kilograms for liquids
    if is_liquid:
        # Use the correct, fixed density provided by the user
        density = LIQUID_DENSITIES[chemical]
        required_mass = required_liters_or_kg * density
    else:  # Powder
        required_mass = required_liters_or_kg

        # Comparison and calculation done entirely in KG
    difference = available_mass - required_mass

    if difference < 0:
        needed_to_buy = abs(difference)
        status_icon = "❌"
    else:
        needed_to_buy = 0.0
        status_icon = "✅"

    status = f"{status_icon} Surplus of {difference:,.2f} {unit}" if difference >= 0 else f"{status_icon} Deficit of {abs(difference):,.2f} {unit}"

    results_list.append({
        'Chemical': chemical,
        'Available Mass': f"{available_mass:,.2f} {unit}",
        'Required Mass': f"{required_mass:,.2f} {unit}",
        'Status/Action': status,
        'Amount To Buy (Deficit)': needed_to_buy,
        'Type': 'Liquid' if is_liquid else 'Powder'
    })

comparison_df = pd.DataFrame(results_list).set_index('Chemical')

# --- Display Results ---
st.subheader("Comparison Summary (All units in KG)")
st.dataframe(comparison_df[['Available Mass', 'Required Mass', 'Status/Action']], use_container_width=True)

st.subheader("🛒 Purchasing List")
# Filter to only show chemicals that need to be bought
purchase_list_df = comparison_df[comparison_df['Amount To Buy (Deficit)'] > 0].copy()

if purchase_list_df.empty:
    st.success("✅ You have enough stock for all products! No purchases necessary.")
else:
    st.error("⚠️ The following products need to be purchased to meet all solution requirements.")

    st.markdown("---")

    # --- Liquid Products Purchase ---
    liquid_to_buy = purchase_list_df[purchase_list_df['Type'] == 'Liquid']
    if not liquid_to_buy.empty:
        st.markdown("#### Liquid Products (Buckets)")

        liquid_purchase_data = []
        for chem in liquid_to_buy.index:
            kg_per_bucket = LIQUID_WEIGHTS[chem]
            amount_to_buy_kg = liquid_to_buy.loc[chem, 'Amount To Buy (Deficit)']
            # Calculate the number of buckets needed (using np.ceil to round up)
            buckets_to_buy = np.ceil(amount_to_buy_kg / kg_per_bucket).astype(int)

            liquid_purchase_data.append({
                'Chemical': chem,
                'Deficit (KG)': f"{amount_to_buy_kg:,.2f} KG",
                'Buckets to Buy': buckets_to_buy,
            })

        liquid_purchase_df_final = pd.DataFrame(liquid_purchase_data).set_index('Chemical')
        st.dataframe(liquid_purchase_df_final, use_container_width=True)

    # --- Powder Products Purchase ---
    powder_to_buy = purchase_list_df[purchase_list_df['Type'] == 'Powder']
    if not powder_to_buy.empty:
        st.markdown("#### Powder Products (Bags)")

        # We need the KG per bag for the powder chemical:
        powder_chem_name = list(POWDER_MASSES.keys())[0]
        kg_per_bag = POWDER_MASSES[powder_chem_name]

        # Calculate the number of bags needed (using np.ceil to round up)
        powder_to_buy['Bags to Buy'] = (
                powder_to_buy['Amount To Buy (Deficit)'] / kg_per_bag
        ).apply(np.ceil).astype(int)

        powder_display_df = powder_to_buy.rename(
            columns={'Amount To Buy (Deficit)': 'Deficit (KG)'}
        )[['Deficit (KG)', 'Bags to Buy']]

        st.dataframe(powder_display_df, use_container_width=True)

st.markdown("---")
st.caption("Application powered by Streamlit.")
st.caption("Application made for KORTOBA ALUMINIUM.")


