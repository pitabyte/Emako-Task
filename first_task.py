import requests
import datetime
import sqlite3
import argparse
import csv

def validateDate(date):
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        print("Invalid date format. Correct argument format is shown below. (Make sure to omit brackets)\n"
              + "<YYYY:MM:DD>")
        quit()
        
def validateCityname(cityname):
    for letter in cityname:
        if not letter.isalpha():
            print("Name of the city must only consist of letters.\n")
            quit()

DEFAULT_DATE = str(datetime.date.today().isoformat())
DEFAULT_CITY = "Wroclaw"
APPID = "c4136c66fc25aa078c962f0f75e9894a"

msg = '''first_task.py [-h] [--city CITY] [--date DATE] [--file FILE]
        Proper use example below:
        python3 first_task.py -c London -d 2020-06-05 -f textfile
    '''

parser=argparse.ArgumentParser(usage=msg)

parser.add_argument("--city", "-c", help="Looks up weather in a specified city", default=DEFAULT_CITY)
parser.add_argument("--date", "-d", help="Looks up weather on a specified date. Correct format: <YYYY-MM-DD>", default=DEFAULT_DATE)
parser.add_argument("--file", "-f", help="Saves weather in a file of a specified name")

args=parser.parse_args()

date = args.date
cityname = args.city
filename = args.file

validateDate(date)
validateCityname(cityname)

if (date == DEFAULT_DATE):
    currentWeatherResponse = requests.get("http://api.weatherapi.com/v1/current.json?key=c3b267362a66431d882125924233001&q=" + cityname + "&aqi=no")
    data = currentWeatherResponse.json()
    temp = str(data["current"]["temp_c"])
    rain = str(data["current"]["precip_mm"])
    if (filename != None):
        f = open(filename + ".csv", 'w')
        header = ['City','Date','Temperature','Precipitation']
        params = (cityname, date, temp, rain)
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerow(params)
        f.close()
        print("Weather has been saved in a file '" + filename + ".csv'")
    else:
        print("City: " + cityname + " " + date + "\n"
        + "Temperature: " + temp + " degrees Celsius \n"
        + "Precipitation: " + rain + " mm")   
else:   
    con = sqlite3.connect("sqlite.db")
    c = con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS weather(city, date, tempMax, tempMin, rain)")
    c.execute("SELECT tempMax, tempMin, rain FROM weather WHERE city=? AND date=?", (cityname, date))
    stats = c.fetchone()
    if(stats != None):
        tempMax = stats[0]
        tempMin = stats[1]
        rain = stats[2]
        params = (cityname, date, tempMax, tempMin, rain)
        print("Successful retrieval from database")
    else:
        geoResponse = requests.get("http://api.openweathermap.org/geo/1.0/direct?q=" + cityname + "&appid=" + APPID) #checks geolocation of a city
        data = geoResponse.json()
        try:
            lat = str(data[0]["lat"])
            lon = str(data[0]["lon"])
        except IndexError:
            print("Incorrect city name")
            quit()
        weatherResponse = requests.get("https://archive-api.open-meteo.com/v1/archive?" + 
                                       "latitude=" + lat + 
                                       "&longitude=" + lon + 
                                       "&start_date="+ date + 
                                       "&end_date="+ date + 
                                       "&daily=temperature_2m_max,temperature_2m_min,rain_sum&timezone=Europe%2FBerlin")
        data = weatherResponse.json()
        try:
            tempMax = data["daily"]["temperature_2m_max"][0]
            tempMin = data["daily"]["temperature_2m_min"][0]
            rain = data["daily"]["rain_sum"][0]
        except KeyError:
            print("No weather data for these parameters. Make sure input format is correct.")
            quit()
        params = (cityname, date, tempMax, tempMin, rain)
        c.execute("INSERT INTO weather (city, date, tempMax, tempMin, rain) VALUES (?, ?, ?, ?, ?)", (params))
        con.commit()
        
    if (filename != None):
        f = open(filename + ".csv", 'w')
        header = ['City','Date','TemperatureMax','TemperatureMin','Precipitation']
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerow(params)
        f.close()
        print("Weather has been saved in a file '" + filename + ".csv'")
    else:
        print(cityname + " " + date + "\n"
            + "Temperature max: " + str(tempMax) + "\n"
            + "Temperature min " + str(tempMin) + "\n"
            + "Precipitation: " + str(rain))

