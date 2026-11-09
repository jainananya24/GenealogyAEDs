import streamlit as st
import pandas as pd
import os
import io

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

# Helper function to process a single serial for the bulk export
def get_genealogy_rows(parent_serial, df_all, df_responses):
    rows = []
    wo, op = "N/A", "N/A"
    
    # Check responses CSV
    if not df_responses.empty:
        match = df_responses[df_responses['Serial Number'] == parent_serial]
        if not match.empty:
            wo = match['Work Order Number'].iloc[0]
            op = match["Operator's Name"].iloc[0]

    # Level 1 Genealogy
    level_1 = df_all[df_all['Parent Serial No'] == parent_serial]
    
    if level_1.empty:
        # Record that it was searched but nothing was found
        rows.append({
            "Top Level AED Serial": parent_serial, "Work Order": wo, "Operator": op,
            "Hierarchy Level": "Not Found", "Parent Part No": "", "Parent Serial No": "",
            "Part No": "", "Serial No": "", "Source File": ""
        })
        return rows

    for _, row in level_1.iterrows():
        # Append Level 1 parts
        rows.append({
            "Top Level AED Serial": parent_serial, "Work Order": wo, "Operator": op,
            "Hierarchy Level": "Level 1", "Parent Part No": row.get('Parent Part No', ''),
            "Parent Serial No": row.get('Parent Serial No', ''), "Part No": row.get('Part No', ''),
            "Serial No": row.get('Serial No', ''), "Source File": row.get('Source File', '')
        })

        # Level 2 Drill-down for ASI-MS-00071
        if row.get('Part No') == "ASI-MS-00071":
            serial_00071 = row.get('Serial No')
            level_2 = df_all[df_all['Parent Serial No'] == serial_00071]
            
            for _, l2_row in level_2.iterrows():
                if l2_row.get('Part No') in ["ASI-MS-01550", "ASI-MS-01599"]:
                    rows.append({
                        "Top Level AED Serial": parent_serial, "Work Order": wo, "Operator": op,
                        "Hierarchy Level": "Level 2 (Sub of ASI-MS-00071)", 
                        "Parent Part No": l2_row.get('Parent Part No', ''),
                        "Parent Serial No": l2_row.get('Parent Serial No', ''), 
                        "Part No": l2_row.get('Part No', ''),
                        "Serial No": l2_row.get('Serial No', ''), 
                        "Source File": l2_row.get('Source File', '')
                    })
    return rows

# Load both datasets
df_all = load_all_data(FOLDER_PATH)
df_responses = load_responses(RESPONSES_CSV)

if df_all.empty:
    st.error("No Genealogy data loaded. Check folder and sheet names.")
    st.stop()

# --- CREATE TABS FOR UI ---
tab1, tab2 = st.tabs(["🔍 Single Search", "📂 Bulk Search (CSV Export)"])

# ==========================================
# TAB 1: INDIVIDUAL SEARCH (Your original code)
# ==========================================
with tab1:
    serial_input = st.text_input("Enter Parent Serial Number to search:", key="serial_search")

    if serial_input:
        parent_serial = serial_input.strip()
        
        # --- Integration: Look up Work Order and Operator ---
        if not df_responses.empty:
            response_match = df_responses[df_responses['Serial Number'] == parent_serial]
            
            if not response_match.empty:
                st.success("✅ Details Found")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Avive Work Order Number", response_match['Work Order Number'].iloc[0])
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

# ==========================================
# TAB 2: BULK SEARCH EXPORT
# ==========================================
with tab2:
    st.markdown("### Paste Multiple Serial Numbers")
    st.write("Paste your ~650 serial numbers below (one per line or comma-separated), then generate the CSV.")
    
    bulk_input = st.text_area("Bulk Serial Numbers:", height=200, help="Paste a column from Excel here.")
    
    if st.button("Generate Bulk Genealogy CSV"):
        if bulk_input.strip():
            # Parse the inputs (handles both newlines and commas)
            raw_serials = bulk_input.replace(",", "\n").split("\n")
            # Clean and remove empty strings/duplicates while preserving order
            serials_to_search = list(dict.fromkeys([s.strip() for s in raw_serials if s.strip()]))
            
            st.info(f"Processing {len(serials_to_search)} unique serial numbers. Please wait...")
            
            all_bulk_rows = []
            progress_bar = st.progress(0)
            
            for idx, s_num in enumerate(serials_to_search):
                all_bulk_rows.extend(get_genealogy_rows(s_num, df_all, df_responses))
                progress_bar.progress((idx + 1) / len(serials_to_search))
            
            bulk_df = pd.DataFrame(all_bulk_rows)
            
            st.success("✅ Processing Complete!")
            st.dataframe(bulk_df.head(10)) # Show a quick preview
            
            # Convert to CSV for download
            csv = bulk_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full Genealogy CSV",
                data=csv,
                file_name="bulk_genealogy_results.csv",
                mime="text/csv",
            )
        else:
            st.warning("Please enter at least one serial number to process.")

st.markdown("---")

with st.expander("ℹ️ About this App & How to Use"):
    st.markdown("""
        **Integrated Features:**
        - **Work Order & Operator Info:** Now pulls data from the *Electronic Data Collection Form*.
        - **Single Genealogy Search:** Searches Excel files for component breakdown on a visual dashboard.
        - **Bulk Genealogy Export:** Paste hundreds of serials at once to generate a comprehensive, flat CSV report of all levels.
        - **Automatic Drill-Down:** Automatically finds sub-components for key parts like `ASI-MS-00071`.
    """)
