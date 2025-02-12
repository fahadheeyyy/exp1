# import requests
# import pandas as pd
# from flask import Flask, render_template, request

# app = Flask(__name__)

# def get_climate_data(city, api_key):
#     """Fetch climate data from OpenWeather API."""
#     url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
#     response = requests.get(url)
    
#     if response.status_code != 200:
#         return None  # Handle API failure gracefully
    
#     data = response.json()

#     if data["cod"] != 200:
#         return None  # Return None instead of raising an exception

#     return {
#         "temperature": data["main"]["temp"],
#         # "humidity": data["main"]["humidity"]  # Relative humidity in %
#     }

# def recommend_plants(soil_data, climate_data):
#     """Filter plant recommendations based on soil and climate data."""
#     try:
#         plants = pd.read_csv("plants.csv")
#     except FileNotFoundError:
#         print("Error: plants.csv file not found!")
#         return []

#     plants.columns = plants.columns.str.strip()  # Clean column names
    
#     # Convert numeric columns to float
#     numeric_columns = [
#         "Min pH", "Max pH", "Min Temp (°C)", "Max Temp (°C)", 
#      "Nitrogen (N)", 
#         "Phosphorus (P)", "Potassium (K)", "Organic Matter (%)", 
#         "Soil Depth (cm)"
#     ]
#     for col in numeric_columns:
#         plants[col] = pd.to_numeric(plants[col], errors="coerce")
    
#     # Fill NaN values in text columns
#     plants["Soil Texture"] = plants["Soil Texture"].fillna("")
#     plants["Soil Aeration"] = plants["Soil Aeration"].fillna("")
#     plants["Sunlight"] = plants["Sunlight"].fillna("")
#     plants["Wind Tolerance"] = plants["Wind Tolerance"].fillna("")
#     plants["Frost Tolerance"] = plants["Frost Tolerance"].fillna("")

#     # Filter plants based on conditions
#     condition = (
#         (plants["Min pH"] <= soil_data["pH"]) & 
#         (soil_data["pH"] <= plants["Max pH"]) &
#         (plants["Min Temp (°C)"] <= climate_data["temperature"]) & 
#         (climate_data["temperature"] <= plants["Max Temp (°C)"]) &
#         # (plants["Min Humidity (%)"] <= climate_data["humidity"]) & 
#         # (climate_data["humidity"] <= plants["Max Humidity (%)"]) &
#         (plants["Soil Texture"].str.contains(soil_data["soil_texture"], case=False, na=False)) &
#         (plants["Nitrogen (N)"] <= soil_data["nitrogen"]) &  # Should be <= for minimum requirement
#         (plants["Phosphorus (P)"] <= soil_data["phosphorus"]) &
#         (plants["Potassium (K)"] <= soil_data["potassium"]) &
#         (plants["Organic Matter (%)"] <= soil_data["organic_matter"]) &
#         (plants["Soil Depth (cm)"] <= soil_data["soil_depth"]) &
#         (plants["Soil Aeration"].str.lower() == soil_data["soil_aeration"].lower()) &
#         (plants["Sunlight"].str.lower() == soil_data["sunlight"].lower()) &
#         (plants["Wind Tolerance"].str.lower() == soil_data["wind_tolerance"].lower()) &
#         (plants["Frost Tolerance"].str.lower() == soil_data["frost_tolerance"].lower())
#     )

#     suitable_plants = plants[condition]
    
#     return suitable_plants.to_dict("records")

# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         try:
#             # Get user input and convert to floats
#             city = request.form["city"]
#             soil_pH = float(request.form["soil_pH"])
#             soil_moisture = float(request.form["soil_moisture"])
#             soil_texture = request.form["soil_texture"]
#             nitrogen = float(request.form["nitrogen"])
#             phosphorus = float(request.form["phosphorus"])
#             potassium = float(request.form["potassium"])
#             organic_matter = float(request.form["organic_matter"])
#             soil_depth = float(request.form["soil_depth"])
#             soil_aeration = request.form["soil_aeration"]
#             sunlight = request.form["sunlight"]
#             wind_tolerance = request.form["wind_tolerance"]
#             frost_tolerance = request.form["frost_tolerance"]
#         except KeyError as e:
#             return f"Missing form field: {e}", 400
#         except ValueError as e:
#             return f"Invalid numeric input: {e}", 400

#         # Fetch climate data
#         api_key = "cdc3ec354af4d9e6bf51504498fdc151"  # Replace with your API key
#         climate_data = get_climate_data(city, api_key)

#         # Prepare soil data
#         soil_data = {
#             "pH": soil_pH,
#             "moisture": soil_moisture,
#             "soil_texture": soil_texture,
#             "nitrogen": nitrogen,
#             "phosphorus": phosphorus,
#             "potassium": potassium,
#             "organic_matter": organic_matter,
#             "soil_depth": soil_depth,
#             "soil_aeration": soil_aeration,
#             "sunlight": sunlight,
#             "wind_tolerance": wind_tolerance,
#             "frost_tolerance": frost_tolerance
#         }

#         # Get plant recommendations
#         recommendations = recommend_plants(soil_data, climate_data)

#         return render_template("index.html", recommendations=recommendations)

#     return render_template("index.html", recommendations=None)
# if __name__ == "__main__":
#     app.run(debug=True)
import requests
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

def get_climate_data(city, api_key):
    """Fetch temperature and humidity from OpenWeather API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    
    if response.status_code != 200:
        return None  # Handle API failure gracefully
    
    data = response.json()
    return {"temperature": data["main"]["temp"], "humidity": data["main"]["humidity"]} if data["cod"] == 200 else None

def recommend_plants(soil_climate_data):
    """Filter plant recommendations based on temperature, humidity, moisture, and pH."""
    try:
        plants = pd.read_csv("plants.csv")
    except FileNotFoundError:
        print("Error: plants.csv file not found!")
        return []

    plants.columns = plants.columns.str.strip()  # Clean column names

    # Convert numeric columns to float
    numeric_columns = ["Min pH", "Max pH", "Min Temp (°C)", "Max Temp (°C)", 
                       "Min Humidity (%)", "Max Humidity (%)", "Min Moisture (%)", "Max Moisture (%)"]
    plants[numeric_columns] = plants[numeric_columns].apply(pd.to_numeric, errors="coerce")

    # Apply filtering conditions
    condition = (
        (plants["Min pH"] <= soil_climate_data["pH"]) & (soil_climate_data["pH"] <= plants["Max pH"]) &
        (plants["Min Temp (°C)"] <= soil_climate_data["temperature"]) & 
        (soil_climate_data["temperature"] <= plants["Max Temp (°C)"]) &
        (plants["Min Humidity (%)"] <= soil_climate_data["humidity"]) & 
        (soil_climate_data["humidity"] <= plants["Max Humidity (%)"]) &
        (plants["Min Moisture (%)"] <= soil_climate_data["moisture"]) & 
        (soil_climate_data["moisture"] <= plants["Max Moisture (%)"])
    )

    return plants[condition].to_dict("records")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            city = request.form["city"]
            soil_climate_data = {
                "pH": float(request.form["soil_pH"]),
                "moisture": float(request.form["soil_moisture"])
            }
        except (KeyError, ValueError) as e:
            return f"Invalid input: {e}", 400

        api_key = "cdc3ec354af4d9e6bf51504498fdc151"  # Replace with your API key
        climate_data = get_climate_data(city, api_key)
        if climate_data:
            soil_climate_data.update(climate_data)

        recommendations = recommend_plants(soil_climate_data)
        return render_template("index.html", recommendations=recommendations)

    return render_template("index.html", recommendations=None)

if __name__ == "__main__":
    app.run(debug=True)
