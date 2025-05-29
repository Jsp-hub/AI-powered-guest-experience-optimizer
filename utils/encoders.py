import joblib
import os

# Get the absolute path to city_encoder.joblib (works locally and on Render)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Points to utils/
CITY_ENCODER_PATH = os.path.join(CURRENT_DIR, "city_encoder.joblib")

# Load the encoder or set to None
try:
    city_encoder = joblib.load(CITY_ENCODER_PATH)  # Now uses the correct path
except FileNotFoundError:
    city_encoder = None

    
# Load the encoder or set to None
# try:
#     city_encoder = joblib.load('city_encoder.joblib')
# except FileNotFoundError:
#     city_encoder = None

# use this block to see if your city_encoder.joblib is working and succesfully encodes the cities.
# # Print all cities with their encoded values 
# if hasattr(city_encoder, 'classes_'):
#     print("\nCity Encodings:")
#     print("--------------")
#     for code, city in enumerate(city_encoder.classes_):
#         print(f"{city}: {code}")
# else:
#     print("Warning: The loaded object doesn't have city encoding information")


def encode_city(city):
    if city_encoder is None:
        raise ValueError("City encoder not loaded. Provide city_encoder.joblib.")
    
    try:
        return int(city_encoder.transform([city])[0])
    except ValueError:
        return -1  # Default for unknown cities




def encode_loyalty(tier):
    mapping = {"none": 0, "platinum": 1, "gold": 2, "silver":3}
    return mapping.get(tier, 0)



def encode_room(room):
    mapping = {"Standard": 0, "Deluxe": 1, "Suite": 2}
    return mapping.get(room, 0)


# def encode_room(amenity):
#     mapping = {"Bar": 0, "Gym": 1, "Lounge": 2,"Pool": 3, "Restaurant": 4, "Spa": 5 }     #labelencoder by alphabatic order
#     return mapping.get(amenity, 0)
