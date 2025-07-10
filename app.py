import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Serial Number Search", layout="centered")

st.title("🔍 Penang AED Genealogy Serial Search")

# Folder where your Excel files are stored
FOLDER_PATH = "excel_file"

@st.cache_data
def load_all_data(folder_path):
    all_data = []
    # Check if the folder exists
    if not os.path.exists(folder_path):
        st.error(f"Error: The folder '{folder_path}' was not found. Please make sure it's in the correct location.")
        return pd.DataFrame()

    files = os.listdir(folder_path)
    if not files:
        st.warning(f"No files found in the '{folder_path}' folder.")
        return pd.DataFrame()

    for file in files:
        if file.endswith(".xlsx"):
            file_path = os.path.join(folder_path, file)
            try:
                # --- KEY CHANGE HERE ---
                # Specify the data type for serial number columns as string during read
                dtype_spec = {
                    'Parent Serial No': str,
                    'Serial No': str
                }
                df = pd.read_excel(file_path, sheet_name="Genealogy", dtype=dtype_spec, engine="openpyxl")
                df["Source File"] = file
                all_data.append(df)
            except Exception as e:
                st.warning(f"Could not read or process {file}: {e}")
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

df_all = load_all_data(FOLDER_PATH)

# Add some debugging to see what's loaded
# st.write("Data loaded successfully. Here's a preview:")
# st.write(df_all.head())
# st.write(df_all.info())

if df_all.empty:
    st.error("No data could be loaded. Please check the file paths, file names, and sheet names ('Genealogy').")
    st.stop()

serial_input = st.text_input("Enter Parent Serial Number to search:", key="serial_search")

if serial_input:
    parent_serial = serial_input.strip()
    # No need to convert here anymore since it's loaded as a string
    filtered = df_all[df_all['Parent Serial No'] == parent_serial]

    if filtered.empty:
        st.warning(f"No match found for: {parent_serial}")
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
            else:
                st.info("No details found for ASI-MS-01550 in the next level.")

            if not part_01599.empty:
                st.subheader("🔹 ASI-MS-01599 Details")
                st.dataframe(part_01599[['Parent Part No', 'Parent Serial No', 'Part No', 'Serial No']])
            else:
                st.info("No details found for ASI-MS-01599 in the next level.")
        else:
            st.info("Part ASI-MS-00071 not found under this parent serial.")

st.markdown("---")
with st.expander("ℹ️ About this App & How to Use"):
    st.markdown("""
        **What does this app do?**
        
        This application allows you to search for component genealogy data within a collection of Excel files. 
        You can enter a parent serial number to find all its associated sub-components. The app also automatically
        traces down specific critical parts to find their sub-components.
    """)
    st.markdown("""
        **How to use it:**
        
        1.  **Enter a Serial Number:** Type or paste the `Parent Serial Number (AED Serial Number)` you want to search for in the text box above.
        2.  **View Results:** The application will display all matching parts found in the Excel files.
        3.  **Check Drill-Down:** If specific parts like `ASI-MS-00071` are found, their sub-components will be displayed in separate sections below.
    """)

