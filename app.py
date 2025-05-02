import streamlit as st
import cx_Oracle
import bcrypt
import os
from dotenv import load_dotenv
load_dotenv()

# === DB connection setup ===
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")
username = os.getenv("username")
password = os.getenv("password")

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
    cursor.execute("SELECT role, password FROM User_Data WHERE name = :name", {'name': name})
    result = cursor.fetchone()
    if result:
        role, password_lob = result
        return role, password_lob.read()  
    return None


def add_user(cursor, name, role, hashed_pw):
    cursor.setinputsizes(password=cx_Oracle.BLOB)
    cursor.execute("""
    INSERT INTO User_Data (name, role, password)
    VALUES (:name, :role, :password)
    """, {'name': name, 'role': role, 'password': hashed_pw})


    
# UI starts here
st.title("Smart Inventory Management System")

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
                role, stored_pw = creds
                if role == "admin" or role == "user":
                    if verify_password(password_input, stored_pw): 
                        st.success(f"Welcome, {role} {name}!")
                    else:
                        st.error("Incorrect password.")
                else:
                    st.error("Unknown role.")
