import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# --- SECURE CONNECTION SETUP ---
def get_gspread_client():
    # Define the scope for Google Sheets and Drive
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        # Accesses the secrets you will paste into the Streamlit Cloud Dashboard
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception:
        st.error("❌ Secrets Error: 'gcp_service_account' not found. Check Streamlit Advanced Settings.")
        st.stop()

# Initialize connection
try:
    client = get_gspread_client()
    sh = client.open("PROTO")
    sheet = sh.sheet1
except Exception as e:
    st.error(f"⚠️ Connection Error: {e}")
    st.info("Ensure the 'PROTO' sheet is shared with your Service Account email.")
    st.stop()

# --- APP INTERFACE ---
st.set_page_config(page_title="PROTO Intake", layout="centered")

st.markdown("### 🏗️ Project Intake Portal")
st.caption("Tracking: PROTO Spreadsheet | Palatine, IL")

# The Form
with st.form("project_entry", clear_on_submit=True):
    st.markdown("**Section 1: General Info**")
    col1, col2 = st.columns(2)
    with col1:
        date_received = st.date_input("1. Date Received", value=datetime.now())
    with col2:
        project_id = st.text_input("2. Project ID", placeholder="XXXX-XXXX")
    
    city_st = st.text_input("3. City, ST", placeholder="e.g. Palatine, IL")

    st.divider()
    
    st.markdown("**Section 2: Material Specs**")
    m1, m2, m3 = st.columns(3)
    with m1:
        fibers = st.text_input("4. Fibers")
    with m2:
        eels = st.text_input("5. Eels")
    with m3:
        reinforcement = st.text_input("6. Reinforcement")

    # Submission Logic
    submit = st.form_submit_button("🚀 Sync to Google Sheets")

    if submit:
        if not project_id:
            st.error("Project ID is required.")
        else:
            # Mapping to your 14-column spreadsheet structure
            # 1:Date, 2:ID, 3:City, 4-8:Empty, 9:Fibers, 10:Empty, 11:Eels, 12:Reinf, 13-14:Empty
            new_row = [
                str(date_received), # 1
                project_id,         # 2
                city_st,            # 3
                "", "", "", "", "", # 4, 5, 6, 7, 8
                fibers,             # 9
                "",                 # 10
                eels,               # 11
                reinforcement,      # 12
                "",                 # 13
                ""                  # 14
            ]

            try:
                with st.spinner("Uploading..."):
                    sheet.append_row(new_row)
                    st.success(f"Project {project_id} added successfully!")
                    st.balloons()
            except Exception as e:
                st.error(f"Failed to sync: {e}")

# Data Preview
if st.checkbox("🔍 View Recent Entries"):
    try:
        data = sheet.get_all_records()
        if data:
            st.dataframe(pd.DataFrame(data).tail(5), use_container_width=True)
    except:
        st.info("No data available to preview yet.")
