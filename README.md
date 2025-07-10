# Penang AED Genealogy Serial Search
A simple and efficient web application built with Streamlit to search for component genealogy data and lot number within a collection of Excel files. This tool is designed to quickly trace the relationship between parent assemblies and their sub-components by searching for a parent serial number.

# 📜 Description
In manufacturing and assembly processes, it's crucial to maintain a clear record of which sub-components are installed in a parent unit. This is often referred to as product genealogy. This application solves the challenge of manually searching through numerous Excel spreadsheets to find this information.
>
The "Penang AED Genealogy Serial Search" app provides a user-friendly interface to:
>
- Instantly search for a specific "Parent Serial Number" across all relevant Excel files.
> 
- Display all matching sub-components associated with that parent serial number.
>
- Automatically perform a multi-level trace-down for specific critical parts (e.g., ASI-MS-00071) to find their own sub-components.
>
- The application is built to be robust, handling potential file errors and ensuring that serial numbers are treated as text to avoid data type issues.

# ✨ Features
- Centralized Searching: Searches all .xlsx files located in a designated folder.
>
- Fast & Efficient: Caches the loaded data to provide near-instant results on subsequent searches.
>
- Specific Part Trace-Down: Automatically drills down to find details for key parts like ASI-MS-01550 and ASI-MS-01599 if their parent ASI-MS-00071 is found.
>
- User-Friendly Interface: Clean and simple UI powered by Streamlit.
>
- Error Handling: Gracefully handles missing folders, empty directories, and corrupted files.
>
- Data Integrity: Reads serial numbers as strings to prevent common Excel data type conversion errors (e.g., dropping leading zeros or converting to scientific notation).

# ⚙️ How It Works
- Data Loading: On startup, the application scans the excel_file/ directory for any files ending with .xlsx.
>
- Aggregation: It reads the "Genealogy" sheet from each Excel file, treating the serial number columns as text, and concatenates them into a single, searchable pandas DataFrame. The source filename is added to each row for easy reference.
>
- Caching: The combined DataFrame is cached in memory. This means the Excel files are only read once, making subsequent searches much faster.
>
- User Input: The user enters a "Parent Serial Number" into the search box.
>
- Filtering & Display: The application filters the main DataFrame to find all rows where the Parent Serial No column matches the user's input.
>
- Drill-Down Logic: If a match is found, it specifically looks for the component ASI-MS-00071. If this part exists, it uses its Serial No to perform a second search to find its own child components, displaying details for ASI-MS-01550 and ASI-MS-01599.


# Folder Structure
The application expects a specific folder structure to work correctly. You must create a folder named excel_file in the same directory as your Python script (app.py or similar).

GenealogyAEDs/
>
├── excel_file/
>
│   ├── data_file_1.xlsx
>
│   ├── data_file_2.xlsx
>
│   └── ...
>
├── app.py              <-- Streamlit script
>
└── requirements.txt
>

- Important: Place all your genealogy Excel files inside the excel_file folder.


# 📊 Data Requirements
For the application to work correctly, your Excel files must meet the following criteria:
>
File Format: Must be .xlsx.
>
Sheet Name: Must contain a sheet named exactly Genealogy.
>
Required Columns: The Genealogy sheet must contain at least the following columns:
>
Parent Part No
>
Parent Serial No
>
Part No
>
Serial No
>
