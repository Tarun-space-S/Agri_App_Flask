from flask import Blueprint, request, jsonify, render_template
from io import StringIO
from routes.crop import response_data
import requests
import csv
import time

location=Blueprint('location',__name__)

@location.route('/location', methods=['GET', 'POST'])
def weather():
    return render_template("location.html")


@location.route('/get_location', methods=['POST', 'GET'])
def get_location():
    # Retrieve latitude and longitude from the JSON data
    status=0
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    address=data.get('address')
    api_key = 'ANG7KD72UDXLEX2RJJZFZ4J4R'
    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{latitude},{longitude}/last30days?unitGroup=metric&include=days&key={api_key}&contentType=csv'

    response = requests.get(url)

    if response.status_code == 200:
        csv_data = response.text
        csv_file = StringIO(csv_data)
        csv_reader = csv.DictReader(csv_file)

        # Initialize variables to store cumulative values
        total_temperature = 0
        total_humidity = 0
        total_rainfall = 0
        num_days = 0

        for row in csv_reader:
            date = row['datetime']
            temperature = float(row['temp'])  # Convert to float
            humidity = float(row['humidity'])  # Convert to float
            rainfall = float(row['precip'])  # Convert to float

            # Accumulate values
            total_temperature += temperature
            total_humidity += humidity
            total_rainfall += rainfall
            num_days += 1

        # print(num_days)
        if num_days > 0:
            # Calculate the average temperature, humidity, and rainfall
            average_temperature = round(total_temperature / num_days,2)
            average_humidity = round(total_humidity / num_days, 2)
            monthly_rainfall = round(total_rainfall,2)
            response_data.update({'average_temperature':average_temperature,'average_humidity':average_humidity,'monthly_rainfall':monthly_rainfall}) 

            # print(f"Average Temperature: {average_temperature}°C")
            # print(f"Average Humidity: {average_humidity}%")
            # print(f"Monthly Rainfall: {monthly_rainfall} mm")
        else:
            print("No data available for the last 30 days.")
    else:
        print(f"Error: Unable to retrieve weather data. Status code: {response.status_code}")
    # Process the data (e.g., store it in a database, perform computations, etc.)
    # Return a response (optional)

    

    response_data.update({'message': 'Location data received', 'latitude': latitude, 'longitude': longitude,'address':address})
    time.sleep(5)
    status=1
    return jsonify(response_data,status)
