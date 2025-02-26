import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Configure the Streamlit app
st.set_page_config(page_title="Data Sweeper", layout="wide")

# Custom CSS for Dark Mode Styling
st.markdown("""
<style>
    .block-container { padding: 3rem 2rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); }
    h1, h2, h3, h4, h5, h6 { color:#fff; }
    .stButton>button { border: none; border-radius: 8px; background-color: #0078D7; color: white; padding: 0.75rem 1.5rem; font-size: 1rem; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4); }
    .stButton>button:hover { background-color: #005a9e; cursor: pointer; }
    .stDataFrame, .stTable { border-radius: 10px; overflow: hidden; }
    .css-1aumxhk, .css-18e3th9 { text-align: left; color: white; }
    .stRadio>label, .stCheckbox>label { color: white; font-weight: bold; }
    .stDownloadButton>button { background-color: #28a745; color: white; }
    .stDownloadButton>button:hover { background-color: #218838; }
</style>
""", unsafe_allow_html=True)

# Title and Description
st.title("📊 Advanced Data Sweeper")
st.write("Transform and clean your CSV and Excel files with ease, featuring built-in data visualization.")

# File Uploader
uploaded_files = st.file_uploader("📁 Upload CSV or Excel files:", type=["csv", "xlsx"], accept_multiple_files=True)

def process_file(file):
    file_extension = os.path.splitext(file.name)[-1].lower()
    try:
        df = pd.read_csv(file) if file_extension == ".csv" else pd.read_excel(file)
    except Exception as e:
        st.error(f"❌ Error processing {file.name}: {e}")
        return

    st.write(f"📄 File Name:** {file.name}")
    st.write(f"📏 File Size:** {file.size / 1024:.2f} KB")
    st.write("🔍 *Preview of the Uploaded File:*")
    st.dataframe(df.head())

    # Data Summary
    if st.checkbox(f"Show Data Summary for {file.name}"):
        st.write(df.describe())

    # Data Cleaning Options
    st.subheader("🛠 Data Cleaning Options")
    if st.checkbox(f"Enable Cleaning for {file.name}"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Remove Duplicates ({file.name})"):
                initial_count = df.shape[0]
                df.drop_duplicates(inplace=True)
                st.success(f"✅ Removed {initial_count - df.shape[0]} duplicate rows.")
        with col2:
            if st.button(f"Fill Missing Values ({file.name})"):
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                st.success("✅ Missing values filled with column means.")

    # Column Selection
    st.subheader("🎯 Select Columns to Convert")
    columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
    df = df[columns]

    # Visualization
    st.subheader("📊 Data Visualization")
    if st.checkbox(f"Show Visualization for {file.name}"):
        if df.select_dtypes(include='number').shape[1] >= 1:
            st.bar_chart(df.select_dtypes(include='number'))
        else:
            st.warning("⚠ No numeric columns available for visualization.")

    # Conversion Options
    st.subheader("🔄 Conversion Options")
    conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
    if st.button(f"Convert {file.name}"):
        buffer = BytesIO()
        file_name = file.name.replace(file_extension, f".{conversion_type.lower()}")
        mime_type = "text/csv" if conversion_type == "CSV" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        if conversion_type == "CSV":
            df.to_csv(buffer, index=False)
        else:
            df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)

        st.download_button(
            label=f"⬇ Download {file.name} as {conversion_type}",
            data=buffer,
            file_name=file_name,
            mime=mime_type
        )

# Process each uploaded file
if uploaded_files:
    for file in uploaded_files:
        process_file(file)

st.success("🎉 All files processed successfully!")
