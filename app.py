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
                "fare": 720
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
        if "Two-Wheeler" in op["vehicle"]:
            op["rate_per_km"] = 12
        elif "Tata Ace" in op["vehicle"]:
            op["rate_per_km"] = 30
        else:
            op["rate_per_km"] = 65

# Pre-defined coordinates for demo hubs
HUB_COORDINATES = {
    "koyambedu": [13.0692, 80.1948],
    "tambaram": [12.9229, 80.1275],
    "madhavaram": [13.1068, 80.2184],
    "guindy": [13.0067, 80.2206],
    "sriperumbudur": [12.9724, 79.9515]
}

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
            destination = st.text_input("Drop Destination", placeholder="e.g., Guindy, Tambaram")
            submit = st.form_submit_button("Match with Local Operator")
            
            if submit and cargo and pickup and destination:
                available_ops = [op for op in data["operators"] if op["status"] == "Available" and op["capacity"] >= weight]
                
                if available_ops:
                    best_op = min(available_ops, key=lambda x: x["capacity"])
                    shipment_id = f"TRK-{int(datetime.now().timestamp())}"
                    
                    mock_distance = random.randint(12, 45)
                    calculated_fare = mock_distance * best_op.get("rate_per_km", 20)
                    
                    new_shipment = {
                        "id": shipment_id,
                        "cargo": cargo,
                        "weight": weight,
                        "pickup": pickup,
                        "destination": destination,
                        "operator": best_op["name"],
                        "status": "Assigned",
                        "distance": mock_distance,
                        "fare": calculated_fare
                    }
                    data["shipments"].append(new_shipment)
                    for op in data["operators"]:
                        if op["name"] == best_op["name"]:
                            op["status"] = "Busy"
                    save_data(data)
                    st.success(f"🎉 Matched with {best_op['name']}! ID: {shipment_id}")
                    st.rerun()
                else:
                    st.error("❌ No local vehicles with enough capacity match right now.")

    with col2:
        st.markdown("### Active Consignment Tracker")
        if not data["shipments"]:
            st.info("No active shipments on the log right now.")
        else:
            for s in reversed(data["shipments"]):
                with st.expander(f"📦 {s['cargo']} -> ID: {s['id']}"):
                    st.write(f"**Route:** {s['pickup']} ➡️ {s['destination']}")
                    st.write(f"**Driver:** {s['operator']}")
                    st.markdown(f"💰 **Estimated Bill:** ₹{s.get('fare', 0)}")
                    
                    status = s["status"]
                    if status == "Assigned":
                        st.progress(25, text="Step 1/4: Driver Booked")
                    elif status == "Picked Up":
                        st.progress(50, text="Step 2/4: Loading Completed")
                    elif status == "In Transit":
                        st.progress(75, text="Step 3/4: In Transit")
                    elif status == "Delivered":
                        st.progress(100, text="Step 4/4: Delivered 🎉")

    with col3:
        st.markdown("### 🗺️ Network Hub Network Map")
        m_prod = folium.Map(location=[13.0827, 80.2707], zoom_start=10)
        for key, coord in HUB_COORDINATES.items():
            folium.Marker(coord, popup=f"Active Hub: {key.capitalize()}", icon=folium.Icon(color='green', icon='cloud')).add_to(m_prod)
        st_folium(m_prod, width="100%", height=450, key="prod_map", returned_objects=[])

# --- 2. OPERATOR PORTAL ---
elif user_role == "🚛 Operator Portal":
    st.title("🚛 Local Transporter Manifest Control")
    col1, col2, col3 = st.columns([1.2, 1.3, 1.5])
    
    with col1:
        st.markdown("### Registered Chennai Fleet")
        df_ops = pd.DataFrame(data["operators"])
        st.dataframe(df_ops[["name", "vehicle", "status"]], use_container_width=True, hide_index=True)
        
        with st.expander("➕ Register a New Driver"):
            new_name = st.text_input("Driver Name")
            new_veh = st.selectbox("Vehicle Type", ["Two-Wheeler", "Tata Ace (Van)", "Eicher Pro (Truck)"])
            new_cap = st.number_input("Payload Limit (kg)", min_value=10, value=1000)
            new_rate = st.number_input("Freight Rate (₹ per KM)", min_value=5, value=25)
            if st.button("Bring Online"):
                if new_name:
                    data["operators"].append({
                        "id": len(data["operators"]) + 1, "name": new_name, "vehicle": new_veh,
                        "capacity": new_cap, "status": "Available", "rate_per_km": new_rate
                    })
                    save_data(data)
                    st.success("Registered successfully!")
                    st.rerun()

    with col2:
        st.markdown("### Live Driver Trip Actions")
        active_jobs = [s for s in data["shipments"] if s["status"] != "Delivered"]
        
        if not active_jobs:
            st.info("No pending deliveries waiting.")
        else:
            for s in active_jobs:
                st.markdown(f"📦 **{s['cargo']}** ({s['weight']}kg) | **₹{s.get('fare', 0)}**")
                current_state = s["status"]
                
                if current_state == "Assigned":
                    if st.button(f"Confirm Pickup (ID: {s['id']})", key=s['id'], use_container_width=True):
                        s["status"] = "Picked Up"
                        save_data(data)
                        st.rerun()
                elif current_state == "Picked Up":
                    if st.button(f"Mark In Transit (ID: {s['id']})", key=s['id'], use_container_width=True):
                        s["status"] = "In Transit"
                        save_data(data)
                        st.rerun()
                elif current_state == "In Transit":
                    if st.button(f"Confirm Delivered (ID: {s['id']})", key=s['id'], use_container_width=True):
                        s["status"] = "Delivered"
                        for op in data["operators"]:
                            if op["name"] == s["operator"]:
                                op["status"] = "Available"
                        save_data(data)
                        st.rerun()

    with col3:
        st.markdown("### 🗺️ Dispatch Manifest Map")
        m_op = folium.Map(location=[13.0827, 80.2707], zoom_start=10)
        
        # Highlight locations where drivers need to pick up active shipments
        for job in active_jobs:
            pickup_clean = job["pickup"].lower().strip()
            # Default to center if pickup location text isn't in our mock coordinate dictionary
            coords = HUB_COORDINATES.get("koyambedu") 
            for key in HUB_COORDINATES:
                if key in pickup_clean:
                    coords = HUB_COORDINATES[key]
            
            folium.Marker(coords, popup=f"PENDING PICKUP: {job['cargo']}", icon=folium.Icon(color='red', icon='play')).add_to(m_op)
            
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
                st.success(f"Consignment Records Found: **{match_found['cargo']}**")
                st.write(f"**Carrier Assigned:** {match_found['operator']}")
                st.write(f"**Route Manifest:** {match_found['pickup']} to {match_found['destination']}")
                st.write(f"**Total Fare Charge:** ₹{match_found.get('fare', 720)}")
                
                status = match_found["status"]
                if status == "Assigned":
                    st.progress(25, text="📦 Step 1: Booking verified.")
                elif status == "Picked Up":
                    st.progress(50, text="🚜 Step 2: Consignment loaded at source.")
                elif status == "In Transit":
                    st.progress(75, text="🚚 Step 3: Vehicle en route on Chennai highway network.")
                elif status == "Delivered":
                    st.info("✨ Final offloading signed off at destination.")
                    st.progress(100, text="🏁 Step 4: Consignment Delivered.")
            else:
                st.error("Invalid tracking reference. Please verify the ID code and try again.")
    
    with col_map:
        st.markdown("### Live Transit Map Routing")
        m_cust = folium.Map(location=[13.0827, 80.2707], zoom_start=11)
        
        # Base markers
        folium.Marker(HUB_COORDINATES["koyambedu"], popup="Koyambedu Hub", icon=folium.Icon(color='green')).add_to(m_cust)
        folium.Marker(HUB_COORDINATES["tambaram"], popup="Tambaram Hub", icon=folium.Icon(color='blue')).add_to(m_cust)
        folium.Marker(HUB_COORDINATES["madhavaram"], popup="Madhavaram GNT Terminal", icon=folium.Icon(color='orange')).add_to(m_cust)
        
        # If a valid shipment is typed, draw a specific connecting path line for that customer
        if search_id and 'match_found' in locals() and match_found:
            # Simple fallback demo mapping logic to connect dots
            p_text = match_found["pickup"].lower()
            d_text = match_found["destination"].lower()
            
            p_coord = HUB_COORDINATES["koyambedu"]
            d_coord = HUB_COORDINATES["tambaram"]
            
            for key in HUB_COORDINATES:
                if key in p_text: p_coord = HUB_COORDINATES[key]
                if key in d_text: d_coord = HUB_COORDINATES[key]
                
            folium.PolyLine(locations=[p_coord, d_coord], color="purple", weight=5, tooltip="Your Package Path").add_to(m_cust)
            folium.Marker(p_coord, popup="YOUR PICKUP", icon=folium.Icon(color='purple', icon='arrow-up')).add_to(m_cust)
            folium.Marker(d_coord, popup="YOUR DELIVERY", icon=folium.Icon(color='purple', icon='flag')).add_to(m_cust)

        st_folium(m_cust, width="100%", height=450, key="cust_map", returned_objects=[])
