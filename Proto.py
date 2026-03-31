import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from PIL import Image

# --- SECURE CONNECTION SETUP ---
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception:
        st.error("❌ Secrets Error: Check Streamlit Settings.")
        st.stop()

# Initialize connection
try:
    client = get_gspread_client()
    sh = client.open("PROTO")
    sheet = sh.sheet1
except Exception as e:
    st.error(f"⚠️ Connection Error: {e}")
    st.stop()

# --- APP LAYOUT (Logo Integration) ---
st.set_page_config(page_title="Rabine Portal", layout="wide")

# Center and display the Rabine logo
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    logo = Image.open("rabine_logo.png")
    st.image(logo, use_column_width=True)

st.markdown("<h3 style='text-align: center; color: black;'>Batch Project Intake Portal</h3>", unsafe_allow_index=True)
st.caption("Auto-Populating PROTO Spreadsheet | Standardized Data Entry")
st.divider()

# --- THE BATCH ENTRY SECTION ---
st.subheader("📝 Step 1: Add or Paste Projects Below")
st.write("You can paste multiple rows from a spreadsheet or type them in. Required fields: Date, ID, City, State.")

# Create an empty template of 10 rows for the editable grid
template_rows = 10
columns = ['1. Date Received', '2. Project ID', '3. City, State', '4. Fibers', '5. Eels', '6. Reinforcement']
empty_data = {col: [""] * template_rows for col in columns}
df_template = pd.DataFrame(empty_data)

# Use Streamlit's data_editor for "Excel-like" entry
# This allows copy/paste (Ctrl+C, Ctrl+V) and multi-select.
edited_df = st.data_editor(
    df_template,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "1. Date Received": st.column_config.DateColumn("Date Received", required=True),
        "2. Project ID": st.column_config.TextColumn("Project ID", placeholder="XXXX-XXXX", required=True),
        "3. City, State": st.column_config.TextColumn("City, State", placeholder="City, State", required=True),
    }
)

# --- THE SYNC SECTION ---
st.divider()
st.subheader("🚀 Step 2: Review and Sync")
sync_btn = st.button("Upload All valid Projects to PROTO")

if sync_btn:
    # 1. Clean up the data: Remove rows that don't have the required fields
    df_to_upload = edited_df.dropna(subset=['1. Date Received', '2. Project ID', '3. City, State']).reset_index(drop=True)
    
    # Check if there is anything left to upload
    num_projects = len(df_to_upload)
    
    if num_projects == 0:
        st.warning("No projects were added. Make sure required fields (Date, ID, City) are filled.")
    else:
        st.info(f"Preparing to upload {num_projects} projects...")
        
        # 2. Build the list of lists for gspread.append_rows()
        batch_rows = []
        for index, row in df_to_upload.iterrows():
            # Standardize date to string
            date_str = str(row['1. Date Received'])
            
            # MAPPING TO YOUR 14 Headings:
            # 1:Date, 2:ID, 3:City, 4-8:Empty, 9:Fibers, 10:Empty, 11:Eels, 12:Reinf, 13-14:Empty
            mapped_row = [
                date_str,             # 1
                row['2. Project ID'], # 2
                row['3. City, State'], # 3
                "", "", "", "", "",    # 4, 5, 6, 7, 8
                row['4. Fibers'],      # 9
                "",                    # 10
                row['5. Eels'],        # 11
                row['6. Reinforcement'], # 12
                "",                    # 13
                ""                     # 14
            ]
            batch_rows.append(mapped_row)

        # 3. Sync everything in one shot
        try:
            with st.spinner(f"Batch uploading {num_projects} projects..."):
                sheet.append_rows(batch_rows)
                st.success(f"Successfully added {num_projects} new projects to PROTO!")
                st.balloons()
        except Exception as e:
            st.error(f"⚠️ Batch Upload Failed: {e}")

# --- RECENT ACTIVITY ---
st.divider()
if st.checkbox("🔍 View Latest PROTO Entries"):
    data = sheet.get_all_records()
    if data:
        st.dataframe(pd.DataFrame(data).tail(10), use_container_width=True)
