import streamlit as st
import locale
from datetime import date

# Page configuration
st.set_page_config(
    page_title="Port Charges Calculator",
    page_icon="⚓",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 8px 0;
    }
    .charge-item {
        padding: 5px 0;
        border-bottom: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Constants
shf = 119
clf = 12
cvf = 140
tsf = 65
ihf = 140
ecf = 150000
sht = 79
clt = 6
cvt = 70
tst = 65
iht = 90
ect = 75000

def format_currency_with_commas(amount, currency_symbol='$'):
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        locale.setlocale(locale.LC_ALL, '')
    
    try:
        formatted_amount = locale.currency(amount, symbol=currency_symbol, grouping=True)
        return formatted_amount
    except:
        return f"{currency_symbol}{amount:,.2f}"

def count_days_between_dates(start_date, end_date):
    delta = end_date - start_date
    return delta.days + 1  # Add 1 to include both start and end dates

def calculate_air_charges(weight, is_dg, carry_in_date, carry_out_date, shipment_type):
    d0 = count_days_between_dates(carry_in_date, carry_out_date)
    
    # Equipment charges based on weight
    if weight < 33:
        eq = 0
    elif 33 <= weight <= 50:
        eq = 10.5
    elif 51 <= weight <= 500:
        eq = 26
    elif 501 <= weight <= 5000:
        eq = 67
    elif 5001 <= weight <= 9999:
        eq = 115
    else:  # weight >= 10000
        eq = 432

    # Handling and storage charges
    if is_dg == "DG":
        han = 0.185 * weight
        if han < 40:
            han = 40
        sto = 0.1854 * weight * d0
        if sto < 40:
            sto = 40
    else:  # NOT DG
        han = 0.085 * weight
        if han < 22:
            han = 22
        if d0 < 3:
            sto = 0
        else:
            sto = 0.0515 * weight * (d0 - 3)
            if sto < 20:
                sto = 20

    # Other charges
    DDT = 2
    TAA = 0.04 * weight
    sec = 0.025 * weight
    if sec < 5:
        sec = 5
    
    # Documentation charges
    if shipment_type == "MAWB":
        no = 1
        doc = 20
        bre = 0
    else:  # CONSO
        no = 1
        doc = 0
        bre = 78

    tot = ((DDT + doc + eq + han + no + sec + sto) * 1.18) + TAA

    charges = {
        "Tanzania Airport Authority (TAA)": TAA,
        "Data Discharge Tancis": DDT,
        "Documentation": doc,
        "Equipment Charges": eq,
        "Handling Charges": han,
        "Notification Charges": no,
        "General Cargo Storage": sto,
        "Security Surcharges": sec,
        "Break Bulk Charges": bre,
        "Total Swissport Charges": tot
    }
    
    return charges, d0

def calculate_lcl_charges(cbm, carry_in_date, carry_out_date):
    d0 = count_days_between_dates(carry_in_date, carry_out_date)
    
    if d0 <= 5:
        d1 = 0
        stl = d1 * cbm * 1
        cwl = 0.3 * cbm
        shl = 7 * cbm
        stp = 5.3 * cbm
        rcl = 0
        cwt = 0
    else:
        d1 = d0 - 5
        stl = d1 * cbm * 1
        cwl = 0.3 * cbm
        shl = 7 * cbm
        stp = 5.3 * cbm
        rcl = 2 * cbm
        if d1 < 21:
            cwt = 0
        else:
            cwt = 0.33 * cbm * (d1 - 14)

    tot = ((stl + cwl + shl + stp + rcl) * 1.18)

    charges = {
        "Storage Charges": stl,
        "Corridor Levy Charges": cwl,
        "Removal Charges": rcl,
        "Shore Handling Charges": shl,
        "Stripping Charges": stp,
        "Customs Warehouse Rent": cwt,
        "Port and ICD Charges for LCL shipment": tot
    }
    
    return charges, d0

def calculate_20ft_charges(containers, carry_in_date, carry_out_date):
    d0 = count_days_between_dates(carry_in_date, carry_out_date)
    
    if d0 <= 5:
        stt = 0
        cwt = 0
        rct = 0
    elif d0 <= 15:
        d3 = d0 - 5
        dr = (d3 * 20) * 1.18
        stt = dr * containers
        cwt = 0
        rct = (100 * containers) * 1.18
    else:
        d4 = d0 - 5
        df = d4 - 10
        d5 = (10 * 20) * 1.18
        d6 = (df * 40) * 1.18
        d7 = d5 + d6
        stt = d7 * containers
        rct = (100 * containers) * 1.18
        if d0 > 21:
            cwt = (0.33 * 36 * (d0 - 14)) * containers
        else:
            cwt = 0

    # Fixed charges
    s = sht * containers
    c = clt * containers
    cv = cvt * containers
    i = iht * containers
    t = tst * containers
    e = ect * containers
    sam = (s + c + cv + i + t) * 1.18
    tot = sam + stt + rct

    charges = {
        "Storage Charges": stt,
        "Removal Charges": rct,
        "Shore Handling Charges": s,
        "Customs Verification Charges": cv,
        "Corridor Levy Charges": c,
        "ICD Handling Charges": i,
        "Container Transfer Charges": t,
        "Customs Warehouse Rent Charges": cwt,
        "Port and ICD Charges for 20FT Container": tot
    }
    
    return charges, d0

def calculate_40ft_charges(containers, carry_in_date, carry_out_date):
    d0 = count_days_between_dates(carry_in_date, carry_out_date)
    
    if d0 <= 5:
        stf = 0
        cwf = 0
        rcf = 0
    elif d0 <= 15:
        d3 = d0 - 5
        dr = (d3 * 40) * 1.18
        stf = dr * containers
        cwf = 0
        rcf = (150 * containers) * 1.18
    else:
        d4 = d0 - 5
        df = d4 - 10
        d5 = (10 * 40) * 1.18
        d6 = (df * 80) * 1.18
        d7 = d5 + d6
        stf = d7 * containers
        rcf = (150 * containers) * 1.18
        if d0 > 21:
            cwf = (0.33 * 72 * (d0 - 21)) * containers
        else:
            cwf = 0

    # Fixed charges
    s = shf * containers
    c = clf * containers
    cv = cvf * containers
    i = ihf * containers
    t = tsf * containers
    e = ecf * containers
    sam = (s + c + cv + i + t) * 1.18
    tot = sam + stf + rcf

    charges = {
        "Storage Charges": stf,
        "Removal Charges": rcf,
        "Shore Handling Charges": s,
        "Customs Verification Charges": cv,
        "Corridor Levy Charges": c,
        "ICD Handling Charges": i,
        "Container Transfer Charges": t,
        "Customs Warehouse Rent Charges": cwf,
        "Port and ICD Charges for 40FT Container": tot
    }
    
    return charges, d0

# Main app
st.markdown('<div class="main-header">⚓ Port Charges Calculator</div>', unsafe_allow_html=True)

# Shipment type selection
shipment_type = st.selectbox(
    "Select Shipment Type",
    ["AIR", "LCL", "20FT", "40FT"],
    help="Choose the type of sea shipment"
)

# Date inputs
st.subheader("📅 Storage Period")
col1, col2 = st.columns(2)
with col1:
    carry_in_date = st.date_input("Carry-in Date", value=date.today())
with col2:
    carry_out_date = st.date_input("Carry-out Date", value=date.today())

# Validate dates
if carry_out_date < carry_in_date:
    st.error("Carry-out date cannot be before carry-in date!")
else:
    # Shipment-specific inputs
    if shipment_type == "AIR":
        st.subheader("✈️ Air Cargo Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            weight = st.number_input("Cargo Weight (kg)", min_value=0.1, value=100.0, step=0.1)
        with col2:
            is_dg = st.radio("Cargo Type", ["DG", "NOT"])
        with col3:
            air_shipment_type = st.radio("Shipment Type", ["MAWB", "CONSO"])
        
        if st.button("Calculate Air Charges", type="primary"):
            charges, days = calculate_air_charges(weight, is_dg, carry_in_date, carry_out_date, air_shipment_type)
            
            st.success(f"✅ Calculation Complete! Storage period: {days} days")
            st.subheader("💰 Charge Breakdown")
            
            for charge_name, amount in charges.items():
                st.markdown(f'<div class="result-box"><strong>{charge_name}:</strong> {format_currency_with_commas(amount)}</div>', unsafe_allow_html=True)

    elif shipment_type == "LCL":
        st.subheader("📦 LCL Shipment Details")
        cbm = st.number_input("CBM (Cubic Meters)", min_value=0.1, value=10.0, step=0.1)
        
        if st.button("Calculate LCL Charges", type="primary"):
            charges, days = calculate_lcl_charges(cbm, carry_in_date, carry_out_date)
            
            st.success(f"✅ Calculation Complete! Storage period: {days} days")
            st.subheader("💰 Charge Breakdown")
            
            for charge_name, amount in charges.items():
                st.markdown(f'<div class="result-box"><strong>{charge_name}:</strong> {format_currency_with_commas(amount)}</div>', unsafe_allow_html=True)

    elif shipment_type == "20FT":
        st.subheader("📦 20FT Container Details")
        containers = st.number_input("Number of Containers", min_value=1, value=1, step=1)
        
        if st.button("Calculate 20FT Charges", type="primary"):
            charges, days = calculate_20ft_charges(containers, carry_in_date, carry_out_date)
            
            st.success(f"✅ Calculation Complete! Storage period: {days} days")
            st.subheader("💰 Charge Breakdown")
            
            for charge_name, amount in charges.items():
                st.markdown(f'<div class="result-box"><strong>{charge_name}:</strong> {format_currency_with_commas(amount)}</div>', unsafe_allow_html=True)

    elif shipment_type == "40FT":
        st.subheader("📦 40FT Container Details")
        containers = st.number_input("Number of Containers", min_value=1, value=1, step=1)
        
        if st.button("Calculate 40FT Charges", type="primary"):
            charges, days = calculate_40ft_charges(containers, carry_in_date, carry_out_date)
            
            st.success(f"✅ Calculation Complete! Storage period: {days} days")
            st.subheader("💰 Charge Breakdown")
            
            for charge_name, amount in charges.items():
                st.markdown(f'<div class="result-box"><strong>{charge_name}:</strong> {format_currency_with_commas(amount)}</div>', unsafe_allow_html=True)

# Instructions
st.markdown("---")
st.info("💡 **Instructions:** Select shipment type, enter dates and required details, then click the calculate button to see the charge breakdown.")