import streamlit as st
from pymongo import MongoClient
from datetime import datetime, date
import pandas as pd
import random

# --- Page Config & Styling ---
st.set_page_config(
    page_title="FoodDash | Multi-Portal DBMS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Minimalist CSS
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .badge-ready { background-color: #28a745; color: white; }
    .badge-prep { background-color: #fd7e14; color: white; }
    .badge-wait { background-color: #6c757d; color: white; }
</style>
""", unsafe_allow_html=True)

# --- Database Connection ---
@st.cache_resource
def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    return client["food_delivery_da3"]

db = get_db()

# --- Sidebar Portal Navigation ---
st.sidebar.markdown("## ⚡ **FoodDash**")
st.sidebar.caption("Relational-to-Document DBMS DA3")
role = st.sidebar.radio(
    "Navigation Portal",
    ["👤 Customer Portal", "🍳 Restaurant Management", "🛵 Delivery Partner Portal", "📊 DBMS Analytics"]
)

# ==============================================================================
# 1. CUSTOMER PORTAL (Dynamic Customer Form + Order Placement)
# ==============================================================================
if role == "👤 Customer Portal":
    st.title("🛒 Customer Ordering Portal")
    
    existing_customers = list(db.customers.find({}, {"customer_id": 1, "first_name": 1, "last_name": 1, "email": 1}))
    cust_mode = "New Customer"
    
    if existing_customers:
        cust_mode = st.radio("Ordering Mode:", ["Create New Customer Profile", "Select Existing Registered Customer"], horizontal=True)
    else:
        st.info("ℹ️ No customers registered in the database yet. Fill out the registration form below to place your first order.")

    active_customer = None

    if cust_mode == "Create New Customer Profile" or not existing_customers:
        with st.expander("📝 Customer Registration & Delivery Address Form", expanded=True):
            with st.form("customer_registration_form"):
                col_n1, col_n2, col_n3 = st.columns(3)
                f_name = col_n1.text_input("First Name *", placeholder="e.g. Rahul")
                m_name = col_n2.text_input("Middle Name", placeholder="Optional")
                l_name = col_n3.text_input("Last Name *", placeholder="e.g. Verma")

                col_d1, col_d2 = st.columns(2)
                dob = col_d1.date_input("Date of Birth", min_value=date(1950, 1, 1), max_value=date.today())
                email = col_d2.text_input("Email Address *", placeholder="rahul@example.com")

                col_a1, col_a2, col_a3, col_a4 = st.columns([2, 1, 1, 1])
                street = col_a1.text_input("Street Address *", placeholder="12, Gandhi Road")
                city = col_a2.text_input("City *", value="Chennai")
                state = col_a3.text_input("State *", value="Tamil Nadu")
                pin = col_a4.text_input("PIN Code *", placeholder="600040")

                col_p1, col_p2 = st.columns(2)
                p1 = col_p1.text_input("Primary Mobile Number *", placeholder="9876543210")
                p2 = col_p2.text_input("Alternate Phone Number", placeholder="Optional")

                reg_submit = st.form_submit_button("Save & Proceed to Ordering", type="primary")

                if reg_submit:
                    if not f_name or not l_name or not email or not street or not pin or not p1:
                        st.error("Please fill in all mandatory fields marked with *")
                    else:
                        last_c = db.customers.find_one(sort=[("customer_id", -1)])
                        next_cid = 101 if not last_c else last_c["customer_id"] + 1
                        
                        phone_list = [p1.strip()]
                        if p2.strip():
                            phone_list.append(p2.strip())

                        cust_doc = {
                            "customer_id": next_cid,
                            "first_name": f_name.strip(),
                            "middle_name": m_name.strip(),
                            "last_name": l_name.strip(),
                            "dob": str(dob),
                            "email": email.strip(),
                            "address": {"street": street.strip(), "city": city.strip(), "state": state.strip(), "pin": pin.strip()},
                            "mobile_numbers": phone_list
                        }
                        db.customers.insert_one(cust_doc)
                        st.session_state["current_customer_id"] = next_cid
                        st.success(f"Customer registered successfully! Customer ID: #{next_cid}")
                        st.rerun()

    else:
        cust_map = {f"#{c['customer_id']} - {c['first_name']} {c['last_name']} ({c['email']})": c['customer_id'] for c in existing_customers}
        chosen_label = st.selectbox("Select Your Customer Account:", list(cust_map.keys()))
        st.session_state["current_customer_id"] = cust_map[chosen_label]

    # Active Customer Context
    current_cid = st.session_state.get("current_customer_id")
    if current_cid:
        active_customer = db.customers.find_one({"customer_id": current_cid})

    if active_customer:
        st.markdown(f"""
        > 👤 **Active Customer:** {active_customer['first_name']} {active_customer['last_name']} | 📞 `{active_customer['mobile_numbers'][0]}` | 📍 `{active_customer['address']['street']}, {active_customer['address']['city']} ({active_customer['address']['pin']})`
        """)

        st.markdown("---")
        st.subheader("Explore Restaurants & Menus")

        restaurants = list(db.restaurants.find())
        if not restaurants:
            st.warning("No restaurants available.")
        else:
            rest_labels = {f"{r['name']} — {r.get('cuisine', 'Specialty')} (⭐ {r.get('avg_rating', 4.5)})": r['restaurant_id'] for r in restaurants}
            selected_r_label = st.selectbox("Choose a Restaurant:", list(rest_labels.keys()))
            selected_rid = rest_labels[selected_r_label]
            rest_obj = db.restaurants.find_one({"restaurant_id": selected_rid})

            if "cart" not in st.session_state or st.session_state.get("cart_rest_id") != selected_rid:
                st.session_state.cart = {}
                st.session_state.cart_rest_id = selected_rid

            col_menu_view, col_cart_view = st.columns([3, 2])

            with col_menu_view:
                st.write(f"#### Menu from {rest_obj['name']}")
                st.caption(f"📍 {rest_obj['address']['street']}, {rest_obj['address']['city']} | 📞 {rest_obj['phone_num']}")
                
                menu_list = rest_obj.get("menu", [])
                if not menu_list:
                    st.info("No items on this restaurant's menu yet.")
                for item in menu_list:
                    with st.container():
                        col_i1, col_i2, col_i3 = st.columns([3, 1, 1])
                        avail = item.get("is_available", True)
                        col_i1.markdown(f"**{item['item_name']}** {'*(Unavailable)*' if not avail else ''}\n\n₹{item['price']:.2f} — *{item.get('description', '')}*")
                        qty = col_i2.number_input("Qty", min_value=0, max_value=10, value=0, key=f"q_{item['item_id']}", disabled=not avail)
                        if col_i3.button("Add", key=f"add_{item['item_id']}", disabled=not avail):
                            if qty > 0:
                                st.session_state.cart[item["item_id"]] = {
                                    "item_id": item["item_id"],
                                    "item_name": item["item_name"],
                                    "unit_price": item["price"],
                                    "qty": qty,
                                    "sub_total": qty * item["price"]
                                }
                                st.toast(f"Added {qty}x {item['item_name']}")
                            else:
                                st.warning("Set quantity > 0")

            with col_cart_view:
                st.write("#### 🛒 Current Cart")
                if not st.session_state.cart:
                    st.caption("Your cart is empty.")
                else:
                    total_sum = 0.0
                    order_items = []
                    for i_id, c_item in list(st.session_state.cart.items()):
                        st.write(f"• **{c_item['item_name']}** x {c_item['qty']} = ₹{c_item['sub_total']:.2f}")
                        total_sum += c_item["sub_total"]
                        order_items.append(c_item)

                    st.markdown(f"### **Order Total: ₹{total_sum:.2f}**")
                    
                    # DA2 Procedure equivalent: classify order
                    tier = "Small Order" if total_sum < 300 else ("Medium Order" if total_sum <= 500 else "Large Order")
                    st.caption(f"Tier: **{tier}**")

                    pay_mode = st.selectbox("Payment Method", ["UPI / NetBanking", "Credit/Debit Card", "Cash on Delivery"])

                    if st.button("Place Order Now", type="primary"):
                        last_ord = db.orders.find_one(sort=[("order_id", -1)])
                        next_oid = 501 if not last_ord else last_ord["order_id"] + 1

                        new_order_doc = {
                            "order_id": next_oid,
                            "customer_id": active_customer["customer_id"],
                            "restaurant_id": selected_rid,
                            "order_date": datetime.now().strftime("%Y-%m-%d"),
                            "order_time": datetime.now().strftime("%H:%M:%S"),
                            "items": order_items,
                            "total_amt": total_sum,
                            "kitchen_status": "Received",
                            "delivery": {
                                "delivery_id": 600 + next_oid,
                                "rider_id": None,
                                "rider_name": "Unassigned",
                                "delivery_time": None,
                                "is_completed": False,
                                "payment_status": "PAID" if pay_mode != "Cash on Delivery" else "PENDING",
                                "bank_stmt_no": f"TXN_{random.randint(1000000, 9999999)}",
                                "amount": total_sum,
                                "customer_food_rating": None,
                                "customer_rider_rating": None
                            }
                        }
                        db.orders.insert_one(new_order_doc)
                        st.session_state.cart = {}
                        st.success(f"Order #{next_oid} confirmed successfully!")
                        st.rerun()

        # Customer's Order History
        st.markdown("---")
        st.subheader("📦 Your Order History")
        user_orders = list(db.orders.find({"customer_id": active_customer["customer_id"]}).sort("order_id", -1))
        if not user_orders:
            st.caption("No orders placed yet.")
        else:
            for uo in user_orders:
                r_info = db.restaurants.find_one({"restaurant_id": uo["restaurant_id"]})
                with st.expander(f"Order #{uo['order_id']} — {r_info['name']} | ₹{uo['total_amt']} | Status: {uo['kitchen_status']}"):
                    st.table(pd.DataFrame(uo["items"])[["item_name", "qty", "unit_price", "sub_total"]])
                    d = uo["delivery"]
                    st.write(f"**Rider:** {d['rider_name']} | **Delivered:** {'✅ Yes' if d['is_completed'] else '🚚 In Progress'}")
                    if d['is_completed'] and d.get('customer_food_rating') is None:
                        st.write("##### Leave Feedback")
                        cfr = st.slider("Food Rating", 1.0, 5.0, 5.0, 0.5, key=f"cfr_{uo['order_id']}")
                        crr = st.slider("Rider Rating", 1.0, 5.0, 5.0, 0.5, key=f"crr_{uo['order_id']}")
                        if st.button("Submit Feedback", key=f"fdbk_{uo['order_id']}"):
                            db.orders.update_one(
                                {"order_id": uo['order_id']},
                                {"$set": {"delivery.customer_food_rating": cfr, "delivery.customer_rider_rating": crr}}
                            )
                            st.success("Thank you for your rating!")
                            st.rerun()

# ==============================================================================
# 2. RESTAURANT MANAGEMENT PORTAL (Kitchen queue + Add/Edit Menus + Add Restaurant)
# ==============================================================================
elif role == "🍳 Restaurant Management":
    st.title("🍳 Restaurant Portal & Kitchen Manager")
    
    r_tab1, r_tab2, r_tab3 = st.tabs(["🔥 Live Kitchen Orders", "📋 Menu Customizer", "➕ Add New Restaurant"])

    restaurants = list(db.restaurants.find())
    
    # TAB 1: Live Kitchen
    with r_tab1:
        if not restaurants:
            st.info("No restaurants found.")
        else:
            rest_lookup = {r['name']: r['restaurant_id'] for r in restaurants}
            sel_r_name = st.selectbox("Select Restaurant Dashboard", list(rest_lookup.keys()), key="kitchen_rest_select")
            curr_rid = rest_lookup[sel_r_name]

            live_orders = list(db.orders.find({"restaurant_id": curr_rid}).sort("order_id", -1))
            if not live_orders:
                st.info(f"No incoming orders for {sel_r_name} right now.")
            else:
                for ord_item in live_orders:
                    with st.container():
                        c_info = db.customers.find_one({"customer_id": ord_item["customer_id"]})
                        c_name = f"{c_info['first_name']} {c_info['last_name']}" if c_info else "Customer"
                        
                        c1, c2, c3 = st.columns([2, 2, 2])
                        c1.markdown(f"**Order #{ord_item['order_id']}** by `{c_name}`\n\nTime: `{ord_item['order_time']}`")
                        
                        items_str = "<br>".join([f"• {it['qty']}x {it['item_name']}" for it in ord_item["items"]])
                        c2.markdown(f"**Items:**<br>{items_str}", unsafe_allow_html=True)
                        
                        current_status = ord_item.get("kitchen_status", "Received")
                        next_status = c3.selectbox(
                            "Update Status",
                            ["Received", "Preparing", "Ready for Pickup", "Dispatched"],
                            index=["Received", "Preparing", "Ready for Pickup", "Dispatched"].index(current_status) if current_status in ["Received", "Preparing", "Ready for Pickup", "Dispatched"] else 0,
                            key=f"k_stat_{ord_item['order_id']}"
                        )
                        if c3.button("Update Status", key=f"btn_k_{ord_item['order_id']}"):
                            db.orders.update_one({"order_id": ord_item['order_id']}, {"$set": {"kitchen_status": next_status}})
                            st.rerun()
                        st.divider()

    # TAB 2: Menu Customizer
    with r_tab2:
        if not restaurants:
            st.info("No restaurants found.")
        else:
            rest_lookup = {r['name']: r['restaurant_id'] for r in restaurants}
            sel_r_menu = st.selectbox("Select Restaurant to Edit Menu", list(rest_lookup.keys()), key="menu_rest_select")
            m_rid = rest_lookup[sel_r_menu]
            r_record = db.restaurants.find_one({"restaurant_id": m_rid})

            st.write(f"#### Edit Existing Dishes for {r_record['name']}")
            for dish in r_record.get("menu", []):
                col_d1, col_d2, col_d3 = st.columns([3, 1, 1])
                col_d1.write(f"**{dish['item_name']}** — ₹{dish['price']}")
                avail = col_d2.checkbox("In Stock", value=dish.get("is_available", True), key=f"stk_{dish['item_id']}")
                if avail != dish.get("is_available", True):
                    db.restaurants.update_one(
                        {"restaurant_id": m_rid, "menu.item_id": dish["item_id"]},
                        {"$set": {"menu.$.is_available": avail}}
                    )
                    st.rerun()

            st.markdown("---")
            st.write("#### Add a New Dish to this Menu")
            with st.form(f"add_dish_form_{m_rid}"):
                new_dish_name = st.text_input("Item Name")
                new_dish_desc = st.text_input("Description")
                new_dish_price = st.number_input("Price (₹)", min_value=10.0, step=10.0, value=150.0)
                if st.form_submit_button("Add Dish"):
                    if new_dish_name:
                        new_item_id = random.randint(500, 9999)
                        db.restaurants.update_one(
                            {"restaurant_id": m_rid},
                            {"$push": {"menu": {
                                "item_id": new_item_id,
                                "item_name": new_dish_name.strip(),
                                "description": new_dish_desc.strip(),
                                "price": float(new_dish_price),
                                "is_available": True
                            }}}
                        )
                        st.success(f"Added {new_dish_name} to {r_record['name']}!")
                        st.rerun()

    # TAB 3: Add New Restaurant
    with r_tab3:
        st.write("#### Register a New Restaurant Partner")
        with st.form("new_restaurant_form"):
            nr_name = st.text_input("Restaurant Name *")
            nr_cuisine = st.text_input("Cuisine Type *", placeholder="e.g. Japanese Sushi, Mexican")
            nr_email = st.text_input("Email *")
            nr_phone = st.text_input("Phone Number *")
            nr_street = st.text_input("Street Address *")
            nr_city = st.text_input("City *", value="Chennai")
            nr_state = st.text_input("State *", value="Tamil Nadu")
            nr_pin = st.text_input("PIN Code *")

            st.write("##### Add Initial Dish for this Restaurant")
            i_name = st.text_input("First Dish Name *", placeholder="e.g. Ramen")
            i_desc = st.text_input("Dish Description", placeholder="e.g. Rich broth noodles")
            i_price = st.number_input("Dish Price (₹)", min_value=20.0, value=250.0)

            if st.form_submit_button("Register Restaurant", type="primary"):
                if not nr_name or not nr_cuisine or not nr_email or not nr_phone or not i_name:
                    st.error("Please fill in all mandatory restaurant fields!")
                else:
                    last_r = db.restaurants.find_one(sort=[("restaurant_id", -1)])
                    next_rid = 201 if not last_r else last_r["restaurant_id"] + 1
                    
                    new_rest_doc = {
                        "restaurant_id": next_rid,
                        "name": nr_name.strip(),
                        "cuisine": nr_cuisine.strip(),
                        "email": nr_email.strip(),
                        "phone_num": nr_phone.strip(),
                        "address": {"street": nr_street.strip(), "city": nr_city.strip(), "state": nr_state.strip(), "pin": nr_pin.strip()},
                        "avg_rating": 4.5,
                        "menu": [{
                            "item_id": random.randint(1000, 9999),
                            "item_name": i_name.strip(),
                            "description": i_desc.strip(),
                            "price": float(i_price),
                            "is_available": True
                        }]
                    }
                    db.restaurants.insert_one(new_rest_doc)
                    st.success(f"Registered {nr_name} with ID #{next_rid}!")
                    st.rerun()

# ==============================================================================
# 3. DELIVERY PARTNER PORTAL (Active Riders + Onboard New Driver)
# ==============================================================================
elif role == "🛵 Delivery Partner Portal":
    st.title("🛵 Delivery Partner Management")

    del_tab1, del_tab2 = st.tabs(["🚀 Rider Deliveries", "➕ Onboard New Driver"])

    riders = list(db.delivery_riders.find())

    # TAB 1: Rider Task View
    with del_tab1:
        if not riders:
            st.warning("No delivery riders registered.")
        else:
            r_map = {f"{r['name']} ({r['license_num']})": r for r in riders}
            chosen_rider_label = st.selectbox("Active Rider Login:", list(r_map.keys()))
            active_rider = r_map[chosen_rider_label]

            st.caption(f"ID: `#{active_rider['rider_id']}` | Contact: `{active_rider['phone_numbers'][0]}` | ⭐ Rating: `{active_rider['avg_rating']}`")
            st.markdown("---")

            col_avail, col_assigned = st.columns(2)

            with col_avail:
                st.subheader("Available for Pickup")
                pool_orders = list(db.orders.find({
                    "delivery.rider_id": None,
                    "kitchen_status": {"$in": ["Preparing", "Ready for Pickup"]}
                }))

                if not pool_orders:
                    st.info("No orders currently waiting for pickup.")
                else:
                    for po in pool_orders:
                        rest_entry = db.restaurants.find_one({"restaurant_id": po["restaurant_id"]})
                        st.markdown(f"**Order #{po['order_id']}** — Pickup: `{rest_entry['name']}`")
                        st.caption(f"Amount: ₹{po['total_amt']} | Payment: {po['delivery']['payment_status']}")
                        if st.button("Claim Delivery", key=f"claim_{po['order_id']}"):
                            db.orders.update_one(
                                {"order_id": po['order_id']},
                                {"$set": {
                                    "delivery.rider_id": active_rider["rider_id"],
                                    "delivery.rider_name": active_rider["name"]
                                }}
                            )
                            st.success(f"Order #{po['order_id']} assigned to you!")
                            st.rerun()
                        st.divider()

            with col_assigned:
                st.subheader("My Active Deliveries")
                my_active = list(db.orders.find({
                    "delivery.rider_id": active_rider["rider_id"],
                    "delivery.is_completed": False
                }))

                if not my_active:
                    st.caption("You have no pending deliveries.")
                else:
                    for ao in my_active:
                        cust_entry = db.customers.find_one({"customer_id": ao["customer_id"]})
                        st.markdown(f"**Order #{ao['order_id']}**")
                        if cust_entry:
                            st.write(f"**Deliver To:** {cust_entry['first_name']} {cust_entry['last_name']}")
                            st.write(f"**Destination:** {cust_entry['address']['street']}, {cust_entry['address']['city']}")
                            st.write(f"**Call Customer:** `{cust_entry['mobile_numbers'][0]}`")
                        st.write(f"**Collect:** ₹{ao['total_amt']} ({ao['delivery']['payment_status']})")
                        
                        if st.button("Mark as Delivered", key=f"del_{ao['order_id']}"):
                            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            db.orders.update_one(
                                {"order_id": ao['order_id']},
                                {"$set": {
                                    "delivery.is_completed": True,
                                    "delivery.delivery_time": now_time,
                                    "delivery.payment_status": "PAID",
                                    "kitchen_status": "Delivered"
                                }}
                            )
                            st.success(f"Delivered order #{ao['order_id']}!")
                            st.rerun()
                        st.divider()

    # TAB 2: Onboard New Driver
    with del_tab2:
        st.write("#### Onboard a New Delivery Partner")
        with st.form("new_driver_registration"):
            d_name = st.text_input("Driver Full Name *")
            d_email = st.text_input("Driver Email Address *")
            d_lic = st.text_input("Driving License Number *", placeholder="TN09-20240001122")
            d_phone = st.text_input("Contact Mobile Number *")

            if st.form_submit_button("Register Driver", type="primary"):
                if not d_name or not d_email or not d_lic or not d_phone:
                    st.error("Please fill in all driver details!")
                else:
                    last_rd = db.delivery_riders.find_one(sort=[("rider_id", -1)])
                    next_rid = 401 if not last_rd else last_rd["rider_id"] + 1

                    new_rider_doc = {
                        "rider_id": next_rid,
                        "name": d_name.strip(),
                        "email": d_email.strip(),
                        "license_num": d_lic.strip(),
                        "avg_rating": 5.0,
                        "phone_numbers": [d_phone.strip()]
                    }
                    db.delivery_riders.insert_one(new_rider_doc)
                    st.success(f"Driver {d_name} enrolled successfully with Rider ID #{next_rid}!")
                    st.rerun()

# ==============================================================================
# 4. DBMS ANALYTICS & DA2 QUERIES PORTAL
# ==============================================================================
elif role == "📊 DBMS Analytics":
    st.title("📊 DBMS Analytical Queries (MongoDB Aggregations)")
    
    # Live Metrics
    pipeline_kpi = [{"$group": {"_id": None, "rev": {"$sum": "$total_amt"}, "avg_val": {"$avg": "$total_amt"}, "cnt": {"$sum": 1}}}]
    kpi_res = list(db.orders.aggregate(pipeline_kpi))
    
    total_revenue = kpi_res[0]["rev"] if kpi_res else 0.0
    avg_order_value = kpi_res[0]["avg_val"] if kpi_res else 0.0
    total_orders = kpi_res[0]["cnt"] if kpi_res else 0

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Revenue (DA2 Query 8)", f"₹{total_revenue:,.2f}")
    col_m2.metric("Average Order Value (DA2 Query 9)", f"₹{avg_order_value:,.2f}")
    col_m3.metric("Total System Orders Placed", total_orders)

    st.markdown("---")

    # DA2 Query 10: Orders per Restaurant
    st.subheader("DA2 Query 10: Restaurant Order Distribution")
    dist_pipeline = [
        {"$group": {"_id": "$restaurant_id", "order_count": {"$sum": 1}, "revenue": {"$sum": "$total_amt"}}},
        {"$lookup": {"from": "restaurants", "localField": "_id", "foreignField": "restaurant_id", "as": "rest"}},
        {"$unwind": "$rest"},
        {"$project": {"Restaurant": "$rest.name", "Cuisine": "$rest.cuisine", "Orders Placed": "$order_count", "Gross Revenue (₹)": "$revenue"}},
        {"$sort": {"Orders Placed": -1}}
    ]
    dist_res = list(db.orders.aggregate(dist_pipeline))
    if dist_res:
        st.dataframe(pd.DataFrame(dist_res)[["Restaurant", "Cuisine", "Orders Placed", "Gross Revenue (₹)"]], use_container_width=True)
    else:
        st.info("No orders placed yet to display metrics.")

    # DA2 Query 14 & 15: Complete Orders & Delivery Status Join
    st.subheader("DA2 Query 14 & 15: End-to-End Order & Delivery Audit")
    audit_pipeline = [
        {"$lookup": {"from": "customers", "localField": "customer_id", "foreignField": "customer_id", "as": "c"}},
        {"$lookup": {"from": "restaurants", "localField": "restaurant_id", "foreignField": "restaurant_id", "as": "r"}},
        {"$unwind": "$c"},
        {"$unwind": "$r"},
        {"$project": {
            "Order ID": "$order_id",
            "Customer": {"$concat": ["$c.first_name", " ", "$c.last_name"]},
            "Restaurant": "$r.name",
            "Amount (₹)": "$total_amt",
            "Status": "$kitchen_status",
            "Rider": "$delivery.rider_name",
            "Payment": "$delivery.payment_status",
            "Delivered": "$delivery.is_completed"
        }},
        {"$sort": {"Order ID": -1}}
    ]
    audit_res = list(db.orders.aggregate(audit_pipeline))
    if audit_res:
        st.dataframe(pd.DataFrame(audit_res), use_container_width=True)
    else:
        st.caption("No records available.")