import pickle
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import pymysql
import mysql.connector
import boto3
import json

if st.session_state.get("authentication_status"):
    st.title("DataBase")
    # -----------------------------
    # Load DB credentials from AWS Secrets Manager
    # -----------------------------
    @st.cache_data
    def get_secret():

        secret_name = "lightsail/mysql"
        region_name = "eu-west-2"

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])

    secret = get_secret()

    # -----------------------------
    # Create DB connection
    # -----------------------------
    @st.cache_resource
    def get_connection():
        return mysql.connector.connect(
            host=secret["host"],
            user=secret["username"],
            password=secret["password"],
            database=secret["dbname"],
            port=secret["port"]
        )

    conn = get_connection()

    # -----------------------------
    # Streamlit UI
    # -----------------------------
    st.title("Lightsail MySQL Viewer (Read-Only)")

    #limit = st.number_input("Rows limit", min_value=1, max_value=2500, value=100)

    if "reload_table" not in st.session_state:
        st.session_state.reload_table = 0

    if st.button("Load Table"):
        st.session_state.reload_table += 1

    if st.session_state.reload_table > 0:
        try:
            query = "SELECT * FROM Field_Data_tbl WHERE 1=1 LIMIT 5000"

            # Reconnect if connection has dropped
            if not conn.is_connected():
                conn.reconnect()

            df = pd.read_sql(query, conn)

            df = df.drop(
                columns=['ID', 'Date_Reported', 'Report_Number', 'Test_Name'],
                errors='ignore'
            )

            st.success(f"Loaded {len(df)} rows")

            # Dynamic filters
            col1, col2, col3 = st.columns(3)

            with col1:
                test_type_filter = st.multiselect(
                    "Filter by Test_Type",
                    options=df['Test_Type'].unique() if 'Test_Type' in df.columns else [],
                    default=None,
                    key="test_type_filter"
                )

            with col2:
                material_type_filter = st.multiselect(
                    "Filter by Material_Type",
                    options=df['Material_Type'].unique() if 'Material_Type' in df.columns else [],
                    default=None,
                    key="material_type_filter"
                )

            with col3:
                date_tested_filter = st.multiselect(
                    "Filter by Date_Tested",
                    options=sorted(pd.to_datetime(df['Date_Tested']).dt.date.unique()) if 'Date_Tested' in df.columns else [],
                    default=None,
                    key="date_tested_filter"
                )

            location_filter = st.radio(
                "Filter by Location",
                options=["All", "Core", "Shoulder", "Formation", "Sand"],
                horizontal=True,
                key="location_filter"
            )

            # Apply filters
            filtered_df = df.copy()

            if test_type_filter:
                filtered_df = filtered_df[filtered_df['Test_Type'].isin(test_type_filter)]

            if material_type_filter:
                filtered_df = filtered_df[filtered_df['Material_Type'].isin(material_type_filter)]

            if date_tested_filter:
                filtered_df = filtered_df[pd.to_datetime(filtered_df['Date_Tested']).isin(date_tested_filter)]

            if location_filter == "Core":
                filtered_df = filtered_df[
                    (filtered_df['Location_ID'].str.contains('core', case=False, na=False)) &
                    (~filtered_df['Location_ID'].str.contains('Formation', case=False, na=False))
                ]
            elif location_filter == "Shoulder":
                filtered_df = filtered_df[
                    (filtered_df['Location_ID'].str.contains('shoulder', case=False, na=False)) &
                    (~filtered_df['Location_ID'].str.contains('Formation', case=False, na=False))
                ]
            elif location_filter == "Formation":
                filtered_df = filtered_df[
                    (filtered_df['Location_ID'].str.contains('formation', case=False, na=False))
                ]    
            elif location_filter == "Sand":
                filtered_df = filtered_df[
                    (filtered_df['Material_Type'].str.contains('sand', case=False, na=False)) |
                    (filtered_df['Material_Type'].str.contains('0-4', case=False, na=False)) |
                    (filtered_df['Material_Type'].str.contains('brett', case=False, na=False)) |
                    (filtered_df['Material_Type'].str.contains('tarmac', case=False, na=False)) |
                    (filtered_df['Material_Type'].str.contains('kendall', case=False, na=False)) |
                    (filtered_df['Material_Type'].str.contains('blanket', case=False, na=False)) |
                    (filtered_df['Material_Type'].str.contains('drain', case=False, na=False)) |
                    (filtered_df['Material_Type'].str.contains('bkt', case=False, na=False)) |
                    (filtered_df['Material_Type'].str.contains('FD', case=False, na=False))
                ]
            elif location_filter != "All":
                filtered_df = filtered_df[filtered_df['Location_ID'].str.contains(location_filter, case=False, na=False)]

            st.dataframe(filtered_df)

        except Exception as e:
            st.error(f"Query failed: {e}")

else:
    st.title("DataBase")
    st.caption("This page is only accessible to authenticated users. Please log in to view the content.")



                                    