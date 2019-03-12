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

def load_model():
    # load the pre-trained Keras model (here we are using a model
    # pre-trained on ImageNet and provided by Keras, but you can
    # substitute in your own networks just as easily)
    global model
    model = keras.models.load_model('models/model_PM2_5.h5')
    model._make_predict_function()

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
	response = {}

	forecastedWeather = getWeather()
	testInput = [
		[0.531629, 0.724701, 0.194444, 0.000000],
		[0.531629, 0.724701, 0.194444, 0.000000]
	]
	testInput = np.array(testInput)
	testInput = testInput.reshape((testInput.shape[0], 1, testInput.shape[1]))
	response["predictions"] = model.predict(testInput)

	return flask.jsonify(response)

def prepareData(dataFormat):
	dataset = read_csv('trainingdata.csv', header=0, index_col=0, usecols=dataFormat)
	cols = dataset.columns.tolist()
	cols = [cols[-1]] + cols[:-1]
	dataset = dataset[cols]
	return dataset
	
def main():
	global predictorPM2_5

	print(("* Loading Keras model and Flask starting server..."
	  "please wait until server has fully started"))
	
	#datasetPM2_5 = prepareData(DATAFORMATPM2_5)
	
	#predictorPM2_5 = LSTMForecast(datasetPM2_5.values, 4)
	#predictorPM2_5.init('models/model_PM2_5.h5', [0,6,7,8,9], True)

	#testInput = [[52.0,12.96,54.752,0.0],[45.0,22.22,58.495999999999995,0.0],[40.0,22.22,54.5,0.0],[40.0,12.96,53.492000000000004,0.0],[49.0,12.96,56.003,0.0],[49.0,12.96,57.002,0.0],[41.0,11.11,58.505,0.0]]
	#predictedPM2_5 = predictorPM2_5.predict(testInput)
	#response = prepareResponse(predictedPM2_5)
	#print(response)
	load_model()
	app.run()

if __name__ == "__main__":
	main()


