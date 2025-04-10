import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Serial Number Search", layout="centered")

st.title("🔍 Genealogy Serial Search App")

# Folder where your Excel files are stored (in your GitHub repo)
FOLDER_PATH = "excel_files"

@st.cache_data
def load_all_data(folder_path):
    all_data = []
    for file in os.listdir(folder_path):
        if file.endswith(".xlsx"):
            file_path = os.path.join(folder_path, file)
            try:
                df = pd.read_excel(file_path, sheet_name="Genealogy", engine="openpyxl")
                df["Source File"] = file
                all_data.append(df)
            except Exception as e:
                st.warning(f"Could not read {file}: {e}")
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

df_all = load_all_data(FOLDER_PATH)

if df_all.empty:
    st.error("No data found. Please check if your Excel files are in the /data folder.")
    st.stop()

serial_input = st.text_input("Enter Parent Serial Number to search:")

if serial_input:
    parent_serial = serial_input.strip()
    filtered = df_all[df_all['Parent Serial No'] == parent_serial]

    if filtered.empty:
        st.warning(f"No match found for: {parent_serial}")
    else:
        st.subheader("📄 Matching Parts")
        st.dataframe(filtered[['Parent Part No', 'Parent Serial No', 'Part No', 'Serial No', 'Source File']])

        # Extract Serial No for ASI-MS-00071
        if "ASI-MS-00071" in filtered['Part No'].values:
            serial_no_00071 = filtered[filtered['Part No'] == "ASI-MS-00071"]['Serial No'].iloc[0]
            st.info(f"Serial Number for ASI-MS-00071: {serial_no_00071}")

            # Trace down to next level using the Serial Number of ASI-MS-00071
            next_level = df_all[df_all['Parent Serial No'] == serial_no_00071]

            # Look for ASI-MS-01550 and ASI-MS-01599
            part_01550 = next_level[next_level['Part No'] == "ASI-MS-01550"]
            part_01599 = next_level[next_level['Part No'] == "ASI-MS-01599"]

            if not part_01550.empty:
                st.subheader("🔹 ASI-MS-01550 Details")
                st.dataframe(part_01550[['Parent Part No', 'Parent Serial No', 'Part No', 'Serial No']])
            else:
                st.info("No details found for ASI-MS-01550.")

            if not part_01599.empty:
                st.subheader("🔹 ASI-MS-01599 Details")
                st.dataframe(part_01599[['Parent Part No', 'Parent Serial No', 'Part No', 'Serial No']])
            else:
                st.info("No details found for ASI-MS-01599.")
        else:
            st.info("Part ASI-MS-00071 not found under this parent serial.")

st.markdown("---")
st.caption("Developed using free tools: GitHub + Streamlit")
