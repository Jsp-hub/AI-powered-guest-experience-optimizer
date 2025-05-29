import streamlit as st
import mysql.connector
import requests
from mysql.connector import Error

# --- Page Title ---
st.title("AI-Powered Guest Experience Chatbot")

# --- MySQL DB Connection ---
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Me&vru1426",
            database="hotel_db",
            pool_name="hotel_pool",  # Added connection pooling
            pool_size=5,
            pool_reset_session=True
        )
        return conn
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None

# --- Fetch Unique Cities ---
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cities():
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT city FROM all_cities_hotels")
        cities = [row[0] for row in cursor.fetchall()]
        return cities
    except Error as e:
        st.error(f"Error fetching cities: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- Fetch Hotels By City ---
def get_hotels(city):
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute("SELECT hotel_name, price FROM all_cities_hotels WHERE city = %s", (city,))
        return cursor.fetchall()
    except Error as e:
        st.error(f"Error fetching hotels: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- Fetch Restaurants By City ---
def get_restaurants(city):
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute("SELECT Resturants FROM cities_with_restaurants WHERE city = %s", (city,))
        return [row[0] for row in cursor.fetchall()]
    except Error as e:
        st.error(f"Error fetching restaurants: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# [Rest of your existing code remains the same...]

# --- Sidebar Guest Profile ---
st.sidebar.header("Guest Profile Info")
age = st.sidebar.number_input("Age", min_value=18, max_value=100, value=30)
days_stayed = st.sidebar.number_input("Days Stayed", min_value=1, max_value=365, value=1)
loyalty_tier = st.sidebar.selectbox("Loyalty Tier", ["Bronze", "Silver", "Gold", "Platinum"])
room_type = st.sidebar.selectbox("Room Type", ["Standard", "Deluxe", "Suite"])
usage_count = st.sidebar.number_input("Usage Count", min_value=0, max_value=1000, value=0)

# --- User Interaction Flow ---
st.markdown("### I am looking for hotel in:")
selected_city = st.selectbox("Choose a city", get_cities())

if selected_city:
    hotels = get_hotels(selected_city)
    if hotels:
        hotel_options = [f"{name} - ${price}" for name, price in hotels]
        selected_hotel = st.selectbox("Available Hotels:", hotel_options)

        if selected_hotel:
            st.markdown("---")
            st.markdown("### Recommended Restaurants:")
            restaurants = get_restaurants(selected_city)
            for r in restaurants:
                st.markdown(f"- {r}")

            st.markdown("---")
            st.markdown("### Anything to ask?")
            user_message = st.text_input("Type your message:")
# --- Final Step: Collect and Send Data ---
            if st.button("Send to AI Chatbot"):
                user_data = {
                    "age": age,
                    "days_stayed": days_stayed,
                    "loyalty_tier": loyalty_tier,
                    "city": selected_city,
                    "room_type": room_type,
                    "usage_count": usage_count,
                    "selected_hotel": selected_hotel.split(" - ")[0],
                }
                payload = {
                    "message": user_message,
                    "user_data": user_data
                }
                response = requests.post("https://ai-powered-guest-experience-optimizer.onrender.com/chat", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"Bot: {data['reply']}")
                else:
                    st.error("Error contacting the server.")
    else:
        st.warning("No hotels found in the selected city.")
