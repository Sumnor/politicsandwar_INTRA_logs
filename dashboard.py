import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
from datetime import datetime

DB_FILE = "pnw_logs.db"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        giver TEXT,
        receiver TEXT,
        resource TEXT,
        amount REAL,
        date TEXT
    )''')
    conn.commit()
    conn.close()

def add_log(giver, receiver, resource, amount):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO logs (giver, receiver, resource, amount, date) VALUES (?, ?, ?, ?, ?)",
              (giver, receiver, resource, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_logs():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM logs", conn)
    conn.close()
    return df

# ---------- APP ----------
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login
if not st.session_state.logged_in:
    st.title("🏛 Politics & War Transaction Tracker")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "sumnor_the_lazy" and password == "Sumnor_INTRA|2025|06|12":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

else:
    st.title("🏛 Politics & War Transaction Tracker")
    st.write("Logged in as **sumnor_the_lazy**")

    # View logs
    st.header("📜 Transaction Logs")
    logs_df = get_logs()
    if logs_df.empty:
        st.write("No logs found.")
    else:
        st.dataframe(logs_df)

    # Add logs
    st.subheader("➕ Add New Transaction")
    giver = st.text_input("Giver")
    receiver = st.text_input("Receiver")
    resource = st.selectbox("Resource", ["Money", "Food", "Oil", "Uranium", "Steel", "Aluminum", "Gasoline", "Munitions"])
    amount = st.number_input("Amount", min_value=0.0, step=0.1)
    if st.button("Add Log"):
        add_log(giver, receiver, resource, amount)
        st.success("✅ Transaction added!")
        st.rerun()

    # Breakdown Button
    if st.button("📊 Show Breakdown"):
        if logs_df.empty:
            st.warning("No data to show.")
        else:
            st.subheader("Breakdown of Transactions")

            # Total by Giver
            giver_chart = alt.Chart(logs_df).mark_bar().encode(
                x=alt.X("giver", sort="-y"),
                y="sum(amount)",
                color="giver"
            ).properties(title="Total Given by Each Player")
            st.altair_chart(giver_chart, use_container_width=True)

            # Total by Resource
            resource_chart = alt.Chart(logs_df).mark_arc().encode(
                theta="sum(amount)",
                color="resource",
                tooltip=["resource", "sum(amount)"]
            ).properties(title="Distribution by Resource")
            st.altair_chart(resource_chart, use_container_width=True)

            # Transactions over time
            logs_df["date"] = pd.to_datetime(logs_df["date"])
            time_chart = alt.Chart(logs_df).mark_line(point=True).encode(
                x="date:T",
                y="sum(amount)",
                color="resource"
            ).properties(title="Transactions Over Time")
            st.altair_chart(time_chart, use_container_width=True)

    # Logout
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
