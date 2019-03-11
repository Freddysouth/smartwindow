from keras.applications import ResNet50
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
import keras.models
from PIL import Image
import numpy as np
import flask
import io
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
import requests
import json

from LSTMForecast import LSTMForecast

app = flask.Flask(__name__)
model = None

DATAFORMAT = ['date', 'PM2.5', 'humidity', 'wnd_spd10', 'temp_avg', 'precipitation_avg']

def toFarenheit(c):
	return 9/5 * c + 32;

def makeListOfWeatherParams(keys, weather):
	d = []
	for day in weather:
		dayList = []
		for key in keys:
			value = 0
			if key == 'highTemperature':
				avgTemp = (float(day['highTemperature']) + float(day['lowTemperature']))/2
				value = toFarenheit(avgTemp)
			else:
				if day[key] != '*':
					value = day[key]
				else:
					value = 0
			dayList.append(float(value))
		d.append(dayList)
	return d

def getWeather():
	response = requests.get("https://weather.cit.api.here.com/weather/1.0/report.json?product=forecast_7days_simple&zipcode=93117&oneobservation=true&app_id=Is7EbpLYqp7H4EUwNyMz&app_code=sdwekigD9nSSWlQBa0pZ3g")
	data = response.json()
	weather = data["dailyForecasts"]["forecastLocation"]["forecast"]
	listOfWeatherParams = makeListOfWeatherParams(["humidity", "windSpeed", "highTemperature", "rainFall"], weather)
	return listOfWeatherParams

@app.route("/predict", methods=["POST"])
def predict():
	pass


def prepareData():
	dataset = read_csv('trainingdata.csv', header=0, index_col=0, usecols=DATAFORMAT)
	cols = dataset.columns.tolist()
	cols = [cols[-1]] + cols[:-1]
	dataset = dataset[cols]
	return dataset
	

if __name__ == "__main__":
	print(("* Loading Keras model and Flask starting server..."
	  "please wait until server has fully started"))
	#dataset = read_csv('pollution.csv', header=0, index_col=0)
	#print(dataset)
	#values = dataset.values[50 : 52]
	
	forcastedWeather = getWeather()
	print(forcastedWeather)
	dataset = prepareData()
	print(dataset)
	predictData = dataset.values[10:20]
	
	predictorP25 = LSTMForecast(dataset.values, 4)
	predictorP25.init('models/model.h5', [0,6,7,8,9], False)

	#values = predictorP25.predict(predictData[:, 1:])
	predictedPollution = predictorP25.predict(forcastedWeather)

	print("###### RESULT ######")
	print(predictedPollution)

	app.run()
