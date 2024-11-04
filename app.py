import streamlit as st
import mysql.connector
from mysql.connector import Error

# Page config for wide layout
st.set_page_config(layout="wide")

# Page title
st.title("Receipt View Retriever")

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

try:
    # Create connection using secrets
    conn = mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )

    # Handle button click
    if fetch_button:
        if store_name and account and password and counter_id:
            cursor = conn.cursor()
            
            # First check if user is a Manager
            auth_query = """
                SELECT LevelX 
                FROM accounts 
                WHERE StoreName = %s AND LoginID = %s AND LoginPW = %s
            """
            cursor.execute(auth_query, (store_name, account, password))
            auth_result = cursor.fetchone()
            
            if auth_result and auth_result[0] == 'Manager':
                # If authenticated as Manager, proceed to get ReceiptView and RunningSales
                view_query = """
                    SELECT ReceiptView, RunningSales 
                    FROM settings 
                    WHERE StoreName = %s AND CounterID = %s
                """
                cursor.execute(view_query, (store_name, counter_id))
                result = cursor.fetchone()
                
                if result:
                    # Display RunningSales in bold header
                    st.markdown(f"## Total Sales: {result[1]}")
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
                    st.markdown(f"```\n{result[0]}\n```")
                else:
                    st.error("No data found for the given Store Name and Counter Name")
            else:
                st.error("Access denied. Manager privileges required.")
            
            cursor.close()
        else:
            st.warning("Please fill in all fields")

except Error as e:
    st.error(f"Error connecting to MySQL: {e}")

finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()
