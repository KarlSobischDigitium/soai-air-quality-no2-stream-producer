import tensorflow as tf
import pickle
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow import keras

import logging
logger = logging.getLogger()


## Class which represents a calibration model for the OpenAirSensors
class SOAIOpenAirCalibrationModel():

    ## Initilizes a calibration model which is saved on disk
    def __init__(self):
        self.model = None
        self.scaler = None

    def fLoad(self, pathToModel, pathToScaler):
        logger.debug(f"Load model from path {pathToModel}")
        self.model = tf.keras.models.load_model(pathToModel)
        self.scaler = pickle.load(open(Path(pathToScaler), 'rb'))  # Path is needed to deal with Windows and Linux

    ## Predicts the value given some features
    #
    # @param data Numpy array with shape (None, 3). These are the features and need to be given in the correct order.
    # @param normalize Boolean whether the data needs to be normalized or not (e.g. for fTrain no normalization is needed since it is done beforhand)
    # @returns value Predicted value based on the calibration model
    def fPredict(self, data, normalize=True):
        if self.scaler is None or self.model is None:
            raise Exception("Load the model etc. first.")

        value = None
        if normalize:
            dataNormalized = self.fNormalize(data)
            value = self.model.predict(dataNormalized)
        else:
            value = self.model.predict(data)

        return value

    ## Since the calibration model was trained with MinMax-normalization it also has to be applied for the prediction
    #
    # @param data Numpy array with shape (None, None)
    # @returns Normalized data
    def fNormalize(self, data):
        dataNormalized = self.scaler.transform(data)
        return dataNormalized

    ## Function to train a calibration model
    #
    # @param features Features for the calibration
    # @param target Target of the calibration (NO2 for example)
    # @param split Fraction which is taken as the test set
    # @returns  Parameters of the training process.
    def fTrain(self, features, target, split=0.1, epochs=50, learningRate=0.005):
        self.scaler = MinMaxScaler()
        featuresScaled = self.scaler.fit_transform(features)

        self.model = self.fCreateModel(features.shape[1], learningRate=learningRate, epochs=epochs)

        if len(featuresScaled) > 10:
            # Split in train and test set
            trainFeatures, testFeatures, trainTarget, testTarget = train_test_split(featuresScaled, target, test_size=split)
        else:
            success = False
            return success, None, None, None, None

        historyCallback = self.model.fit(trainFeatures, trainTarget, epochs=epochs, batch_size=10, validation_split=0.1)
        evaluateTest = self.model.evaluate(testFeatures, testTarget)

        predictionTest = self.fPredict(testFeatures, normalize=False)

        success = True
        return success, historyCallback, evaluateTest, predictionTest, testTarget

    ## Creates and returns the model which is used for the calibration.
    def fCreateModel(self, nFeatures, learningRate=0.005, epochs=50):

        # Define NN via keras functional API
        input1 = keras.layers.Input(nFeatures)
        dense1 = keras.layers.Dense(10, activation="relu")(input1)
        output1 = keras.layers.Dense(1)(dense1)

        model = keras.Model(inputs=[input1], outputs=[output1])
        model.compile(loss="mse", optimizer=tf.keras.optimizers.Adam(learningRate, decay=learningRate / epochs))

        return model
