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
        # Accesses credentials from Streamlit Secrets
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

# Logo Section - Using the uploaded RA Logo.jpg
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    try:
        logo = Image.open("RA Logo.jpg")
        st.image(logo, use_container_width=True)
    except:
        st.warning("⚠️ Logo file 'RA Logo.jpg' not found.")

st.markdown("<h3 style='text-align: center; color: black;'>Batch Project Intake Portal</h3>", unsafe_allow_html=True)
st.caption("Standardized Data Entry for PROTO Spreadsheet | Rabine America")
st.divider()

# --- BATCH ENTRY SECTION ---
st.subheader("📝 Step 1: Add or Paste Projects")

# Initialize the data grid with correct column types and names
if 'data_df' not in st.session_state:
    st.session_state.data_df = pd.DataFrame({
        'Project ID': [""] * 10,
        'Concrete Fibers': [""] * 10,
        'Asphalt Fibers': [""] * 10,
        'Eel Qty': [""] * 10,
        'PNA Dowels': [""] * 10,
        'PNA Baskets': [""] * 10
    })

# Editable Data Grid for multiple entries
edited_df = st.data_editor(
    st.session_state.data_df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Project ID": st.column_config.TextColumn("Project ID", required=True),
    }
)

# --- SYNC LOGIC ---
st.divider()
st.subheader("🚀 Step 2: Sync to PROTO")

if st.button("Upload All Valid Rows to Google Sheets"):
    # Filter rows that have at least a Project ID
    df_to_upload = edited_df[edited_df['Project ID'].astype(str).str.strip() != ""]
    
    num_rows = len(df_to_upload)

    if num_rows == 0:
        st.warning("No projects found to upload. Please fill in the Project ID.")
    else:
        batch_data = []
        for index, row in df_to_upload.iterrows():
            # Mapping data to your spreadsheet's 14-column structure
            # Adjust the mapping below as needed based on your master sheet's actual columns
            new_entry = [
                str(datetime.now().strftime("%Y-%m-%d")), # 1: Auto-add today's date
                str(row['Project ID']),                   # 2
                "",                                       # 3: City (leave blank or add to grid)
                "", "", "", "", "",                        # 4, 5, 6, 7, 8
                str(row['Concrete Fibers']),              # 9
                str(row['Asphalt Fibers']),               # 10
                str(row['Eel Qty']),                      # 11
                str(row['PNA Dowels']),                   # 12
                str(row['PNA Baskets']),                  # 13
                ""                                        # 14
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
            st.dataframe(pd.DataFrame(raw_data).tail(10), use_container_width=True)
    except:
        st.info("Could not load preview.")