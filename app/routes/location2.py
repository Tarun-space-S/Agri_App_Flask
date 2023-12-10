from flask import Blueprint, request, jsonify, render_template
from io import StringIO
from routes.crop import response_data
import requests
import csv
import pandas as pd

location=Blueprint('location2',__name__)

@location.route('/location2', methods=['GET', 'POST'])
def weather():
    return render_template("loc2.html")


@location.route('/get_location2', methods=['POST', 'GET'])
def get_location():
    # Retrieve latitude and longitude from the JSON data
    status=0
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
   
    
    api_key = 'B4M75WHYNBJLHJMNCBEBMDHGQ'

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

         
        else:
            print("No data available for the last 30 days.")
    else:
        print(f"Error: Unable to retrieve weather data. Status code: {response.status_code}")
   
    
    

    response_data.update({'latitude': latitude, 'longitude': longitude})
    status=1
    return jsonify(message='Weather data retrieved',status='1')
