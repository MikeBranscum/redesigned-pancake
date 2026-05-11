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
streamlit
gspread
google-auth
pandas
[gcp_service_account]
type = "service_account"
project_id = "proto-491818"
private_key_id = "e893b95ce644cecdfcde89627251461ec526c0b2"
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDwOOIzdH15lAas\nQcokcgKPbgT1Pdp3r8Td44KCJpmyaqXqFw3TLdgC5KYmyG3sgJQKOAOi9b/LgAtk\nSaizNWWIGNZ+WNhZ2zcBxX+CszAlt7xWHKF+0CBAwm9bxlqgbFNMgTRMBdQWGVzq\nhbBlViqJZAYx2qV3iD4M1SRGEoNJa/7T8E8fWasVZAFp4piNRfj6cveyCEUYtMVf\npTrevZF2OMEj5IV1Fj7gMuzq4lB71ar47wf6WnrMaJj9XOdp/Cs9+hojUTrEdbDe\n2zL6F3ul1v9C5yPzV7GXE5e4yRqT4uvvSxy6IziPzrqrG/l+H0Se2IdCamZ11wPX\nnwDcjwtvAgMBAAECggEABEywV8Vs/YEVwX2H9bEItLJ+ajlKMLw3pNUOn++67oOU\nJqV0/OOkKyEWjDkoJoSCodAw2HjXjvfivE/JMjPxdkcjh61lae5PhLuZNaipYvNv\n7oaiqVdmTGJuhdD+DEMEFql1Wyr7ic24aQYtixLIvh7JMZk9Pu90VNx3wr1QFj9M\ntdEkQQjG21Qp/Sea4mW54suW4/LBwlpPrJnuY915gxuJfUqI202I/iIOJOacsx9R\ngYKd10BfTyIlE0UHHV87YIREI8Tn+41/FRJYTj62Vi2LZixJptya4Q78dxGSBGSb\nbXIjEfwLDxdH8EA2Wms0KMtdowyaM5wpu6xCcw9vIQKBgQD/SVqa6S6VtML53nQG\nG7wokQeM1iyLSm/OrdfTUyhH4TPRFMYp4S3OlWoFquOht382P7NrJgUEH9zliwyO\nh9fK3dpqlreO2mE4bNv7oCc00DqGpHMP9NmAe44woBDZ/e2+4mLHEl8Da2zTFQzb\n29pWg9CGgFckAcEz3cg9KTRDHwKBgQDw5MB22MDSkmJS/MoB9zBFtpL89v9dBzc1\nWX/uByOABBg7LCPIFJYYoWrHnTz4J6J8ZkYC/xAobq8Cy/1UpkSDWW+jUeH2491V\nntymvsNo54h8LCl6GX/GrY48huzUkCWqT5EkhiHTHxIFXpeaxKFW3O93LIan4/b3\nE8/BAwn9sQKBgGonopmQJWLzS7CDpFN17QQharZRySwSw/N5rqmdhr59EwL6VHzN\nujKRRwkcSpPQrgFs87q2kJdqeHyrGYmbS0x8fHqeOa4ZeRvxiHhV3HfFrtCWSZJ1\nCoy21CW8KcW8JcSedty48vGFFjegJTy3a09WeLu1WocKg8CBlOZ539WZAoGAfLdR\n1bX+joZvFVv/EelyOoV9sC4Io5c6xAokK43SmVKFYQ1HMS1HUFUxvUrw5+FNRG6G\nzMJVETnMrfwCmjLCweYp4DpibLooO03WGxYkgUlt5ivPBYHyH2B3hWqtbpd6iKRN\nFsXC+VTataD1iJFInnogGGkbBg0GLYE6TElQgOECgYB5zUmwzu708d5a+I1ik7Y6\nCyuPuDPEk14IcGUksfaxHZiwJ6lLFhvPC58sgPcgmHqIP9uLoH+r4M1xxtL9/e8k\nfO5Z3jq5Qf+f4/w57QQ/PhBeOSdgs7/yuYMyHTgO2FBKkenAiWzvi/kelncZqq9X\ntSBauTxom/zB//GU3jJUjQ==\n-----END PRIVATE KEY-----\n"
client_email = "pancake-sync@proto-491818.iam.gserviceaccount.com"
client_id = "110172129448680228974"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/pancake-sync%40proto-491818.iam.gserviceaccount.com"
universe_domain = "googleapis.com"

# Ignore local secrets
.streamlit/secrets.toml

# Ignore Python cache
__pycache__/
*.py[cod]

# Ignore the old JSON key if you still have it
service_account.json
