
import streamlit as st
import pandas as pd
import os

# Folder where Excel files are stored (relative path after upload to GitHub)
excel_folder = "excel_files"

# Gather all Excel files
files = [f for f in os.listdir(excel_folder) if f.endswith(".xlsx")]

@st.cache_data
def load_all_data():
    all_data = pd.DataFrame()
    for file in files:
        try:
            df = pd.read_excel(os.path.join(excel_folder, file), sheet_name="Genealogy", engine="openpyxl")
            df['Source File'] = file
            all_data = pd.concat([all_data, df], ignore_index=True)
        except Exception as e:
            st.error(f"⚠️ Error reading {file}: {e}")
    return all_data

st.title("🔍 Serial Number Lookup")

data = load_all_data()

serial = st.text_input("Enter a Parent Serial Number")

if serial:
    filtered = data[data['Parent Serial No'] == serial]
    if filtered.empty:
        st.warning("No matching record found.")
    else:
        st.success(f"Found {len(filtered)} records!")
        st.dataframe(filtered[['Parent Part No', 'Parent Serial No', 'Part No', 'Serial No', 'Source File']])
