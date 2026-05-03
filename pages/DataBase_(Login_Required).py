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
            st.dataframe(df)

        except Exception as e:
            st.error(f"Query failed: {e}")
else:
    st.title("DataBase")
    st.caption("This page is only accessible to authenticated users. Please log in to view the content.")



                                    