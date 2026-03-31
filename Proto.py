import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from PIL import Image
from datetime import datetime

# --- SECURE CONNECTION SETUP ---
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception:
        st.error("❌ Secrets Error: Check Streamlit 'Advanced Settings' for gcp_service_account.")
        st.stop()

# Initialize connection
try:
    client = get_gspread_client()
    sh = client.open("PROTO")
    sheet = sh.sheet1
except Exception as e:
    st.error(f"⚠️ Connection Error: {e}")
    st.stop()

# --- APP LAYOUT ---
st.set_page_config(page_title="Rabine Project Portal", layout="wide")

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    try:
        logo = Image.open("rabine_logo.png")
        st.image(logo, use_container_width=True)
    except:
        st.warning("⚠️ Logo file 'rabine_logo.png' not found.")

st.markdown("<h3 style='text-align: center; color: black;'>Batch Project Intake Portal</h3>", unsafe_allow_html=True)
st.caption("Standardized Data Entry for PROTO Spreadsheet | Rabine America")
st.divider()

# --- BATCH ENTRY SECTION ---
st.subheader("📝 Step 1: Add or Paste Projects")

# Fix: Initialize with correct types to avoid StreamlitAPIException
if 'data_df' not in st.session_state:
    st.session_state.data_df = pd.DataFrame({
        'Date Received': [None] * 10,
        'Project ID': [""] * 10,
        'City, State': [""] * 10,
        'Fibers': [""] * 10,
        'Eels': [""] * 10,
        'Reinforcement': [""] * 10
    })

edited_df = st.data_editor(
    st.session_state.data_df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Date Received": st.column_config.DateColumn("Date Received", required=True, format="YYYY-MM-DD"),
        "Project ID": st.column_config.TextColumn("Project ID", required=True),
        "City, State": st.column_config.TextColumn("City, State", required=True),
    }
)

# --- SYNC LOGIC ---
st.divider()
st.subheader("🚀 Step 2: Sync to PROTO")

if st.button("Upload All Valid Rows to Google Sheets"):
    # Drop rows where Date, ID, or City are missing
    df_to_upload = edited_df.dropna(subset=['Date Received', 'Project ID', 'City, State'])
    df_to_upload = df_to_upload[df_to_upload['Project ID'].astype(str).str.strip() != ""]
    
    num_rows = len(df_to_upload)

    if num_rows == 0:
        st.warning("No valid projects found to upload.")
    else:
        batch_data = []
        for index, row in df_to_upload.iterrows():
            new_entry = [
                str(row['Date Received']), # 1
                str(row['Project ID']),    # 2
                str(row['City, State']),   # 3
                "", "", "", "", "",         # 4-8
                str(row['Fibers']),        # 9
                "",                        # 10
                str(row['Eels']),          # 11
                str(row['Reinforcement']), # 12
                "",                        # 13
                ""                         # 14
            ]
            batch_data.append(new_entry)

        try:
            with st.spinner(f"Syncing {num_rows} projects..."):
                sheet.append_rows(batch_data)
                st.success(f"Successfully added {num_rows} projects!")
                st.balloons()
        except Exception as e:
            st.error(f"Failed to sync: {e}")

if st.checkbox("🔍 View Latest Entries in PROTO"):
    try:
        raw_data = sheet.get_all_records()
        if raw_data:
            st.dataframe(pd.DataFrame(raw_data).tail(10), use_container_width=True)
    except:
        st.info("Could not load preview.")
