import psycopg2
import os
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime
import base64

# Load environment variables
load_dotenv()

# Database connection details
DB_HOST = os.getenv("AIVEN_HOST")
DB_PORT = os.getenv("AIVEN_PORT")
DB_NAME = os.getenv("AIVEN_DB")
DB_USER = os.getenv("AIVEN_USER")
DB_PASS = os.getenv("AIVEN_PASSWORD")

def fetch_owners():
    query = "SELECT owner_id, owner_name FROM pledgegtd.owners"
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()
    cur.execute(query)
    owners = cur.fetchall()
    cur.close()
    conn.close()
    return owners

def insert_owner(name, email):
    query = """
    INSERT INTO pledgegtd.owners (owner_name, owner_email)
    VALUES (%s, %s)
    """
    params = (name, email)
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Failed to insert owner: {e}")

def insert_task(verb, direct_object, owner_id):
    query = """
    INSERT INTO pledgegtd.tasks (verb, direct_object, owner_id, createdat, updatedat)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING taskid
    """
    params = (verb, direct_object, owner_id, datetime.now(), datetime.now())
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        cur.execute(query, params)
        taskid = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return taskid
    except Exception as e:
        st.error(f"Failed to insert task: {e}")
        return None

# Convert the image to base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_base64 = get_base64_of_bin_file("beekeeper.png")

# Streamlit UI
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{img_base64}");
        background-size: contain; /* Adjust this as needed */
        background-repeat: no-repeat;
        background-position: center;
        color: #fff;
    }}
    .stButton > button {{
        color: #fff;
        background-color: #000;
        border-radius: 5px;
        padding: 10px;
        border: none;
        margin: 10px;
    }}
    .css-1d391kg {{
        display: none;
    }}
    .stSidebar {{
        background-color: #fff;
    }}
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6, .stSidebar p {{
        color: #000;
    }}
    .fixed-header {{
        position: fixed;
        top: 0;
        width: 100%;
        background-color: #fff;
        z-index: 1000;
        padding: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar content
with st.sidebar:
    st.subheader("Owner Management")
    owners = fetch_owners()
    owner_options = {owner[1]: owner[0] for owner in owners}  # {owner_name: owner_id}

    with st.expander("Add New Owner"):
        with st.form(key="new_owner_form"):
            st.subheader("Add New Owner")
            new_owner_name = st.text_input("Owner Name")
            new_owner_email = st.text_input("Owner Email")
            submit_button = st.form_submit_button("Submit")
            if submit_button:
                if not new_owner_name or not new_owner_email:
                    st.error("Both fields are required.")
                else:
                    insert_owner(new_owner_name, new_owner_email)
                    st.success("Owner added successfully!")
                    # Refresh owner options
                    owners = fetch_owners()
                    owner_options = {owner[1]: owner[0] for owner in owners}

# Main content
st.title("Beekeeper")

# Fixed Header
st.markdown('<div class="fixed-header">Task Management</div>', unsafe_allow_html=True)

# Task Management
st.subheader("Add a New Task")
with st.form(key="task_form", clear_on_submit=True):
    col1, col2 = st.columns([2, 2])
    with col1:
        verb = st.text_input("Work Action (Imperative)")
    with col2:
        direct_object = st.text_input("Work Product (Direct Object)")

    owner_col1, owner_col2 = st.columns([3, 1])
    with owner_col1:
        selected_owner_name = st.selectbox("Work Product Recipient (Indirect Object)", list(owner_options.keys()))
    with owner_col2:
        submit_button = st.form_submit_button("Add Task")
        if submit_button:
            if not verb or not direct_object or not selected_owner_name:
                st.error("All fields are required.")
            else:
                owner_id = owner_options.get(selected_owner_name)
                if not owner_id:
                    st.error("Selected owner is invalid.")
                else:
                    task_id = insert_task(verb, direct_object, owner_id)
                    if task_id:
                        st.success(f"Task added successfully.")
