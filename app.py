import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime
import folium
from streamlit_folium import st_folium

# --- CONFIGURATION & DATABASE SETUP ---
st.set_page_config(page_title="Chennai Logistics Aggregator", layout="wide")
DB_FILE = "logistics_db.json"

# --- 🚀 CUSTOM BRANDING DESIGN & FINTECH TIMELINE CSS ---
st.markdown("""
    <style>
        .stApp { background-color: #0d1117; }
        .stApp, .stMarkdown, p, span, div, .stText { color: #ecf2f8 !important; }
        label, [data-testid="stWidgetLabel"] p { color: #ecf2f8 !important; font-weight: 600 !important; }
        h1, h2, h3, [data-testid="stHeader"] { color: #00FFCC !important; font-family: 'Courier New', Courier, monospace; font-weight: 700; }
        .stDataFrame div, table, th, td, [data-testid="stTable"] { color: #ecf2f8 !important; background-color: #161b22 !important; }
        .streamlit-expanderHeader { background-color: #161b22 !important; border: 1px solid #30363d !important; border-radius: 8px !important; color: #00FFCC !important; }
        
        /* Unified Tracking & Payment Card Shadowing */
        div[data-testid="stMetricBlock"] {
            background-color: #161b22;
            border: 1px solid #30363d;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 4px 12px rgba(0, 255, 204, 0.05);
        }
        div[data-testid="stMetricBlock"] [data-testid="stMetricLabel"] p { color: #8b949e !important; }
        
        .stButton>button {
            background-color: #1f242c !important;
            color: #00FFCC !important;
            border: 1px solid #00FFCC !important;
            border-radius: 6px !important;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #00FFCC !important;
            color: #0d1117 !important;
            box-shadow: 0 0 10px #00FFCC;
        }
    </style>
""", unsafe_allow_html=True)

default_operators = [
    {"id": 1, "name": "Muthu Chennai Fast Freight", "vehicle": "Tata Ace (Van)", "capacity": 850, "status": "Available", "rate_per_km": 30, "wallet_balance": 4500},
    {"id": 2, "name": "Annamalai Local Couriers", "vehicle": "Two-Wheeler", "capacity": 30, "status": "Available", "rate_per_km": 12, "wallet_balance": 1200},
    {"id": 3, "name": "Koyambedu Market Bulk Transport", "vehicle": "Eicher Pro (Truck)", "capacity": 4000, "status": "Busy", "rate_per_km": 65, "wallet_balance": 18200}
]

if not os.path.exists(DB_FILE):
    initial_data = {
        "operators": default_operators,
        "producer_wallet": 25000,
        "shipments": [
            {
                "id": "TRK-CH101",
                "cargo": "Fresh Tomatoes",
                "weight": 500,
                "pickup": "Koyambedu Wholesale Market",
                "destination": "Tambaram Delivery Hub",
                "operator": "Muthu Chennai Fast Freight",
                "status": "In Transit",
                "distance": 24,
                "fare": 720,
                "gate_queue": 0,
                "is_split": False,
                "child_trips": [],
                "payment_status": "Paid (In Escrow)"
            }
        ]
    }
    with open(DB_FILE, "w") as f:
        json.dump(initial_data, f, indent=4)

def load_data():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# Check fields migration to clear errors
if "producer_wallet" not in data: data["producer_wallet"] = 25000
for op in data["operators"]:
    if "wallet_balance" not in op: op["wallet_balance"] = 5000
    if "rate_per_km" not in op: op["rate_per_km"] = 30
    if "capacity" not in op: op["capacity"] = 1000
save_data(data)

HUB_COORDINATES = {
    "koyambedu": [13.0692, 80.1948], "tambaram": [12.9229, 80.1275], "madhavaram": [13.1068, 80.2184],
    "guindy": [13.0067, 80.2206], "sriperumbudur": [12.9724, 79.9515], "t. nagar (alley 1)": [13.0324, 80.2337],
    "sowcarpet (alley 2)": [13.0978, 80.2792], "parrys (alley 3)": [13.0945, 80.2891]
}

def create_satellite_map(center_coords, zoom=11):
    sat_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    labels_url = "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}"
    m = folium.Map(location=center_coords, zoom_start=zoom, tiles=sat_url, attr="Esri")
    folium.TileLayer(tiles=labels_url, attr="Esri Labels", name="Road Labels", overlay=True, control=False).add_to(m)
    folium.Circle(location=[13.04, 80.22], radius=12000, color="#00FFCC", fill=True, fill_color="#00FFCC", fill_opacity=0.05).add_to(m)
    return m

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚚 Chennai Logistics Hub")
st.sidebar.markdown("Select your portal view below:")
user_role = st.sidebar.radio("Go To View:", ["🌾 Producer Portal", "🚛 Operator Portal", "📦 Consumer Tracking"])

# --- 1. PRODUCER PORTAL ---
if user_role == "🌾 Producer Portal":
    st.title("🌾 Producer Dashboard & Unified Freight Ledgers")
    
    # Header Balance Counters
    c_w1, c_w2 = st.columns(2)
    with c_w1: st.metric(label="🛡️ Shippers Available Balance", value=f"₹{data['producer_wallet']:,}")
    with c_w2:
        escrow_sum = sum(s["fare"] for s in data["shipments"] if s["payment_status"] == "Paid (In Escrow)")
        st.metric(label="🔒 Total Freight Value Locked in Route Escrow", value=f"₹{escrow_sum:,}")
        
    col1, col2, col3 = st.columns([1.2, 1.3, 1.5])
    
    with col1:
        active_backhauls = [op for op in data["operators"] if op["status"].startswith("Empty Backhaul:")]
        if active_backhauls:
            st.markdown("### 🌟 30% Backhaul Price Match Detected!")
            for b_op in active_backhauls:
                route_info = b_op["status"].replace("Empty Backhaul:", "")
                st.warning(f"🚛 {b_op['name']} Empty Return: **{route_info}**")
                if st.button(f"Fund & Claim Backhaul Route", key=f"bh_claim_{b_op['id']}"):
                    try:
                        b_pickup, b_dest = route_info.split("➡️")
                        b_pickup, b_dest = b_pickup.strip(), b_dest.strip()
                    except:
                        b_pickup, b_dest = "Tambaram Delivery Hub", "Koyambedu Wholesale Market"
                    
                    mock_distance = random.randint(15, 30)
                    discounted_fare = int((mock_distance * b_op.get("rate_per_km", 25)) * 0.70)
                    
                    if data["producer_wallet"] >= discounted_fare:
                        data["producer_wallet"] -= discounted_fare
                        shipment_id = f"TRK-BH-{int(datetime.now().timestamp())}"
                        new_shipment = {
                            "id": shipment_id, "cargo": "Discounted Backhaul Produce", "weight": int(b_op["capacity"] * 0.8),
                            "pickup": b_pickup, "destination": b_dest, "operator": b_op["name"], "status": "Assigned",
                            "distance": mock_distance, "fare": discounted_fare, "gate_queue": 0, "is_split": False, "child_trips": [],
                            "payment_status": "Paid (In Escrow)"
                        }
                        data["shipments"].append(new_shipment)
                        b_op["status"] = "Busy"
                        save_data(data); st.success("💰 Escrow Funded! Tracking ID active."); st.rerun()
            st.markdown("---")

        st.markdown("### Book Freight & Fund Route Escrow")
        with st.form("delivery_form", clear_on_submit=True):
            cargo = st.text_input("Goods Type")
            weight = st.number_input("Total Load Weight (kg)", min_value=1, value=100)
            pickup = st.text_input("Pickup Hub (e.g., Koyambedu)")
            destination = st.text_input("Drop Destination (e.g., Tambaram)")
            submit = st.form_submit_button("Authorize Escrow & Match Driver")
            
            if submit and cargo and pickup and destination:
                available_ops = [op for op in data["operators"] if op["status"] == "Available" and op["capacity"] >= weight]
                if available_ops:
                    best_op = min(available_ops, key=lambda x: x["capacity"])
                    mock_distance = random.randint(12, 45)
                    calculated_fare = mock_distance * best_op.get("rate_per_km", 20)
                    
                    if data["producer_wallet"] >= calculated_fare:
                        data["producer_wallet"] -= calculated_fare
                        shipment_id = f"TRK-{int(datetime.now().timestamp())}"
                        new_shipment = {
                            "id": shipment_id, "cargo": cargo, "weight": weight, "pickup": pickup, "destination": destination,
                            "operator": best_op["name"], "status": "Assigned", "distance": mock_distance, "fare": calculated_fare,
                            "gate_queue": 0, "is_split": False, "child_trips": [], "payment_status": "Paid (In Escrow)"
                        }
                        data["shipments"].append(new_shipment)
                        best_op["status"] = "Busy"
                        save_data(data); st.success(f"🎉 Escrow Secured! ID: {shipment_id}"); st.rerun()
                    else:
                        st.error("❌ Balance insufficient to clear driver escrow route costs.")

    with col2:
        st.markdown("### Unified Tracker & Payment Stream")
        if not data["shipments"]:
            st.info("No shipments active on network log.")
        else:
            for s in reversed(data["shipments"]):
                with st.expander(f"📦 {s['cargo']} [ID: {s['id']}]"):
                    st.write(f"**Route Corridor:** {s['pickup']} ➡️ {s['destination']}")
                    st.write(f"**Carrier Fleet Partner:** {s['operator']}")
                    
                    # LAYERED REAL-TIME PAYMENTS + TRACKING ENGINE INFUSION
                    st.markdown("---")
                    st.markdown(f"💰 **Financial Ledger:** ₹{s['fare']} &rarr; `{s['payment_status']}`")
                    
                    if s.get("is_split"):
                        st.info("⚡ **Multi-Modal Last Mile Hand-off Active**")
                        for child in s["child_trips"]:
                            st.write(f"🛵 {child['runner']} &rarr; `{child['status']}` ({child['loc']})")
                    else:
                        status = s["status"]
                        if status == "Stuck at Gate Queue":
                            st.warning(f"⚠️ **Gate Queue Delays Active:** Vehicle token position #{s.get('gate_queue', 12)}")
                        else:
                            if status == "Assigned": st.progress(25, text="Milestone 1/4: Escrow Funded & Driver Booked")
                            elif status == "Picked Up": st.progress(50, text="Milestone 2/4: Cargo Loaded at Source")
                            elif status == "In Transit": st.progress(75, text="Milestone 3/4: Fleet Vector En Route")
                            elif status == "Delivered": st.progress(100, text="Milestone 4/4: Dispatched & Payout Settled ✅")

    with col3:
        st.markdown("### 🗺️ Live Hybrid Hub Tracker")
        m_prod = create_satellite_map([13.0827, 80.2707], zoom=10)
        for key, coord in HUB_COORDINATES.items():
            folium.Marker(coord, popup=f"Terminal Hub: {key.upper()}").add_to(m_prod)
        st_folium(m_prod, width="100%", height=450, key="prod_map", returned_objects=[])

# --- 2. OPERATOR PORTAL ---
elif user_role == "🚛 Operator Portal":
    st.title("🚛 Fleet Control Manifest & Settlement Console")
    
    col1, col2, col3 = st.columns([1.1, 1.4, 1.5])
    
    with col1:
        st.markdown("### Registered Driver Wallet Ledgers")
        for op in data["operators"]:
            st.markdown(f"**{op['name']}**")
            st.code(f"Class: {op['vehicle']} | Certified Balance: ₹{op['wallet_balance']:,}")
            st.markdown("---")

    with col2:
        st.markdown("### Unified Logistics & Payout Disbursal Pipeline")
        active_jobs = [s for s in data["shipments"] if s["status"] != "Delivered"]
        
        if not active_jobs:
            st.info("No active freights waiting action items.")
        else:
            for s in active_jobs:
                st.markdown(f"📦 **{s['cargo']}** | Escrow Vault Value: **₹{s['fare']}**")
                current_state = s["status"]
                
                if not s.get("is_split"):
                    if current_state == "Assigned":
                        if st.button(f"Confirm Pickup (ID: {s['id']})", key=f"pk_{s['id']}", use_container_width=True):
                            s["status"] = "Picked Up"; save_data(data); st.rerun()
                    elif current_state == "Picked Up":
                        if st.button(f"Mark In Transit (ID: {s['id']})", key=f"it_{s['id']}", use_container_width=True):
                            s["status"] = "In Transit"; save_data(data); st.rerun()
                    elif current_state == "In Transit":
                        if st.button(f"🚨 Flag Market Gate Hold (ID: {s['id']})", key=f"stk_{s['id']}", use_container_width=True):
                            s["status"] = "Stuck at Gate Queue"; s["gate_queue"] = random.randint(8, 22); save_data(data); st.rerun()
                        
                        if st.button(f"⚡ Hand-off Last Mile to Bike Fleet", key=f"splt_{s['id']}", use_container_width=True):
                            s["is_split"] = True; s["status"] = "Split Delivery Last-Mile"
                            dest_clean = s["destination"].lower()
                            loc_name = "T. Nagar (Alley 1)" if "nagar" in dest_clean else ("Sowcarpet (Alley 2)" if "sowcarpet" in dest_clean else "Parrys (Alley 3)")
                            s["child_trips"] = [
                                {"runner": "Bike Agent A", "status": "Out for Delivery", "loc": loc_name},
                                {"runner": "Bike Agent B", "status": "Out for Delivery", "loc": loc_name}
                            ]
                            save_data(data); st.rerun()
                        
                        # UNIFIED TRANSIT COMPLETION + FINANCIAL ESCROW DISBURSAL ACTION
                        if st.button(f"✅ Confirm Dropoff & Disburse Escrow Funds (ID: {s['id']})", key=f"bh_pub_{s['id']}", use_container_width=True):
                            s["status"] = "Delivered"
                            s["payment_status"] = "Released to Operator"
                            for op in data["operators"]:
                                if op["name"] == s["operator"]:
                                    op["wallet_balance"] += s["fare"]
                                    op["status"] = f"Empty Backhaul: {s['destination']} ➡️ {s['pickup']}"
                            save_data(data); st.rerun()
                            
                    elif current_state == "Stuck at Gate Queue":
                        if st.button(f"✅ Clear Token Yard & Disburse Escrow Funds (ID: {s['id']})", key=f"clr_{s['id']}", use_container_width=True):
                            s["status"] = "Delivered"
                            s["payment_status"] = "Released to Operator"
                            s["gate_queue"] = 0
                            for op in data["operators"]:
                                if op["name"] == s["operator"]:
                                    op["wallet_balance"] += s["fare"]
                                    op["status"] = f"Empty Backhaul: {s['destination']} ➡️ {s['pickup']}"
                            save_data(data); st.rerun()
                else:
                    st.success("⚡ Split Flow Active: Managing Bike Fleet")
                    if st.button(f"🏁 Finalize Bike Runs & Release Escrow Payout (ID: {s['id']})", key=f"fnbk_{s['id']}", use_container_width=True):
                        s["status"] = "Delivered"
                        s["payment_status"] = "Released to Operator"
                        for op in data["operators"]:
                            if op["name"] == s["operator"]:
                                op["wallet_balance"] += s["fare"]
                                op["status"] = "Available"
                        save_data(data); st.rerun()

    with col3:
        st.markdown("### 🗺️ Operational Dispatch Console")
        m_op = create_satellite_map([13.0827, 80.2707], zoom=11)
        for job in active_jobs:
            coords = HUB_COORDINATES["koyambedu"]
            for key in HUB_COORDINATES:
                if key in job["pickup"].lower() or key in job["destination"].lower(): coords = HUB_COORDINATES[key]
            folium.Marker(coords, popup=f"{job['cargo']} - Escrow: ₹{job['fare']}").add_to(m_op)
        st_folium(m_op, width="100%", height=450, key="op_map", returned_objects=[])

# --- 3. CONSUMER TRACKING ---
elif user_role == "📦 Consumer Tracking":
    st.title("📦 Consignment Quick Status Portal")
    col_input, col_map = st.columns([1, 1])
    
    with col_input:
        st.markdown("### Enter your Tracking ID:")
        search_id = st.text_input("Tracking Reference Number", placeholder="e.g., TRK-CH101")
        
        if search_id:
            match_found = next((s for s in data["shipments"] if s["id"] == search_id), None)
            if match_found:
                # UNIFIED DISPLAY CARD
                st.success(f"Consignment Verified: **{match_found['cargo']}**")
                
                # Layered FinTech Audit Badge
                if match_found["payment_status"] == "Released to Operator":
                    st.markdown("🟢 **Financial Audit Ledger:** `PAYMENT CLEARANCE DISBURSED TO DRIVER WALLET`")
                else:
                    st.markdown("🟡 **Financial Audit Ledger:** `ESCROW RETAINED SECURE IN PLATFORM HOLD`")
                
                st.write(f"**Route Manifest Corridor:** {match_found['pickup']} to {match_found['destination']}")
                st.write(f"**Total Invoiced Freight Booking Bill:** ₹{match_found['fare']}")
                
                status = match_found["status"]
                if status == "Delivered": 
                    st.progress(100, text="🏁 Step 4/4: Cargo Drop Complete & Escrow Fully Disbursed.")
                elif status == "Stuck at Gate Queue":
                    st.error("🚨 Step 3.5/4: Physical Delays Active at Terminal Entrance Unloading Yards.")
                    estimated_wait = match_found.get('gate_queue', 12) * 15
                    st.metric(label="Estimated Yard Delay Clearance Timer", value=f"{estimated_wait} Mins")
                else:
                    st.progress(50, text=f"Physical Transit State Tracker: `{status}`")
            else:
                st.error("Invalid tracking reference. Please verify the ID code.")
    
    with col_map:
        st.markdown("### Live Tactical Route Map")
        m_cust = create_satellite_map([13.0827, 80.2707], zoom=11)
        
        if search_id and 'match_found' in locals() and match_found:
            p_coord = HUB_COORDINATES["koyambedu"]
            d_coord = HUB_COORDINATES["tambaram"]
            for key in HUB_COORDINATES:
                if key in match_found["pickup"].lower(): p_coord = HUB_COORDINATES[key]
                if key in match_found["destination"].lower(): d_coord = HUB_COORDINATES[key]
                
            line_color = "#FF9900" if match_found["status"] == "Stuck at Gate Queue" else ("#00FFFF" if match_found.get("is_split") else "#FF00FF")
            folium.PolyLine(locations=[p_coord, d_coord], color=line_color, weight=6, opacity=0.9).add_to(m_cust)
            folium.Marker(p_coord, popup="SOURCE").add_to(m_cust)
            folium.Marker(d_coord, popup="DESTINATION").add_to(m_cust)

        st_folium(m_cust, width="100%", height=450, key="cust_map", returned_objects=[])
