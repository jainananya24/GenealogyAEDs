import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Serial Number Search", layout="centered")

st.title("🔍 Penang AED Genealogy Serial Search")

# Paths for data
FOLDER_PATH = "excel_file"
RESPONSES_CSV = "STM-03005 Rev E.csv"

@st.cache_data
def load_all_data(folder_path):
    all_data = []
    if not os.path.exists(folder_path):
        st.error(f"Error: The folder '{folder_path}' was not found.")
        return pd.DataFrame()

    files = os.listdir(folder_path)
    if not files:
        st.warning(f"No files found in the '{folder_path}' folder.")
        return pd.DataFrame()

    for file in files:
        if file.endswith(".xlsx"):
            file_path = os.path.join(folder_path, file)
            try:
                dtype_spec = {'Parent Serial No': str, 'Serial No': str}
                df = pd.read_excel(file_path, sheet_name="Genealogy", dtype=dtype_spec, engine="openpyxl")
                df["Source File"] = file
                all_data.append(df)
            except Exception as e:
                st.warning(f"Could not read or process {file}: {e}")
    
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

@st.cache_data
def load_responses(csv_path):
    """Loads the Electronic Data Collection CSV responses."""
    if not os.path.exists(csv_path):
        st.error(f"CSV file '{csv_path}' not found.")
        return pd.DataFrame()
    try:
        # Skip the first 2 rows to get to the actual headers
        df = pd.read_csv(csv_path, skiprows=2, dtype={'Serial Number': str})
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

# Load both datasets
df_all = load_all_data(FOLDER_PATH)
df_responses = load_responses(RESPONSES_CSV)

if df_all.empty:
    st.error("No Genealogy data loaded. Check folder and sheet names.")
    st.stop()

serial_input = st.text_input("Enter Parent Serial Number to search:", key="serial_search")

if serial_input:
    parent_serial = serial_input.strip()
    
    # --- Integration: Look up Work Order and Operator ---
    if not df_responses.empty:
        # Search for the serial number in the CSV responses
        response_match = df_responses[df_responses['Serial Number'] == parent_serial]
        
        if not response_match.empty:
            st.success("✅ Work Order & Operator Found")
            # Create columns to display the info neatly
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Work Order Number", response_match['Work Order Number'].iloc[0])
            with col2:
                st.metric("Operator's Name", response_match["Operator's Name"].iloc[0])
        else:
            st.info(f"No Work Order/Operator record found in the CSV for Serial: {parent_serial}")

    # --- Original Genealogy Search Logic ---
    filtered = df_all[df_all['Parent Serial No'] == parent_serial]

    if filtered.empty:
        st.warning(f"No match found in Genealogy for: {parent_serial}")
    else:
        st.subheader("📄 Matching Parts")
        st.dataframe(filtered[['Parent Part No', 'Parent Serial No', 'Part No', 'Serial No', 'Source File']])

        # Extract Serial No for ASI-MS-00071
        asi_00071_rows = filtered[filtered['Part No'] == "ASI-MS-00071"]
        if not asi_00071_rows.empty:
            serial_no_00071 = asi_00071_rows['Serial No'].iloc[0]
            st.info(f"Serial Number for ASI-MS-00071: **{serial_no_00071}**")

            # Trace down to next level
            next_level = df_all[df_all['Parent Serial No'] == serial_no_00071]

            # Look for ASI-MS-01550 and ASI-MS-01599
            part_01550 = next_level[next_level['Part No'] == "ASI-MS-01550"]
            part_01599 = next_level[next_level['Part No'] == "ASI-MS-01599"]

            if not part_01550.empty:
                st.subheader("🔹 ASI-MS-01550 Details")
                st.dataframe(part_01550[['Parent Part No', 'Parent Serial No', 'Part No', 'Serial No']])

            if not part_01599.empty:
                st.subheader("🔹 ASI-MS-01599 Details")
                st.dataframe(part_01599[['Parent Part No', 'Parent Serial No', 'Part No', 'Serial No']])
        else:
            st.info("Part ASI-MS-00071 not found under this parent serial.")

st.markdown("---")
with st.expander("ℹ️ About this App"):
    st.markdown("""
        **Integrated Features:**
        - **Work Order & Operator Info:** Now pulls data from the *Electronic Data Collection Form*.
        - **Genealogy Search:** Searches Excel files for component breakdown.
        - **Automatic Drill-Down:** Automatically finds sub-components for key parts like `ASI-MS-00071`.
    """)
