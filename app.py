import streamlit as st
import cx_Oracle
import bcrypt
import os
from dotenv import load_dotenv
from Admin.Alerts import mark_alerts
from Admin.Suppliers import supplier_data, supplier_groupby, supplier_loc
from User.Products import prod_cluster
from Admin.Clusters import view_cluster_data, update_product_cluster, cluster_analysis
from Admin.Products import view_product_data
from User.Transactions import view, conduct
from Admin.Suppliers import supplier_crud
from Admin.Products import add_products, update_products, delete_products
from Admin.Users import view_and_del_acc
from Admin.Alerts import view_alerts

# Load environment variables
load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")


# Streamlit session state for authentication
if 'is_user' not in st.session_state:
    st.session_state.is_user = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Functions for authentication and database interaction
def create_connection():
    return cx_Oracle.connect(user=username, password=password, dsn=dsn)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def user_exists(cursor, name):
    cursor.execute("SELECT COUNT(*) FROM User_Data WHERE name = :name", {'name': name})
    return cursor.fetchone()[0] > 0

def get_user_credentials(cursor, name):
    cursor.execute("SELECT user_id, role, password FROM User_Data WHERE name = :name", {'name': name})
    result = cursor.fetchone()
    if result:
        user_id, role, password_lob = result
        return user_id, role, password_lob.read()
    return None

def add_user(cursor, name, role, hashed_pw):
    cursor.setinputsizes(password=cx_Oracle.BLOB)
    cursor.execute(""" 
        INSERT INTO User_Data (name, role, password) 
        VALUES (:name, :role, :password)
    """, {'name': name, 'role': role, 'password': hashed_pw})

def change_password_section(current_user_id):
    with st.expander("🔐 Change Password"):
        current_password = st.text_input("Current Password", type="password", key="current_pass")
        new_password = st.text_input("New Password", type="password", key="new_pass")

        if st.button("Update Password", key="btn_change_pass"):
            try:
                conn = create_connection()
                cursor = conn.cursor()

                # Fetch stored password
                cursor.execute("""
                    SELECT password FROM User_Data WHERE user_id = :user_id
                """, {'user_id': current_user_id})
                result = cursor.fetchone()

                if not result:
                    st.error("❌ User not found.")
                    return

                stored_password = result[0].read()

                if not verify_password(current_password, stored_password):
                    st.error("❌ Current password is incorrect.")
                    return

                # Update password
                new_hashed = hash_password(new_password)
                cursor.setinputsizes(password=cx_Oracle.BLOB)
                cursor.execute("""
                    UPDATE User_Data
                    SET password = :password
                    WHERE user_id = :user_id
                """, {'password': new_hashed, 'user_id': current_user_id})
                conn.commit()

                st.success("✅ Password updated successfully.")

            except cx_Oracle.DatabaseError as e:
                st.error(f"❌ Database Error: {e}")
            finally:
                if 'conn' in locals():
                    conn.close()

if not st.session_state['is_user'] and not st.session_state['is_admin']:
    st.title("🔐 Smart Inventory Management System")
    mode = st.radio("Choose Mode:", ["Login", "Signup"])
    name = st.text_input("Username")
    password_input = st.text_input("Password", type="password")

    if mode == "Signup":
        if st.button("Sign Up"):
            with create_connection() as conn:
                cursor = conn.cursor()
                if user_exists(cursor, name):
                    st.warning("User already exists!")
                else:
                    hashed = hash_password(password_input)
                    add_user(cursor, name, "user", hashed)
                    conn.commit()
                    st.success("Signup successful! You can now log in.")

    elif mode == "Login":
        if st.button("Login"):
            with create_connection() as conn:
                cursor = conn.cursor()
                creds = get_user_credentials(cursor, name)
                if not creds:
                    st.error("User not found.")
                else:
                    user_id, role, stored_pw = creds
                    if verify_password(password_input, stored_pw):
                        st.session_state['is_admin'] = (role.lower() == "admin")
                        st.session_state['is_user'] = (role.lower() == "user")
                        st.session_state['user_id'] = user_id
                        st.session_state['username'] = name
                        st.session_state['role'] = role
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect password.")
                        

def fetch_all_product_names():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Products")
        return [row[0] for row in cursor.fetchall()]
    
def fetch_all_categories():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM Products")
        return [row[0] for row in cursor.fetchall()]
    
def fetch_all_cluster_ids():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT cluster_id FROM Products")
        return [row[0] for row in cursor.fetchall()]
    
def fetch_all_suppliers():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Suppliers")
        return [row[0] for row in cursor.fetchall()]

product_names = fetch_all_product_names()  
category_names = fetch_all_categories()
cluster_ids = fetch_all_cluster_ids()
supplier_names = fetch_all_suppliers()

if st.session_state['is_admin']:
    st.title("🔐 Smart Inventory Management System")
    st.success(f"Welcome, {st.session_state.role} {st.session_state.username}!")

    # Logout functionality
    if st.button("Logout"):
        for key in ["is_user", "is_admin", "username", "role", "supplier_output"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # Admin Dashboard
    st.subheader("Admin Dashboard")

    # Accordion-style collapsible sections for queries
    with st.expander("🏭 Supplier Data"):
        supplier_tabs = st.tabs(["🔍 By Name", "📊 Group by Location", "🌍 Filter by Location", "➕ Add Supplier", "✏️ Update Supplier", "❌ Delete Supplier"])

        with supplier_tabs[0]:
            supplier_name = st.text_input("Enter Supplier Name", key="supplier_name")
            if st.button("Get Supplier Info", key="btn_supplier_info"):
                output = supplier_data.fetch_supplier_info(supplier_name)
                for line in output:
                    st.text(line)

        with supplier_tabs[1]:
            if st.button("Show Grouped Supplier Counts", key="btn_grouped"):
                grouped = supplier_groupby.fetch_supplier_groupby()
                for loc, count in grouped:
                    st.write(f"{loc}: {count} suppliers")

        with supplier_tabs[2]:
            city = st.text_input("City (optional)", key="city_input")
            country = st.text_input("Country (optional)", key="country_input")
            if st.button("Search by Location", key="btn_search_location"):
                data = supplier_loc.fetch_suppliers_by_location(city if city else None, country if country else None)
                for line in data:
                    st.text(line)


        with supplier_tabs[3]:
            st.subheader("Add New Supplier")
            new_id = st.text_input("Supplier ID", key="create_id")
            new_name = st.text_input("Supplier Name", key="create_name")
            new_loc = st.text_input("Location", key="create_loc")
            new_contact = st.text_input("Contact Info", key="create_contact")

            if st.button("Create Supplier"):
                result = supplier_crud.create_supplier(int(new_id), new_name, new_loc, new_contact)
                st.success(result["success"]) if "success" in result else st.error(result["error"])

        # ✏️ Update Supplier
        with supplier_tabs[4]:
            st.subheader("Update Supplier Info")
            update_id = st.text_input("Supplier ID to Update", key="update_id")
            new_name = st.text_input("New Name (optional)", key="update_name")
            new_loc = st.text_input("New Location (optional)", key="update_loc")
            new_contact = st.text_input("New Contact Info (optional)", key="update_contact")

            if st.button("Update Supplier"):
                result = supplier_crud.update_supplier(int(update_id), name=new_name or None, location=new_loc or None, contact_info=new_contact or None)
                st.success(result["success"]) if "success" in result else st.error(result["error"])

        # ❌ Delete Supplier
        with supplier_tabs[5]:
            st.subheader("Delete Supplier")
            delete_id = st.text_input("Supplier ID to Delete", key="delete_id")

            if st.button("Delete Supplier"):
                result = supplier_crud.delete_supplier(int(delete_id))
                st.success(result["success"]) if "success" in result else st.error(result["error"])

        
    # Cluster Queries Section
    with st.expander("🔢 Cluster Data"):
        cluster_tabs = st.tabs(["🔎 Filter Clusters", "✔️ Get Cluster data", "🔀 Update Product Cluster"])

        with cluster_tabs[0]:
            min_quantity = st.text_input("Minimum Avg Quantity", key="min_qty")
            min_price = st.text_input("Minimum Avg Price", key="min_price")
            min_sales = st.text_input("Minimum Avg Sales", key="min_sales")
            min_popularity = st.text_input("Minimum Popularity Score", key="min_pop")
            min_clusters = st.text_input("Number of Clusters", key="num_clusters")

            if st.button("Run Cluster Filter", key="btn_run_cluster_filter"):
                results = cluster_analysis.filter_clusters(
                    float(min_quantity) if min_quantity else None,
                    float(min_price) if min_price else None,
                    float(min_sales) if min_sales else None,
                    float(min_popularity)/100 if min_popularity else None,
                    float(min_clusters) if min_clusters else None
                )
                for line in results:
                    st.text(line)

        with cluster_tabs[1]:
            cluster_id = st.text_input("Enter Cluster ID", key="cluster_id")
            if st.button("Get Cluster Data", key="btn_cluster_data"):
                cluster_details = view_cluster_data.fetch_cluster_details(cluster_id)
                
                if "error" in cluster_details:
                    st.error(cluster_details["error"])
                else:
                    st.subheader(f"📦 Cluster ID: {cluster_details['Cluster ID']}")
                    st.markdown(f"**Average Quantity:** {cluster_details['Average Quantity']}")
                    st.markdown(f"**Average Price:** ₹{cluster_details['Average Price']}")
                    st.markdown(f"**Average Sales:** {cluster_details['Average Sales']}")
                    st.markdown(f"**Popularity Score:** {cluster_details['Popularity Score']*100}%")

                    # Nicely format Category Distribution
                    st.markdown("**🗂 Category Distribution:**")
                    for category in cluster_details['Category Distribution']:
                        st.markdown(f"- {category}")
                        
       # Tab 3 - Update Product Cluster
        with cluster_tabs[2]:
            st.markdown("### 🔄 Reassign Product to Cluster")
            product_id = st.text_input("Product ID", key="cluster_update_product_id")
            new_cluster_id = st.text_input("New Cluster ID", key="cluster_update_new_id")

            if st.button("Update Product Cluster", key="btn_update_cluster"):
                if product_id and new_cluster_id:
                    result = update_product_cluster.reassign_product_cluster(
                        int(product_id),
                        int(new_cluster_id)
                    )

                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(result["success"])
                else:
                    st.warning("Please enter both Product ID and New Cluster ID.")
                    


    with st.expander("📦 Product Data"):
        product_tabs = st.tabs([
            "🔎 View Product Data", "🔄 Stock In/Out Product", "➕ Create Product",
            "✏️ Update Product", "❌ Delete Product"
        ])

        # --- 🔍 View Product ---
        with product_tabs[0]:
            selected_product = st.selectbox("Select a product to view", product_names, key="view_product_name")
            if st.button("Get Product Info", key="btn_view_product"):
                data = view_product_data.fetch_product_data_by_name(selected_product)
                if "error" in data:
                    st.error(data["error"])
                else:
                    st.markdown("### Product Details")
                    for k, v in data.items():
                        st.write(f"**{k}**: {v}")
                    
        with product_tabs[1]:
            st.markdown("### 🔄 Conduct Transaction")
            product_name = st.selectbox("Select Product", product_names, key="conduct_product_name")
            quantity = st.number_input("Quantity (positive for stock-in, negative for stock-out)", key="conduct_quantity")
            user_id = st.session_state["user_id"] 
            
            if st.button("Conduct Transaction", key="btn_conduct_transaction"):
                if product_name and user_id:
                    result = conduct.call_conduct_transaction(product_name, int(quantity), int(user_id))
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success(result["success"])
                else:
                    st.warning("Please enter both Product Name and User ID.")

        # --- ➕ Create Product ---
        with product_tabs[2]:
            st.subheader("Add New Product")
            new_name = st.text_input("Product Name")
            new_category = st.selectbox("Category", category_names)
            new_price = st.number_input("Price", min_value=0.0)
            new_qty = st.number_input("Quantity", min_value=0)
            new_sales = st.number_input("Sales", min_value=0)
            new_rating = st.number_input("Rating")
            selected_supplier_create = st.selectbox("Supplier", supplier_names)
            selected_cluster_create = st.selectbox("Cluster", cluster_ids)  
            
            if st.button("Add Product"):
                supplier_id = add_products.get_supplier_id_from_name(selected_supplier_create)
                if new_name and supplier_id and new_category:
                    result = add_products.add_product(new_name, new_category, float(new_price), int(new_qty), int(new_sales), float(new_rating)/100, supplier_id, selected_cluster_create)
                    if "success" in result:
                        st.success(result["success"])
                    else:
                        st.error(result["error"])
                else:
                    st.warning("Please fill all required fields.")

        
        with product_tabs[3]:
            st.subheader("Update Product")
            update_id = st.text_input("Product ID to Update")
            update_name = st.text_input("New Name (optional)")
            update_category = st.selectbox("New Category (optional)", category_names)
            update_price = st.text_input("New Price (optional)")
            update_qty = st.text_input("New Quantity (optional)")
            update_sales = st.text_input("New Sales (optional)")
            update_rating = st.text_input("New Rating (optional)")
            selected_supplier_update = st.selectbox("New Supplier (optional)", supplier_names)
            
            if st.button("Update Product"):
                try:
                    supplier_id = add_products.get_supplier_id_from_name(selected_supplier_update)
                    result = update_products.update_product(
                        int(update_id),
                        name=update_name or None,
                        category=update_category or None,
                        price=float(update_price) if update_price else None,
                        quantity=int(update_qty) if update_qty else None,
                        sales=int(update_sales) if update_sales else None,
                        rating=float(update_rating)/100 if update_rating else None,
                        supplier_id=supplier_id,
                    )
                    if "success" in result:
                        st.success(result["success"])
                    else:
                        st.error(result["error"])
                except Exception as e:
                    st.error(str(e))


        # --- ❌ Delete Product ---
        with product_tabs[4]:
            st.subheader("Delete Product")
            delete_id = st.text_input("Product ID to Delete")
            if st.button("Delete Product"):
                try:
                    result = delete_products.delete_product(int(delete_id))
                    if "success" in result:
                        st.success(result["success"])
                    else:
                        st.error(result["error"])

                except Exception as e:
                    st.error(str(e))

    with st.expander("👤 User Management"):
        df_users = view_and_del_acc.fetch_non_admin_users()

        if not df_users.empty:
            st.dataframe(df_users, use_container_width=True)

            # Filter current user and allow deletion only for non-admins
            delete_name = st.selectbox("🔴 Select a user to delete", df_users["Name"])

            if st.button("❌ Delete Selected User"):
                selected_id = int(df_users[df_users["Name"] == delete_name]["User ID"].values[0])
                msg = view_and_del_acc.delete_user(selected_id)
                st.success(msg)
                st.rerun()
        else:
            st.info("No non-admin users found.")
    
    with st.expander("🔔 Alerts"):
        df_alerts = view_alerts.fetch_inventory_alerts()

        if df_alerts.empty:
            st.success("No alerts to show.")
        else:
            df_display = df_alerts.copy()
            df_display["ALERT_DATE"] = df_display["ALERT_DATE"].astype(str)
            df_display["STATUS"] = df_display["IS_PROCESSED"].apply(lambda x: "✅ Processed" if x else "❗ Pending")
            df_display = df_display[["PRODUCT_NAME", "ALERT_TYPE", "ALERT_DATE", "MESSAGE", "STATUS"]]

            st.dataframe(df_display, use_container_width=True)

            st.write("---")
            st.subheader("Pending Alerts")
            pending_alerts = df_alerts[df_alerts["IS_PROCESSED"] == 0]

            if pending_alerts.empty:
                st.success("All alerts are processed.")
            else:
                for i, row in pending_alerts.iterrows():
                    col1, col2, col3 = st.columns([3, 6, 2])
                    col1.markdown(f"**{row['PRODUCT_NAME']}** - {row['ALERT_TYPE']}")
                    col2.markdown(f"_{row['MESSAGE']} (at {row['ALERT_DATE']})_")
                    if col3.button("Mark Done", key=f"btn_{i}"):
                        mark_alerts.mark_alert_as_processed(row["PRODUCT_ID"], row["ALERT_DATE"])
                        st.success(f"Marked {row['PRODUCT_NAME']} as processed.")
                        st.rerun()




elif st.session_state['is_user']:
    st.title("🔐 Smart Inventory Management System")
    st.success(f"Welcome, {st.session_state.role} {st.session_state.username}!")

    # Logout functionality
    if st.button("Logout"):
        for key in ["is_user", "is_admin", "username", "role"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.subheader("🧑‍💼 User Dashboard")

    with st.expander("📦 Product Recommendations"):
        with st.form("recommendation_form"):
            category = st.selectbox("Enter Product Name or Category", product_names+category_names, key="user_category")
            submitted = st.form_submit_button("Recommend Items")

            if submitted and category:
                results = prod_cluster.recommend_items_by_category(category)
                if results:
                    st.markdown("### 📋 Recommended Items:")
                    for line in results:
                        st.text(line)
                else:
                    st.info("No recommendations found for that category.")
    with st.expander("🛒 Buy Products"):
        with st.form("buy_product_form"):
            product_name = st.selectbox("Select Product", product_names, key="user_product_name")
            quantity = st.number_input("Quantity", min_value=1, key="user_quantity")
            submitted = st.form_submit_button("Buy Product")

            if submitted and product_name and quantity:
                result = conduct.call_conduct_transaction(product_name, -int(quantity), st.session_state["user_id"])
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success(result["success"])

    with st.expander("📜 View Transactions"):
        transactions = view.fetch_transactions(
            user_id=st.session_state['user_id'],
            is_admin=st.session_state['is_admin']
        )

        if isinstance(transactions, dict) and "error" in transactions:
            st.error(transactions["error"])
        elif transactions:
            st.dataframe(transactions)
        else:
            st.info("No transactions found.")

    change_password_section(st.session_state["user_id"])

