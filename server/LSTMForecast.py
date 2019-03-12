import pickle
from math import sqrt
import numpy as np
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
import keras.models
from keras.layers import Dense
from keras.layers import LSTM
import os

class LSTMForecast:

	def __init__(self, values, index):
		self.values = values
		self.train = []
		self.test = []
		self.trainInput = []
		self.trainOutput = []
		self.testInput = []
		self.testOutput = []
		self.model = None
		self.history = None

		#self.encoder = LabelEncoder()
		#self.encoder = self.encoder.fit(self.values[:, index])
		
		#self.values[:, index] = self.encoder.transform(self.values[:, index])
		
		self.scaler = MinMaxScaler(feature_range=(0, 1))
		self.scaler = self.scaler.fit(values)

		self.values = self.values.astype('float32')
		# normalize features
		self.values = self.scaler.transform(self.values)
		

	# convert series to supervised learning
	def series_to_supervised(self, n_in=1, n_out=1, dropnan=True):
		n_vars = 1 if type(self.values) is list else self.values.shape[1]
		df = DataFrame(self.values)
		cols, names = list(), list()
		# input sequence (t-n, ... t-1)
		#for i in range(n_in, 0, -1):
		shiftInput = 0
		cols.append(df.shift(shiftInput))
		names += [('var%d(t-%d)' % (j, shiftInput)) for j in range(n_vars)]
		# forecast sequence (t, t+1, ... t+n)
		for i in range(0, n_out):
			cols.append(df.shift(-i))
			if i == 0:
				names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
			else:
				names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
		# put it all together
		agg = concat(cols, axis=1)
		agg.columns = names
		# drop rows with NaN values
		if dropnan:
			agg.dropna(inplace=True)
		return agg

	def dropColumns(self, columnIndexes):
		reframed = self.series_to_supervised(1, 1)
		reframed.drop(reframed.columns[columnIndexes], axis=1, inplace=True)
		#print("########### REFRAMED: ")
		#print(reframed)
		self.values = reframed.values

	def splitTrainTestSets(self, trainRatio):
		self.train = self.values[:int(len(self.values) * trainRatio), :]
		self.test = self.values[int(len(self.values)* trainRatio):, :]

	# split into train and test sets
	#values = reframed.values
	#n_train_hours = 365 * 24
	#train = values[:n_train_hours, :]
	#test = values[n_train_hours:, :]
	#train, test = split(0.8, values)
	def splitInputOutput(self):
		self.trainInput, self.trainOutput = self.train[:, :-1], self.train[:, -1]
		self.testInput, self.testOutput = self.test[:, :-1], self.test[:, -1]
	# split into input and outputs
	#train_X, train_y = train[:, :-1], train[:, -1]
	#test_X, test_y = test[:, :-1], test[:, -1]

	def reshapeTrainTestInputSetsTo3d(self):
		self.trainInput = self.trainInput.reshape((self.trainInput.shape[0], 1, self.trainInput.shape[1]))
		self.testInput = self.testInput.reshape((self.testInput.shape[0], 1, self.testInput.shape[1]))

	# reshape input to be 3D [samples, timesteps, features]
	#train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
	#test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
	#print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)

	def saveModel(self, filePath):
		self.model.save(filePath)

	def initModel(self):
		self.model = keras.models.Sequential()
		self.model.add(LSTM(50, input_shape=(self.trainInput.shape[1], self.trainInput.shape[2])))
		self.model.add(Dense(1))
		self.model.compile(loss='mae', optimizer='adam')

	def fitModel(self, filePath):
		self.history = self.model.fit(self.trainInput, self.trainOutput, epochs=50, batch_size=72, validation_data=(self.testInput, self.testOutput), verbose=2, shuffle=False)
		self.saveModel(filePath)

	def reshapePredictionInputTo3d(self, predictionInput):
		return predictionInput.reshape((predictionInput.shape[0], 1, predictionInput.shape[1]))

	def getNormalizedPrediction(self, predictionInput):
		predictionInput = predictionInput.reshape((predictionInput.shape[0], 1, predictionInput.shape[1]))
		return self.model.predict(predictionInput)

	def getActualPrediction(self, predictionInput, prediction):
		#predictionInput = predictionInput.reshape((predictionInput.shape[0], predictionInput.shape[2]))
		actualizedPrediction = np.concatenate((prediction, predictionInput), axis=1)
		actualizedPrediction = self.scaler.inverse_transform(actualizedPrediction)
		return actualizedPrediction

	def trainModel(self, filePath, columnsToDrop):
		self.dropColumns(columnsToDrop)
		# split dataset into train and test sets
		self.splitTrainTestSets(0.9)
		# split train and test sets to representative inputs and outputs
		self.splitInputOutput()
		self.reshapeTrainTestInputSetsTo3d()
		# prepare, fit, and save model
		self.initModel()
		self.fitModel(filePath)

	def init(self, filePath, columnsToDrop, train):
		if train:
			self.trainModel(filePath, columnsToDrop)
		else:
			if os.path.exists(filePath):
				self.model = keras.models.load_model(filePath)
				self.model._make_predict_function()
			else:
				self.trainModel(filePath, columnsToDrop)

	#input format: [[weatherparameters...., previosPollution]]
	def predict(self, inputData):
		#inputData[:, 4] = self.encoder.transform(inputData[:, 4])
		prepend = np.zeros((len(inputData), 1))
		inputData = np.concatenate((prepend, inputData), axis=1)
		#print(inputData[0])
		
		scaled = self.scaler.transform(inputData)
		scaled = scaled[:, 1:]

		normalizedPrediction = self.getNormalizedPrediction(scaled)
		actualPrediction = self.getActualPrediction(scaled, normalizedPrediction)

		return actualPrediction[:, 0]


	#test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))

	#inv_yhat = concatenate((yhat, test_X[:, 1:]), axis=1)
	#inv_yhat = scaler.inverse_transform(inv_yhat)
	#inv_yhat = inv_yhat[:,0]

	#print(inv_yhat)

	#test_y = test_y.reshape((len(test_y), 1))
	#inv_y = concatenate((test_y, test_X[:, 1:]), axis=1)
	#inv_y = scaler.inverse_transform(inv_y)
	#inv_y = inv_y[:,0]

	#rmse = sqrt(mean_squared_error(inv_y, inv_yhat))
	#print('Test RMSE: %.3f' % rmse)

	#model.save('model.h5')


