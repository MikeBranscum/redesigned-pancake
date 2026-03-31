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
        # Accesses the secrets you pasted into the Streamlit Cloud Dashboard
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception:
        st.error("❌ Secrets Error: Check Streamlit 'Advanced Settings' for gcp_service_account.")
        st.stop()

# Initialize connection to the PROTO Sheet
try:
    client = get_gspread_client()
    sh = client.open("PROTO")
    sheet = sh.sheet1
except Exception as e:
    st.error(f"⚠️ Connection Error: {e}")
    st.info("Ensure the 'PROTO' sheet is shared with your Service Account email.")
    st.stop()

# --- APP LAYOUT ---
st.set_page_config(page_title="Rabine Project Portal", layout="wide")

# Logo Section
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    try:
        # Ensure your logo file is named exactly 'rabine_logo.png' in your folder
        logo = Image.open("rabine_logo.png")
        st.image(logo, use_container_width=True)
    except:
        st.warning("⚠️ Logo file 'rabine_logo.png' not found in folder.")

st.markdown("<h3 style='text-align: center; color: black;'>Batch Project Intake Portal</h3>", unsafe_allow_html=True)
st.caption("Standardized Data Entry for PROTO Spreadsheet | Rabine America")
st.divider()

# --- BATCH ENTRY SECTION ---
st.subheader("📝 Step 1: Add or Paste Projects")
st.info("Tip: Highlight rows in Excel, copy (Ctrl+C), and paste (Ctrl+V) directly into the grid below.")

# Define the columns for the input grid
columns = ['Date Received', 'Project ID', 'City, State', 'Fibers', 'Eels', 'Reinforcement']

# Create a 10-row empty starting point in session state
if 'data_df' not in st.session_state:
    st.session_state.data_df = pd.DataFrame([[""] * len(columns)] * 10, columns=columns)

# Editable Data Grid
# Note: 'placeholder' removed to ensure compatibility with your Streamlit version
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
    # Filter out any rows that are missing the core required data
    # We drop rows where the essential fields are NaN or empty strings
    df_to_upload = edited_df.dropna(subset=['Date Received', 'Project ID', 'City, State'])
    
    # Ensure we aren't uploading rows that are just empty strings
    df_to_upload = df_to_upload[df_to_upload['Project ID'].astype(str).str.strip() != ""]
    
    num_rows = len(df_to_upload)

    if num_rows == 0:
        st.warning("No valid projects found to upload. Please fill in Date, ID, and City.")
    else:
        batch_data = []
        for index, row in df_to_upload.iterrows():
            # Construct the 14-column row for the spreadsheet
            # 1:Date, 2:ID, 3:City, 4-8:Empty, 9:Fibers, 10:Empty, 11:Eels, 12:Reinf, 13-14:Empty
            new_entry = [
                str(row['Date Received']), # 1
                str(row['Project ID']),    # 2
                str(row['City, State']),   # 3
                "", "", "", "", "",         # 4, 5, 6, 7, 8
                str(row['Fibers']),        # 9
                "",                        # 10
                str(row['Eels']),          # 11
                str(row['Reinforcement']), # 12
                "",                        # 13
                ""                         # 14
            ]
            batch_data.append(new_entry)

        try:
            with st.spinner(f"Syncing {num_rows} projects to PROTO..."):
                sheet.append_rows(batch_data)
                st.success(f"Successfully added {num_rows} projects!")
                st.balloons()
        except Exception as e:
            st.error(f"Failed to sync: {e}")

# --- PREVIEW ---
st.divider()
if st.checkbox("🔍 View Latest Entries in PROTO"):
    try:
        raw_data = sheet.get_all_records()
        if raw_data:
            # Show the last 10 entries added to the sheet
            st.dataframe(pd.DataFrame(raw_data).tail(10), use_container_width=True)
    except:
        st.info("Could not load preview. Check spreadsheet permissions.")
