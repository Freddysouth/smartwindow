import flask
import requests
import json

import numpy as np

from pandas import read_csv
from pandas import DataFrame
from pandas import concat

import keras.models

from LSTMForecaster import LSTMForecaster

app = flask.Flask(__name__)

predictorPM2_5 = None
predictorPM10 = None

DATAFORMATPM2_5 = ['date', 'PM2.5', 'humidity', 'wnd_spd10', 'temp_avg', 'precipitation_avg']
DATAFORMATPM10 = ['date', 'PM10', 'humidity', 'wnd_spd10', 'temp_avg', 'precipitation_avg']
UNPREDICTED_COLS = [0,6,7,8,9]

PM2_5_LOW_POLLUTION_TRESHHOLD = 12
PM2_5_MEDIUM_POLLUTION_TRESHHOLD = 35.4

PM10_LOW_POLLUTION_TRESHHOLD = 50
PM10_MEDIUM_POLLUTION_TRESHHOLD = 100

def toFarenheit(c):
	return 9/5 * c + 32;

#makes a 7day, 2d list of weather parameters: keys
def makeListOfWeatherParams(keys, weatherForecast):
	weekParams = []
	for day in weatherForecast:
		dayParams = []
		for key in keys:
			value = 0
			if key == 'highTemperature':
				avgTemp = (float(day['highTemperature']) + float(day['lowTemperature']))/2
				value = toFarenheit(avgTemp)
			else:
				value = day[key] if day[key] != '*' else 0
			dayParams.append(float(value))
		weekParams.append(dayParams)
	return weekParams


def prepareResponse(predictedPollution, pollutionType):
	lowTreshold = PM2_5_LOW_POLLUTION_TRESHHOLD if pollutionType == "PM2_5" else PM10_LOW_POLLUTION_TRESHHOLD
	mediumTreshold = PM2_5_MEDIUM_POLLUTION_TRESHHOLD if pollutionType == "PM2_5" else PM10_MEDIUM_POLLUTION_TRESHHOLD
	
	response = {"predictedPollution": predictedPollution}
	descriptions = []
	for value in predictedPollution:
		if (value <= lowTreshold):
			descriptions.append("low")
		elif (value <= mediumTreshold):
			descriptions.append("medium")
		else:
			descriptions.append("high")
	response["descriptions"] = descriptions
	return response

def getWeather():
	response = requests.get("https://weather.cit.api.here.com/weather/1.0/report.json?product=forecast_7days_simple&zipcode=93117&oneobservation=true&app_id=Is7EbpLYqp7H4EUwNyMz&app_code=sdwekigD9nSSWlQBa0pZ3g")
	data = response.json()

	weatherForecast = data["dailyForecasts"]["forecastLocation"]["forecast"]
	weatherParams = makeListOfWeatherParams(["humidity", "windSpeed", "highTemperature", "rainFall"], weatherForecast)
	return weatherParams

def prepareData(filePath, dataFormat):
	dataset = read_csv(filePath, header=0, index_col=0, usecols=dataFormat)
	cols = dataset.columns.tolist()
	cols = [cols[-1]] + cols[:-1]
	dataset = dataset[cols]
	return dataset

# endpoints
@app.route("/predict/<pollutionType>", methods=["GET"])
def predict(pollutionType):
	predictor = predictorPM2_5 if pollutionType == "PM2_5" else predictorPM10
	
	forecastedWeather = getWeather()
	predictedPollution = predictor.predict(forecastedWeather)
	response = prepareResponse(predictedPollution.tolist(), pollutionType)
	return flask.jsonify(response)
	
@app.route("/", methods=["GET"])
def home():
	return flask.render_template('index.html')

def main():
	global predictorPM2_5, predictorPM10

	print(("* Loading Keras model and Flask starting server..."
	  "please wait until server has fully started"))
	
	datasetPM2_5 = prepareData('trainingData/training_PM2_5.csv', DATAFORMATPM2_5)
	datasetPM10 = prepareData('trainingData/training_PM10.csv', DATAFORMATPM10)

	predictorPM2_5 = LSTMForecaster(datasetPM2_5.values)
	predictorPM2_5.init('models/model_PM2_5.h5', UNPREDICTED_COLS, False)
	#predictorPM2_5.csvResults()

	predictorPM10 = LSTMForecaster(datasetPM10.values)
	predictorPM10.init('models/model_PM10.h5', UNPREDICTED_COLS, False)

	app.run()

if __name__ == "__main__":
	main()


