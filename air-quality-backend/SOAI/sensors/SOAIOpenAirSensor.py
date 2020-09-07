from SOAI.sensors.SOAISensor import SOAISensor
from SOAI.models.SOAIOpenAirCalibrationModel import SOAIOpenAirCalibrationModel

import os
import logging
import numpy as np

logger = logging.getLogger()


## Class which represents an OpenAirSensor
#
# This class differs from a normal sensor by using a calibration model to convert measurments to NO2.
class SOAIOpenAirSensor(SOAISensor):

    ## Initializes one OpenAir Cologne sensor
    #
    # @param ID ID (sensorID) of the sensor
    # @param location Location of the sensor given as tuple (latitude, longitude)
    def __init__(self, ID, location):
        logger.debug(f"Set up OpenAir Cologne Sensor with ID {ID} at location {location}")

        super().__init__("OpenAirCologne", ID, location)

        self.calibModel = None

    ## Loads the calibration model
    #
    # @param pathToModel Path to model to use for calibration
    # @param pathToScaler Path to scaler which is used to scale the data before prediction
    def fLoadCalibration(self, pathToModel, pathToScaler):
        logger.debug(f"Set up calibration model for OpenAir Cologne sensior with ID {self.ID} at location {self.location}")
        if os.path.isfile(pathToModel):
            self.calibModel = SOAIOpenAirCalibrationModel()
            self.calibModel.fLoad(pathToModel, pathToScaler)
        else:
            logger.warning(f"No calibration model found in path {pathToModel}. Set sensor as inactive.")
            self.fSetInactive()

    ## Sets a already loaded calibration model
    #
    # @param model Instance of the SOAIOpenAirCalibrationModel
    def fSetCalibration(self, model):
        if type(model).__name__ == "SOAIOpenAirCalibrationModel":
            self.calibModel = model
        else:
            raise Exception(f"Calibration model needs to be of type SOAIOpenAirCalibrationModel and not {type(model).__name__}")

    ## Returns the calibration model
    def fGetCalibration(self):
        return self.calibModel

    ## Returns a boolean whether a calibration model is set
    def fHasCalibration(self):
        if self.calibModel is not None:
            return True
        else:
            return False

    ## Converts one data sample to an NO2 value using the calibration model
    #
    # @param dataDict Dictionary with the features {r2: x, temp: y, hum: z} (in this case measurment corresponds to r2)
    def fDataToNO2(self, dataDict):
        if self.calibModel is None:
            logger.warning("No calibration model found. Is this sensor calibrated?")
            raise Exception("No calibration model found.")

        # Check if all features are available
        neededColumns = ["r2", "temp", "hum"]
        for col in neededColumns:
            if col not in dataDict.keys():
                logger.error(f"Features have no value for {col}.")
                raise Exception(f"Features have no value {col}.")

        data = np.array([dataDict["hum"], dataDict["temp"], dataDict["r2"]])
        data = data.reshape(1, -1)
        no2 = self.calibModel.fPredict(data)

        return no2
