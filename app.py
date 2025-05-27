from flask import Flask, request, jsonify
import joblib
import spacy
from utils.encoders import encode_loyalty, encode_city, encode_room

app = Flask(__name__)

nlp = spacy.load("en_core_web_sm")

model_upgrade = joblib.load("models/predict_upgrade_acceptance.pkl")
model_offer = joblib.load("models/predict_offer_response.pkl")
model_amenity = joblib.load("models/predict_preferred_amenity.pkl")

def get_intent(text):
    text = text.lower()
    doc = nlp(text)
    if "upgrade" in text:
        return "ask_upgrade"
    elif "offer" in text or "promotion" in text:
        return "ask_offer"
    elif "amenity" in text or "facility" in text:
        return "ask_amenity"
    else:
        return "unknown"

def prepare_features(data):
    age = int(data.get("age", 30))
    days_stayed = int(data.get("days_stayed", 1))
    loyalty_tier = data.get("loyalty_tier", "Bronze")
    room_type = data.get("room_type", "Standard")
    city = data.get("city", "New York")
    usage_count = int(data.get("usage_count", 0))

    return [[
        age,
        days_stayed,
        encode_loyalty(loyalty_tier),
        encode_city(city),
        encode_room(room_type),
        usage_count
    ]], loyalty_tier, room_type

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    user_data = request.json.get("user_data", {})

    intent = get_intent(user_message)
    features, loyalty_tier, room_type = prepare_features(user_data)

    if intent == "ask_upgrade":
        prediction = model_upgrade.predict(features)[0]
        if prediction == 0:
            reply = "You don't have a room upgrade offer."
        else:
            if room_type == "Suite":
                reply = "You already have the best room — no upgrade available."
            elif room_type == "Standard":
                reply = "You are eligible for an upgrade to Deluxe at 10% discount."
            elif room_type == "Deluxe":
                reply = "You are eligible for an upgrade to Suite at 20% discount."
            else:
                reply = "Upgrade option not available."

    elif intent == "ask_offer":
        prediction = model_offer.predict(features)[0]
        if prediction == 0:
            reply = "You are not eligible for any offer."
        else:
            if room_type == "Deluxe" and loyalty_tier == "Gold":
                reply = "You are eligible for a complimentary access to Meals."
            elif room_type == "Suite" and loyalty_tier == "Platinum":
                reply = "You are eligible for access to Premium Lounge."
            else:
                reply = "You are eligible for a personalized welcome gift."

    elif intent == "ask_amenity":
        amenity_map = {0: "Bar", 1: "Gym", 2: "Lounge", 3: "Pool", 4: "Restaurant", 5: "Spa"}
        prediction = model_amenity.predict(features)[0]
        reply = f"You have access to our {amenity_map.get(prediction, 'Bar')} facility."
        

    else:
        reply = "Sorry, I didn't understand. Please ask about upgrades, offers, or amenities."

    return jsonify({"reply": reply, "intent": intent})

if __name__ == "__main__":
    app.run(debug=True)
