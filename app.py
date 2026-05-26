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

default_operators = [
    {"id": 1, "name": "Muthu Chennai Fast Freight", "vehicle": "Tata Ace (Van)", "capacity": 850, "status": "Available", "rate_per_km": 30},
    {"id": 2, "name": "Annamalai Local Couriers", "vehicle": "Two-Wheeler", "capacity": 30, "status": "Available", "rate_per_km": 12},
    {"id": 3, "name": "Koyambedu Market Bulk Transport", "vehicle": "Eicher Pro (Truck)", "capacity": 4000, "status": "Busy", "rate_per_km": 65}
]

if not os.path.exists(DB_FILE):
    initial_data = {
        "operators": default_operators,
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
                "child_trips": []
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

# Clean up older databases on the fly to prevent KeyErrors
for op in data["operators"]:
    if "rate_per_km" not in op:
        op["rate_per_km"] = 12 if "Two-Wheeler" in op["vehicle"] else (30 if "Tata Ace" in op["vehicle"] else 65)

# Pre-defined coordinates for demo hubs
HUB_COORDINATES = {
    "koyambedu": [13.0692, 80.1948],
    "tambaram": [12.9229, 80.1275],
    "madhavaram": [13.1068, 80.2184],
    "guindy": [13.0067, 80.2206],
    "sriperumbudur": [12.9724, 79.9515],
    "t. nagar (alley 1)": [13.0324, 80.2337],
    "sowcarpet (alley 2)": [13.0978, 80.2792],
    "parrys (alley 3)": [13.0945, 80.2891]
}

# --- 🛰️ FREE HIGH-RES SATELLITE MAP CONFIGURATOR ---
def create_satellite_map(center_coords, zoom=11):
    # Pulls real-time aerospace imagery maps from Esri servers for free
    satellite_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    attribution = "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
    
    return folium.Map(
        location=center_coords,
        zoom_start=zoom,
        tiles=satellite_url,
        attr=attribution
    )

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚚 Chennai Logistics Hub")
st.sidebar.markdown("Select your portal view below:")
user_role = st.sidebar.radio("Go To View:", ["🌾 Producer Portal", "🚛 Operator Portal", "📦 Consumer Tracking"])

# --- 1. PRODUCER PORTAL ---
if user_role == "🌾 Producer Portal":
    st.title("🌾 Producer / Trader Dashboard")
    st.subheader("Book Shipments across Chennai & TN Hubs")
    
    col1, col2, col3 = st.columns([1.2, 1.3, 1.5])
    
    with col1:
        st.markdown("### Request Transport Match")
        with st.form("delivery_form", clear_on_submit=True):
            cargo = st.text_input("Goods / Produce Type", placeholder="e.g., Mangoes, Rice bags")
            weight = st.number_input("Total Load Weight (kg)", min_value=1, value=100)
            pickup = st.text_input("Pickup Location in Chennai", placeholder="e.g., Koyambedu, Madhavaram")
            destination = st.text_input("Drop Destination (Type 'T. Nagar' or 'Sowcarpet' for split demo)", placeholder="e.g., T. Nagar, Tambaram")
            submit = st.form_submit_button("Match with Local Operator")
            
            if submit and cargo and pickup and destination:
                available_ops = [op for op in data["operators"] if op["status"] == "Available" and op["capacity"] >= weight]
                
                if available_ops:
                    best_op = min(available_ops, key=lambda x: x["capacity"])
                    shipment_id = f"TRK-{int(datetime.now().timestamp())}"
                    
                    mock_distance = random.randint(12, 45)
                    calculated_fare = mock_distance * best_op.get("rate_per_km", 20)
                    
                    new_shipment = {
                        "id": shipment_id, "cargo": cargo, "weight": weight, "pickup": pickup, "destination": destination,
                        "operator": best_op["name"], "status": "Assigned", "distance": mock_distance, "fare": calculated_fare,
                        "gate_queue": 0, "is_split": False, "child_trips": []
                    }
                    data["shipments"].append(new_shipment)
                    for op in data["operators"]:
                        if op["name"] == best_op["name"]: op["status"] = "Busy"
                    save_data(data)
                    st.success(f"🎉 Matched with {best_op['name']}! ID: {shipment_id}")
                    st.rerun()

    with col2:
        st.markdown("### Active Consignment Tracker")
        if not data["shipments"]:
            st.info("No active shipments on the log right now.")
        else:
            for s in reversed(data["shipments"]):
                with st.expander(f"📦 {s['cargo']} -> ID: {s['id']}"):
                    st.write(f"**Route:** {s['pickup']} ➡️ {s['destination']}")
                    st.write(f"**Main Fleet Operator:** {s['operator']}")
                    
                    if s.get("is_split"):
                        st.info("⚡ **Multi-Modal Hub Hand-off Active!**")
                        for child in s["child_trips"]:
                            st.write(f"🛵 {child['runner']} ➡️ `{child['status']}` ({child['loc']})")
                    else:
                        status = s["status"]
                        if status == "Stuck at Gate Queue":
                            st.warning(f"⚠️ **Koyambedu Gate Hold Position:** #{s.get('gate_queue', 12)}")
                        else:
                            if status == "Assigned": st.progress(25, text="Step 1/4: Driver Booked")
                            elif status == "Picked Up": st.progress(50, text="Step 2/4: Loading Completed")
                            elif status == "In Transit": st.progress(75, text="Step 3/4: In Transit")
                            elif status == "Delivered": st.progress(100, text="Step 4/4: Delivered 🎉")

    with col3:
        st.markdown("### 🗺️ Aerospace Satellite Hub Network")
        m_prod = create_satellite_map([13.0827, 80.2707], zoom=10)
        for key, coord in HUB_COORDINATES.items():
            folium.Marker(coord, popup=f"Hub: {key.upper()}", icon=folium.Icon(color='green', icon='cloud')).add_to(m_prod)
        st_folium(m_prod, width="100%", height=450, key="prod_map", returned_objects=[])

# --- 2. OPERATOR PORTAL ---
elif user_role == "🚛 Operator Portal":
    st.title("🚛 Local Transporter Manifest Control")
    col1, col2, col3 = st.columns([1.1, 1.4, 1.5])
    
    with col1:
        st.markdown("### Registered Chennai Fleet")
        df_ops = pd.DataFrame(data["operators"])
        st.dataframe(df_ops[["name", "vehicle", "status"]], use_container_width=True, hide_index=True)

    with col2:
        st.markdown("### Live Driver Trip Actions")
        active_jobs = [s for s in data["shipments"] if s["status"] != "Delivered"]
        
        if not active_jobs:
            st.info("No pending deliveries waiting.")
        else:
            for s in active_jobs:
                st.markdown(f"📦 **{s['cargo']}** (To: {s['destination']})")
                current_state = s["status"]
                
                if not s.get("is_split"):
                    if current_state == "Assigned":
                        if st.button(f"Confirm Pickup (ID: {s['id']})", key=f"pk_{s['id']}", use_container_width=True):
                            s["status"] = "Picked Up"; save_data(data); st.rerun()
                    elif current_state == "Picked Up":
                        if st.button(f"Mark In Transit (ID: {s['id']})", key=f"it_{s['id']}", use_container_width=True):
                            s["status"] = "In Transit"; save_data(data); st.rerun()
                    elif current_state == "In Transit":
                        if st.button(f"🚨 Report Stuck at Gate Queue (ID: {s['id']})", key=f"stk_{s['id']}", use_container_width=True):
                            s["status"] = "Stuck at Gate Queue"; s["gate_queue"] = random.randint(8, 22); save_data(data); st.rerun()
                        
                        # --- TRIGGER MULTI-MODAL LAST MILE SPLIT ---
                        if st.button(f"⚡ Split Consignment to 2-Wheelers (Narrow Streets)", key=f"splt_{s['id']}", use_container_width=True):
                            s["is_split"] = True
                            s["status"] = "Split Delivery Last-Mile"
                            dest_clean = s["destination"].lower()
                            loc_name = "T. Nagar (Alley 1)" if "nagar" in dest_clean else ("Sowcarpet (Alley 2)" if "sowcarpet" in dest_clean else "Parrys (Alley 3)")
                            
                            s["child_trips"] =
