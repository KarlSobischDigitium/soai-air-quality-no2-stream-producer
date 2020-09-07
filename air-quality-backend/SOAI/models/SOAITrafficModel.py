import tensorflow as tf
import pickle
from pathlib import Path
import pandas as pd

import logging
logger = logging.getLogger()


## Class which represents all models which are base on traffic data
class SOAITrafficModel():

    features = ["no2", "rgreen", "rorange", "rred", "rbrown", "hum", "temp", "wg"]
    target = "no2_shifted"

    ## Initilizes the traffic models for the sensors
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

    ## Preprocess the input data.
    #
    # Concat the traffic and sensor data + interpolate features
    # @param dataSensor Sensor data with specific column names
    # @param dataTraffic Traffic data
    def fPreprocess(self, dataSensor, dataTraffic):
        dataSensor = dataSensor.resample("1h").mean()
        dataTraffic = dataTraffic.resample("1h").mean()

        timeMin = max(dataSensor.index.min(), dataTraffic.index.min())
        timeMax = min(dataSensor.index.max(), dataTraffic.index.max())

        dataSensor = dataSensor.loc[(dataSensor.index >= timeMin) & (dataSensor.index <= timeMax)]
        dataTraffic = dataTraffic.loc[(dataTraffic.index >= timeMin) & (dataTraffic.index <= timeMax)]

        dataSensor["no2_ip"] = dataSensor.interpolate()["no2"]
        dataSensor["wg_ip"] = dataSensor.interpolate()["wg"]
        dataSensor["hum_ip"] = dataSensor.interpolate()["hum"]
        dataSensor["temp_ip"] = dataSensor.interpolate()["temp"]

        dataTrain = pd.concat([dataSensor, dataTraffic])

        features = dataTrain[self.features].values
        target = dataTrain[self.target]

        return features, target
