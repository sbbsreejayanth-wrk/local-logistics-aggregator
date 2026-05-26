import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime
import folium
from streamlit_folium import st_folium

# --- CONFIGURATION & DATABASE SETUP ---
st.set_page_config(page_title="NEO-CHENNAI | Autonomous Logistics Aggregator", layout="wide")
DB_FILE = "logistics_db.json"

# --- 🚀 THE PREMIUM ENTERPRISE GLASSMORPHISM CSS ENGINE ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

        /* Global Theme Overrides */
        .stApp {
            background: linear-gradient(135deg, #0b0f17 0%, #111827 100%) !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Force highly visible typography colors */
        .stApp, .stMarkdown, p, span, div, .stText {
            color: #f3f4f6 !important;
        }
        
        /* Premium Glow Section Headers */
        h1 {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
            color: #00FFCC !important;
            letter-spacing: -1px;
            text-transform: uppercase;
            text-shadow: 0 0 20px rgba(0, 255, 204, 0.2);
            margin-bottom: 25px !important;
        }
        h2, h3 {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 600 !important;
            color: #ffffff !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 8px;
            margin-top: 20px !important;
        }

        /* Glassmorphic Data Cards & Widgets */
        div[data-testid="stMetricBlock"], .streamlit-expanderHeader, div.stForm {
            background: rgba(22, 30, 49, 0.6) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(0, 255, 204, 0.15) !important;
            border-radius: 12px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
            padding: 20px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        div[data-testid="stMetricBlock"]:hover {
            border-color: rgba(0, 255, 204, 0.4) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 255, 204, 0.1) !important;
            transform: translateY(-2px);
        }

        /* Metric Labels Alignment */
        div[data-testid="stMetricBlock"] [data-testid="stMetricLabel"] p {
            color: #9ca3af !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }
        div[data-testid="stMetricBlock"] [data-testid="stMetricValue"] div {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
            color: #ffffff !important;
        }

        /* Premium Form Controls & Input Fields */
        label, [data-testid="stWidgetLabel"] p {
            color: #9ca3af !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
        }
        
        input, select, textarea, div[data-baseweb="select"] {
            background-color: #0b0f17 !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
        }
        input:focus, select:focus, textarea:focus {
            border-color: #00FFCC !important;
            box-shadow: 0 0 8px rgba(0, 255, 204, 0.2) !important;
        }

        /* High-End Enterprise Tables */
        .stDataFrame div, table, th, td, [data-testid="stTable"] {
            color: #e5e7eb !important;
            background-color: #111827 !important;
            border-collapse: collapse;
        }
        th {
            background-color: #1f2937 !important;
            font-family: 'JetBrains Mono', monospace !important;
            color: #00FFCC !important;
            text-transform: uppercase;
            font-size: 0.8rem;
        }

        /* Cyberpunk Button Core Framework */
        .stButton>button {
            background: linear-gradient(90deg, #1f2937 0%, #111827 100%) !important;
            color: #00FFCC !important;
            border: 1px solid #00FFCC !important;
            border-radius: 8px !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 600 !important;
            padding: 10px 24px !important;
            letter-spacing: 0.5px;
            transition: all 0.4s ease-in-out !important;
            width: 100%;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #00FFCC 0%, #00E6B8 100%) !important;
            color: #0b0f17 !important;
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.4) !important;
            border-color: #00FFCC !important;
        }

        /* Left Hand Navigation Rail styling */
        section[data-testid="stSidebar"] {
            background: #070a10 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        }
        section[data-testid="stSidebar"] .stRadio > label {
            color: #00FFCC !important;
            font-family: 'JetBrains Mono', monospace;
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
        ],
        "tickets": []
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

if "producer_wallet" not in data: data["producer_wallet"] = 25000
if "tickets" not in data: data["tickets"] = []

for op in data["operators"]:
    if "rate_per_km" not in op: op["rate_per_km"] = 12 if "Two-Wheeler" in op["vehicle"] else (30 if "Tata Ace" in op["vehicle"] else 65)
    if "capacity" not in op: op["capacity"] = 30 if "Two-Wheeler" in op["vehicle"] else (850 if "Tata Ace" in op["vehicle"] else 4000)
    if "wallet_balance" not in op: op["wallet_balance"] = 3500

for s in data["shipments"]:
    if "fare" not in s: s["fare"] = 0
    if "payment_status" not in s: s["payment_status"] = "Released to Operator" if s["status"] == "Delivered" else "Paid (In Escrow)"
save_data(data)

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

def create_satellite_map(center_coords, zoom=11):
    sat_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    labels_url = "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}"
    m = folium.Map(location=center_coords, zoom_start=zoom, tiles=sat_url, attr="Esri Maxar")
    folium.TileLayer(tiles=labels_url, attr="Esri Labels", overlay=True, control=False).add_to(m)
    folium.Circle(location=[13.04, 80.22], radius=12000, color="#00FFCC", fill=True, fill_color="#00FFCC", fill_opacity=0.04).add_to(m)
    return m

# --- PREMIUM BRAND SIDEBAR RAIL ---
st.sidebar.markdown("<h2 style='color:#00FFCC; font-family:\"JetBrains Mono\"; text-align:center;'>⚡ NEO-CHX</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align:center; color:#9ca3af; font-size:0.8rem; margin-bottom:30px;'>Core Routing Protocol v4.2</p>", unsafe_allow_html=True)
user_role = st.sidebar.radio("CHOOSE DEPLOYMENT VIEW:", ["🌾 Producer Portal", "🚛 Operator Portal", "📦 Consumer Tracking", "💬 Customer Experience & Payments"])

# --- 1. PRODUCER PORTAL ---
if user_role == "🌾 Producer Portal":
    st.title("🌾 PRODUCER & TRADER COMMAND CENTER")
    
    c_w1, c_w2 = st.columns(2)
    with c_w1:
        st.metric(label="🛡️ Trader Prepaid Balance Ledger", value=f"₹{data['producer_wallet']:,}")
    with c_w2:
        escrow_sum = sum(s.get("fare", 0) for s in data["shipments"] if s.get("payment_status") == "Paid (In Escrow)")
        st.metric(label="🔒 Capital Secured in Route Escrow", value=f"₹{escrow_sum:,}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.3, 1.4, 1.5])
    
    with col1:
        active_backhauls = [op for op in data["operators"] if op["status"].startswith("Empty Backhaul:")]
        if active_backhauls:
            st.markdown("### 🌟 GREEN BACKHAUL MATCHES")
            for b_op in active_backhauls:
                route_info = b_op["status"].replace("Empty Backhaul:", "")
                st.warning(f"🚛 {b_op['name']} Route: {route_info}")
                if st.button(f"Claim 30% Rebate Match ({b_op['id']})", key=f"bh_{b_op['id']}"):
                    try: b_pickup, b_dest = [x.strip() for x in route_info.split("➡️")]
                    except: b_pickup, b_dest = "Tambaram Delivery Hub", "Koyambedu Wholesale Market"
                    
                    mock_dist = random.randint(15, 30)
                    fare = int((mock_dist * b_op.get("rate_per_km", 25)) * 0.70)
                    if data["producer_wallet"] >= fare:
                        data["producer_wallet"] -= fare
                        s_id = f"TRK-BH-{int(datetime.now().timestamp())}"
                        data["shipments"].append({
                            "id": s_id, "cargo": "Rebate Produce Match", "weight": int(b_op["capacity"]*0.8),
                            "pickup": b_pickup, "destination": b_dest, "operator": b_op["name"], "status": "Assigned",
                            "distance": mock_dist, "fare": fare, "gate_queue": 0, "is_split": False, "child_trips": [], "payment_status": "Paid (In Escrow)"
                        })
                        b_op["status"] = "Busy"
                        save_data(data)
                        st.rerun()

        st.markdown("### NEW SHIPMENT DISPATCH")
        with st.form("delivery_form", clear_on_submit=True):
            cargo = st.text_input("Goods Manifest Designation", placeholder="e.g., Organic Rice Cargo")
            weight = st.number_input("Payload Metrics (kg)", min_value=1, value=500)
            pickup = st.text_input("Origin Hub", placeholder="e.g., Koyambedu")
            destination = st.text_input("Destination Terminal", placeholder="e.g., Tambaram")
            if st.form_submit_button("Instantiate Match & Secure Escrow") and cargo and pickup and destination:
                available_ops = [op for op in data["operators"] if op["status"] == "Available" and op["capacity"] >= weight]
                if available_ops:
                    best_op = min(available_ops, key=lambda x: x["capacity"])
                    mock_dist = random.randint(15, 40)
                    fare = mock_dist * best_op.get("rate_per_km", 25)
                    if data["producer_wallet"] >= fare:
                        data["producer_wallet"] -= fare
                        s_id = f"TRK-{int(datetime.now().timestamp())}"
                        data["shipments"].append({
                            "id": s_id, "cargo": cargo, "weight": weight, "pickup": pickup, "destination": destination,
                            "operator": best_op["name"], "status": "Assigned", "distance": mock_dist, "fare": fare,
                            "gate_queue": 0, "is_split": False, "child_trips": [], "payment_status": "Paid (In Escrow)"
                        })
                        for o in data["operators"]:
                            if o["name"] == best_op["name"]: o["status"] = "Busy"
                        save_data(data)
                        st.rerun()

    with col2:
        st.markdown("### LIVE CONSIGNMENT REPOSITORY")
        if not data["shipments"]: st.info("No active logs found.")
        for s in reversed(data["shipments"]):
            with st.expander(f"📦 {s['cargo']} [ID: {s['id']}]"):
                st.markdown(f"**Route Vector:** `{s['pickup']}` to `{s['destination']}`")
                st.markdown(f"**Assigned Fleet Asset:** {s['operator']}")
                st.markdown(f"**Financial Escrow Clearance:** `₹{s.get('fare', 0)}` | `{s.get('payment_status')}`")
                if s.get("is_split"):
                    st.warning("⚡ Multi-Modal Split Stream Engaged")
                    for c in s["child_trips"]: st.text(f"🛵 {c['runner']} -> {c['status']} ({c['loc']})")
                else:
                    st.write(f"**Telemetry State:** `{s['status']}`")

    with col3:
        st.markdown("### STRATEGIC HUB TELEMETRY MAP")
        m_prod = create_satellite_map([13.0827, 80.2707], zoom=10)
        for k, coord in HUB_COORDINATES.items():
            folium.Marker(coord, popup=f"Terminal: {k.upper()}", icon=folium.Icon(color='blue', icon='cloud')).add_to(m_prod)
        st_folium(m_prod, width="100%", height=500, key="prod_map", returned_objects=[])

# --- 2. OPERATOR PORTAL ---
elif user_role == "🚛 Operator Portal":
    st.title("🚛 TRANSPORTER MANIFEST CONTROL CONSOLE")
    col1, col2, col3 = st.columns([1.2, 1.4, 1.5])
    
    with col1:
        st.markdown("### DISPATCH MANAGEMENT METRICS")
        st.dataframe(pd.DataFrame(data["operators"])[["name", "vehicle", "wallet_balance", "status"]], use_container_width=True, hide_index=True)
        
        st.markdown("### CX COMPLIANCE TICKETS")
        if not data.get("tickets"): st.info("Zero active system compliance disputes.")
        for tk in data["tickets"]:
            with st.expander(f"🎫 [{tk['type']}] Ref: {tk['shipment_id']}"):
                st.caption(f"Status: {tk['status']} | Logged Logs: {tk['issue_text']}")
                if tk["status"] == "Open" and st.button("Flag as Settled", key=f"res_{tk['timestamp']}"):
                    tk["status"] = "Resolved"
                    save_data(data)
                    st.rerun()

    with col2:
        st.markdown("### DRIVER ROUTING TELEMETRY PIE")
        active_jobs = [s for s in data["shipments"] if s["status"] != "Delivered"]
        if not active_jobs: st.info("No logistics requests queued.")
        for s in active_jobs:
            st.markdown(f"⚙️ **{s['cargo']}** Asset Ledger: `{s['operator']}`")
            c_state = s["status"]
            if not s.get("is_split"):
                if c_state == "Assigned" and st.button(f"Confirm Cargo Intake (ID: {s['id']})", key=f"pk_{s['id']}"):
                    s["status"] = "Picked Up"; save_data(data); st.rerun()
                elif c_state == "Picked Up" and st.button(f"Inject into Fleet Highway (ID: {s['id']})", key=f"it_{s['id']}"):
                    s["status"] = "In Transit"; save_data(data); st.rerun()
                elif c_state == "In Transit":
                    if st.button(f"⚠️ Flag Gate Gridlock Delay (ID: {s['id']})", key=f"stk_{s['id']}"):
                        s["status"] = "Stuck at Gate Queue"; s["gate_queue"] = random.randint(5, 18); save_data(data); st.rerun()
                    if st.button(f"⚡ Deploy Multimodal 2-Wheeler Split", key=f"splt_{s['id']}"):
                        s["is_split"] = True; s["status"] = "Split Delivery Last-Mile"
                        loc = "T. Nagar (Alley 1)" if "nagar" in s["destination"].lower() else "Sowcarpet (Alley 2)"
                        s["child_trips"] = [{"runner": f"Runner-Asset {i}", "status": "Out bound", "loc": loc} for i in ["A", "B", "C"]]
                        save_data(data); st.rerun()
                    if st.button(f"✅ Safe Drop & Execute Settle (ID: {s['id']})", key=f"dc_{s['id']}"):
                        s["status"] = "Delivered"; s["payment_status"] = "Released to Operator"
                        for o in data["operators"]:
                            if o["name"] == s["operator"]: o["wallet_balance"] += s.get("fare", 0); o["status"] = "Available"
                        save_data(data); st.rerun()
            else:
                if st.button(f"🏁 Complete Split Cycle Ledger (ID: {s['id']})", key=f"fnbk_{s['id']}"):
                    s["status"] = "Delivered"; s["payment_status"] = "Released to Operator"
                    for o in data["operators"]:
                        if o["name"] == s["operator"]: o["wallet_balance"] += s.get("fare", 0); o["status"] = "Available"
                    save_data(data); st.rerun()

    with col3:
        st.markdown("### ACTIVE ROUTE DISPATCH VECTOR")
        m_op = create_satellite_map([13.0827, 80.2707], zoom=11)
        for job in active_jobs:
            coords = HUB_COORDINATES["koyambedu"]
            for k in HUB_COORDINATES:
                if k in job["pickup"].lower() or k in job["destination"].lower(): coords = HUB_COORDINATES[k]
            folium.Marker(coords, popup=f"{job['cargo']}: {job['status']}", icon=folium.Icon(color='red')).add_to(m_op)
        st_folium(m_op, width="100%", height=500, key="op_map", returned_objects=[])

# --- 3. CONSUMER TRACKING ---
elif user_role == "📦 Consumer Tracking":
    st.title("📦 REAL-TIME CONSIGNMENT AUDIT RADAR")
    col_input, col_map = st.columns([1, 1])
    
    with col_input:
        search_id = st.text_input("INPUT SYSTEM ENCRYPTED TRACKING ID", placeholder="e.g., TRK-CH101")
        if search_id:
            match_found = next((s for s in data["shipments"] if s["id"] == search_id), None)
            if match_found:
                st.success(f"Security Clearance Verified | Manifest: **{match_found['cargo']}**")
                st.markdown(f"💰 **System Invoiced Cost:** `₹{match_found.get('fare', 0)}` | **Escrow State:** `{match_found.get('payment_status')}`")
                st.markdown(f"🛣️ **Core Route Path:** `{match_found['pickup']}` to `{match_found['destination']}`")
                
                if match_found.get("is_split"):
                    st.info("⚡ System deployed multi-modal runner assets to bypass perimeter congestion zones.")
                    for rn in match_found["child_trips"]: st.markdown(f"* `[ASSET]` **{rn['runner']}** -> Status: `{rn['status']}` ({rn['loc']})")
                else:
                    st.metric("CURRENT STATUS", value=match_found["status"])
            else: st.error("Tracking reference sequence unrecognized in database cluster.")
    
    with col_map:
        st.markdown("### LIVE PATHWAY TELEMETRY VECTOR")
        m_cust = create_satellite_map([13.0827, 80.2707], zoom=11)
        st_folium(m_cust, width="100%", height=500, key="cust_map", returned_objects=[])

# --- 4. CUSTOMER EXPERIENCE (CX) & PAYMENT PORTAL ---
elif user_role == "💬 Customer Experience & Payments":
    st.title("💬 CUSTOMER INTELLIGENCE & TRANSACTION PORTAL")
    
    # Financial Display Strip for Visibility
    c_pay1, c_pay2 = st.columns(2)
    with c_pay1:
        st.metric(label="💳 UNIFIED PREPAID CUSTOMER BALANCE", value=f"₹{data['producer_wallet']:,}")
    with c_pay2:
        total_spent = sum(s.get("fare", 0) for s in data["shipments"] if s["status"] == "Delivered")
        st.metric(label="📈 TOTAL OVERALL FREIGHT TURNOVER", value=f"₹{total_spent:,}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    cx_col1, cx_col2 = st.columns([1.1, 0.9])
    
    with cx_col1:
        # --- NEW PREMIUM PAYMENT TERMINAL SUB-SECTION ---
        st.markdown("### 💳 SECURE TOP-UP WALLET HUB")
        with st.form("wallet_topup_form", clear_on_submit=True):
            st.markdown("<p style='color:#00FFCC; font-size:0.85rem; font-family:\"JetBrains Mono\"'>MOCK INSTANT FUND GATEWAY</p>", unsafe_allow_html=True)
            topup_amount = st.number_input("Top-up Amount (INR)", min_value=100, max_value=100000, value=5000, step=500)
            
            pay_c1, pay_c2 = st.columns(2)
            with pay_c1:
                card_num = st.text_input("Debit / Corporate Card Number", value="•••• •••• •••• 4242")
            with pay_c2:
                card_expiry = st.text_input("Expiry Date / CVV", value="12/29 | •••")
                
            if st.form_submit_button("Authorize Digital Fund Transfer"):
                data["producer_wallet"] += int(topup_amount)
                save_data(data)
                st.success(f"🎉 Gateway Settled! Added ₹{topup_amount:,} directly to your corporate balance storage.")
                st.rerun()
                
        st.markdown("<br>### ⭐ DISPATCH QUALITY EVALUATION", unsafe_allow_html=True)
        delivered_shipments = [s for s in data["shipments"] if s["status"] == "Delivered"]
        if not delivered_shipments: 
            st.info("No archive data sets verified to populate telemetry updates.")
        else:
            shipment_options = {f"📦 {s['cargo']} (ID: {s['id']})": s for s in delivered_shipments}
            target_shipment = shipment_options[st.selectbox("Select Finished Manifest Target:", list(shipment_options.keys()))]
            
            with st.form("feedback_form", clear_on_submit=True):
                rating = st.slider("Select Performance Index Score", 1, 5, 5)
                fb = st.text_area("Log Asset Interface Feedback Matrix", placeholder="e.g., Flawless handoff timing...")
                if st.form_submit_button("Settle Performance Metrics"):
                    target_shipment["rating"] = rating; target_shipment["feedback"] = fb; save_data(data)
                    st.success("Performance rating safely parsed into database layer.")
        
        st.markdown("<br>### 🎫 DEPLOY INCIDENT DISPUTE ESCALATION", unsafe_allow_html=True)
        with st.form("ticket_form", clear_on_submit=True):
            t_id = st.text_input("Linked Manifest Reference Target ID", placeholder="e.g., TRK-CH101")
            i_type = st.selectbox("Dispute Class Vector", ["Delayed Delivery Network State", "Damaged Physical Cargo", "Operator Ledger Inconsistency"])
            i_desc = st.text_area("Provide Comprehensive Incident Logs")
            if st.form_submit_button("Transmit Ticket to Dispatch Desk") and t_id and i_desc:
                data["tickets"].append({"shipment_id": t_id, "type": i_type, "issue_text": i_desc, "status": "Open", "timestamp": int(datetime.now().timestamp())})
                save_data(data); st.success("Incident data broadcast to operator dispatch rails.")
                
    with cx_col2:
        st.markdown("### 🧾 DIGITAL TRANSACTION BILLING REPOSITORY")
        if not data["shipments"]:
            st.info("No invoice logs archived yet.")
        else:
            for s in reversed(data["shipments"]):
                inv_status = "🟢 SETTIED" if s["status"] == "Delivered" else "🔒 HELD IN ESCROW"
                with st.expander(f"🧾 INV-{s['id']} [{inv_status}]"):
                    st.markdown(f"**Cargo Manifest Detail:** {s['cargo']}")
                    st.markdown(f"**Route Vectors:** `{s['pickup']}` ➡️ `{s['destination']}`")
                    st.markdown("---")
                    
                    # Programmatic Cost Auditing Breakdown
                    base_fare = s.get("fare", 0)
                    platform_cut = int(base_fare * 0.05)
                    driver_payout = base_fare - platform_cut
                    
                    st.markdown(f"• Driver Core Freight Charge: `₹{driver_payout:,}`")
                    st.markdown(f"• Automated Matching Overhead (5%): `₹{platform_cut:,}`")
                    st.markdown(f"**Gross Total Cost Charged:** `₹{base_fare:,}`")
                    st.caption(f"Payment State Lifecycle Indicator: {s.get('payment_status')}")

        st.markdown("<br>### ❔ SYSTEM FUNCTIONAL PROTOCOLS (FAQ)", unsafe_allow_html=True)
        with st.expander("Why do assets report 'Stuck at Gate Queue'?"):
            st.write("Major market access corridors like Koyambedu maintain high physical intake friction profiles. The automated scheduling engine maps queue parameters dynamically to predict turnaround times down to the minute.")
        with st.expander("How does the Escrow Engine lock trader collateral securely?"):
            st.write("Payments are strictly restricted using programmed holding locks. Operators cannot bypass or route balance reserves into personal clearing nodes until specific terminal validation protocols run on-site.")
