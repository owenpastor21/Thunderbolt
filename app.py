import streamlit as st
import requests
import json

# Page config for wide layout
st.set_page_config(layout="wide")

# Page title
st.title("Receipt View Retriever V2")

# API base URL
API_BASE_URL = "http://owenpastor21-001-site10.atempurl.com/QueryExecutor.aspx"  # Replace with your actual API URL

# Function to send requests to the API
def execute_query(query, parameters):
    try:
        # Construct the payload
        payload = {
            "Query": query,
            "Parameters": parameters
        }
        
        # Make the request to the API
        response = requests.post(API_BASE_URL, json=payload)
        
        # Check for successful response
        if response.status_code == 200:
            # Return JSON response from the API
            return response.json()
        else:
            st.error(f"API error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None

# Create a container for the header section
with st.container():
    # Create two rows of inputs using columns
    col1, col2 = st.columns(2)
    
    with col1:
        store_name = st.text_input("Store Name")
        counter_id = st.text_input("Counter Name")
    
    with col2:
        account = st.text_input("Account")
        password = st.text_input("Password", type="password")

    # Center the button using columns
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        fetch_button = st.button("Get Receipt View", use_container_width=True)

# Add a separator
st.markdown("<hr>", unsafe_allow_html=True)

# Handle button click
if fetch_button:
    if store_name and account and password and counter_id:
        # First, check if the user has Manager privileges
        auth_query = """
            SELECT LevelX 
            FROM accounts 
            WHERE StoreName = %s AND LoginID = %s AND LoginPW = %s
        """
        auth_params = [{"StoreName": store_name}, {"LoginID": account}, {"LoginPW": password}]
        auth_result = execute_query(auth_query, auth_params)
        
        if auth_result and auth_result.get("data"):
            level = auth_result["data"][0].get("LevelX")
            
            if level == "Manager":
                # If authenticated as Manager, proceed to get ReceiptView and RunningSales
                view_query = """
                    SELECT ReceiptView, RunningSales 
                    FROM settings 
                    WHERE StoreName = %s AND CounterID = %s
                """
                view_params = [{"StoreName": store_name}, {"CounterID": counter_id}]
                result = execute_query(view_query, view_params)
                
                if result and result.get("data"):
                    result_data = result["data"][0]
                    
                    # Display RunningSales in bold header
                    st.markdown(f"## Total Sales: {result_data.get('RunningSales')}")
                    st.markdown("<hr>", unsafe_allow_html=True)  # Add separator line
                    
                    # Display the receipt view with monospace font
                    st.markdown("""
                        <style>
                        .receipt-view {
                            font-family: 'Courier New', Courier, monospace;
                            white-space: pre;
                            overflow-x: auto;
                            font-size: 14px;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    # Using markdown with code block for monospace display
                    st.markdown(f"```\n{result_data.get('ReceiptView')}\n```")
                else:
                    st.error("No data found for the given Store Name and Counter Name")
            else:
                st.error("Access denied. Manager privileges required.")
        else:
            st.error("Authentication failed or user not authorized as Manager.")
    else:
        st.warning("Please fill in all fields")
