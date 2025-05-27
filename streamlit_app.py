import streamlit as st
import mysql.connector
import requests

# --- Page Title ---
st.title("AI-Powered Guest Experience Chatbot")

# --- MySQL DB Connection ---
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="your_username",
        password="your_password",
        database="hotel_db"
    )

# --- Fetch Unique Cities ---
@st.cache_data
def get_cities():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT city FROM all_cities_hotels")
    cities = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return cities

# --- Fetch Hotels By City ---
def get_hotels(city):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT hotel_name, price FROM all_cities_hotels WHERE city = %s", (city,))
    hotels = cursor.fetchall()
    cursor.close()
    conn.close()
    return hotels

# --- Fetch Restaurants By City ---
def get_restaurants(city):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT restaurant_name FROM recommended_restaurants WHERE city = %s", (city,))
    restaurants = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return restaurants

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
                response = requests.post("https://your-flask-service.onrender.com/chat", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"Bot: {data['reply']}")
                else:
                    st.error("Error contacting the server.")
    else:
        st.warning("No hotels found in the selected city.")
