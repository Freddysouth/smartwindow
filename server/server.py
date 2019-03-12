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

predictorPM2_5 = None

DATAFORMATPM2_5 = ['date', 'PM2.5', 'humidity', 'wnd_spd10', 'temp_avg', 'precipitation_avg']
DATAFORMATPM10 = ['date', 'PM10', 'humidity', 'wnd_spd10', 'temp_avg', 'precipitation_avg']

PM2_5_LOW_POLLUTION_TRESHHOLD = 12
PM2_5_MEDIUM_POLLUTION_TRESHHOLD = 35.4

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

def prepareResponse(predictedPollution):
	response = {}
	response["pollutionValue"] = predictedPollution
	predictionDescription = []

	for i in predictedPollution:
		if (i <= PM2_5_LOW_POLLUTION_TRESHHOLD):
			predictionDescription.append("low")
		elif (i <= PM2_5_MEDIUM_POLLUTION_TRESHHOLD):
			predictionDescription.append("medium")
		else:
			predictionDescription.append("high")
	response["pollutionDescription"] = predictionDescription
	return response

def getWeather():
	response = requests.get("https://weather.cit.api.here.com/weather/1.0/report.json?product=forecast_7days_simple&zipcode=93117&oneobservation=true&app_id=Is7EbpLYqp7H4EUwNyMz&app_code=sdwekigD9nSSWlQBa0pZ3g")
	data = response.json()
	weather = data["dailyForecasts"]["forecastLocation"]["forecast"]
	listOfWeatherParams = makeListOfWeatherParams(["humidity", "windSpeed", "highTemperature", "rainFall"], weather)
	return listOfWeatherParams

@app.route("/predict", methods=["GET"])
def predict():
	forecastedWeather = getWeather()
	results = predictorPM2_5.predict(forecastedWeather)
	response = prepareResponse(results.tolist())
	return flask.jsonify(response)

def prepareData(filePath, dataFormat):
	dataset = read_csv(filePath, header=0, index_col=0, usecols=dataFormat)
	cols = dataset.columns.tolist()
	cols = [cols[-1]] + cols[:-1]
	dataset = dataset[cols]
	return dataset
	
def main():
	global predictorPM2_5

	print(("* Loading Keras model and Flask starting server..."
	  "please wait until server has fully started"))
	
	datasetPM2_5 = prepareData('trainingdata.csv' ,DATAFORMATPM2_5)
	
	predictorPM2_5 = LSTMForecast(datasetPM2_5.values, 4)
	predictorPM2_5.init('models/model_PM2_5.h5', [0,6,7,8,9], False)

	app.run()

if __name__ == "__main__":
	main()


