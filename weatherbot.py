#!/usr/bin/env python

"""
juniper's first foray into weather hacking.

Requires:
  pip install geocode

  openweathermap free account and a valid API code (which I am not checking in)
  You can get an account here: https://home.openweathermap.org/users/sign_up
  And your api keys will be here: https://home.openweathermap.org/api_keys

Sources:
  http://geocoder.readthedocs.io
  http://github.com/ZeevG/python-forecast.io

According to openweathermap.org:
  api.openweathermap.org/data/2.5/weather?lat=35&lon=139
"""

import datetime
import geocoder
import json
import requests
import sys
import time

api_key_path = "./api_key"
base_url = "http://api.openweathermap.org/data/2.5"
current_url = "%s/weather?" % base_url
forecast_url = "%s/forecast?" % base_url

# TODO(self) - find the darn flags library that we put in opensource and USE IT
# TODO(self) - implement the ability to look up by zip code or just supply
#              your own lat/long.

def GetAPIKey(api_key_path):
  """ Get the API key out of the file that contains nothing but the key.

  Requires:
    api_key_path: the path to the API key file
  Returns:
    api_key: the api key for openweathermap
  """

  with open(api_key_path, "r") as f:
    for line in f.readlines():
      api_key = line.rstrip("\n")
  return api_key

def GetLatLongQuery(location, units, api_key):
  """ Use Geocoder to convert a city/country or city/state to lat-long

  Requires:
    location: the location you're looking up
    units: the type of temperature you'd like to return back
    api_key: the api key for openweathermap

  Returns:
    query: the query to plug in to the openweathermap web interface
  """

  a = geocoder.google(location)
  query = { 'lat': a.lat,
            'lon': a.lng,
            'units': units,
            'APPID': api_key
          }
  return query

def GetWeatherData(url, query):
  """ Get the base weather data from openweathermap

  This sometimes barfs on me unexpectedly, and I can't figure out why. A
  while loop doesn't fix it - it only works if I exit the script and restart.
  I'm guessing it's a bug on their end.

  Requires:
    url: the URL of openweathermap to query (current, forecast, etc)
    query: what to query them for (location, units, api key)

  Returns:
    parsed_q: the un-json-ified data provided by openweathermap
  """

  q = requests.get(url, params=query)
  if not q.ok:
    print "Oh no! Couldn't get the weather; please try again in a few seconds."
    exit(1)
  parsed_q = json.loads(q.text)
  return parsed_q

def CurrentTemp(current):
  """ Print the current temps and humidity.

  TODO(self) - expand this out to include UV index!

  Requires:
    current: the data passed from openweathermap, stripped of jsonage
  """

  print "The current temperature is: %s degrees" % (str(current['main']['temp']))
  print "The current humidity is: %s%%" % (str(current['main']['humidity']))
  print "The current weather is: %s" % (current['weather'][0]['main'])

def ForecastBrief(forecast):
  """ Print a brief forecast of the next 5 days: highs, lows & sky conditions

  Requires:
    forecast: the forecast data returned by openweathermap
  """

  print "The brief forecast for the next five days:"
  print "Today (remaining): "
  hourly_forecast = []
  low = high = forecast['list'][0]['main']['temp']

  for elt in forecast['list']:
    dt = datetime.datetime.fromtimestamp(elt['dt'])
    temp = elt['main']['temp']
    weather_forecast = elt['weather'][0]['main']

    if dt.hour == 02:
      print "%s:" % dt.strftime('%Y-%m-%d (%A)')
      low = high = elt['main']['temp']
      hourly_forecast = [weather_forecast]
    else:
      hourly_forecast.append(weather_forecast)
      if low > temp:
        low = temp
      if high < temp:
        high = temp
    if dt.hour == 23:
      print "  Forecasted High: %s degrees" % str(high)
      print "  Forecasted Low: %s degrees" % str(low)
      # TODO(self) - figure out how to have this comma separated, on one line
      print "  Weather forecast includes: ",
      for w in set(hourly_forecast):
        print w,
      print

def ForecastFull(forecast):
  """ Print a full forecast of the next 5 days: highs, lows & sky conditions

  Requires:
    forecast: the forecast data returned by openweathermap
  """

  for elt in forecast['list']:
    dt = datetime.datetime.fromtimestamp(elt['dt'])

    if dt.hour == 02:
      print "%s:" % dt.strftime('%Y-%m-%d (%A)')

    temp = str(elt['main']['temp']) + 'F'
    humidity = str(elt['main']['humidity']) + '%'
    #hourly_forecast = elt['weather'][0]['main']
    forecast_desc = elt['weather'][0]['description']

    print "  %s: Temperature: %s degrees, Humidity: %s, Forecast: %s" % (dt.strftime('%H:%M:%S'), temp, humidity, forecast_desc)
    if dt.hour == 23:
      print

def main():

  # Check to make sure we got our arguments...
  if not sys.argv[1] or not sys.argv[2] or not sys.argv[3]:
    print "Usage: weatherbot.py 'Location, ST' 'C|F' 'current|brief|full'"
    exit(0)

  # TODO(self) - sanity checking on this argument.
  location = sys.argv[1]

  # Which side of the pond are we on? Celcius, or Farenheit
  units = sys.argv[2]
  if units == "F":
    units = 'imperial'
  elif units == "C":
    units = 'metric'
  else:
    units = 'imperial'

  # Pull the API key from the file; put it in a file so I can just check in
  # my code without having to remember to pull the api_key every time.
  api_key = GetAPIKey(api_key_path)
  query = GetLatLongQuery(location, units, api_key)

  # And now...the weather!
  print "The Weather for %s" % (location)

  if sys.argv[3] == "current":
    current = GetWeatherData(current_url, query)
    CurrentTemp(current)
  elif sys.argv[3] == "brief":
    forecast = GetWeatherData(forecast_url, query)
    ForecastBrief(forecast)
  elif sys.argv[3] == "full":
    forecast = GetWeatherData(forecast_url, query)
    ForecastFull(forecast)
  print

if __name__ == "__main__":
  main()
