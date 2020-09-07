from .SOAISensor import SOAISensor
from SOAI.models.SOAITrafficRegression import SOAITrafficRegression

import os
import logging
import numpy as np
logger = logging.getLogger()


## Class which represents a Lanuv sensor
#
# This is kind of a dummy class since a Lanuv sensor does not need to treat different then a normal sensor
class SOAILanuvSensor(SOAISensor):

    ## Initializes one Lanuv sensor
    #
    # @param ID ID (sensorID) of the sensor
    # @param location Location of the sensor given as tuple (latitude, longitude)
    def __init__(self, ID, location):
        logger.debug(f"Set up Lanuv sensor with ID {ID} at location {location}")
        super().__init__("Lanuv", ID, location)

        self.trafficModel = None

        self.active = True

    ## Since the data is already a calibrated NO2 value this is a dummy function
    #
    # @param dataDict Dictionary with the features {no2: x} (measurment corresponds to NO2 value)
    def fDataToNO2(self, dataDict):
        # Check if all features are available
        neededColumns = ["no2"]
        for col in neededColumns:
            if col not in dataDict.keys():
                logger.error(f"Features have no value for {col}.")
                raise Exception(f"Features have no value {col}.")

        return dataDict["no2"]

    ## Loads the traffic model
    #
    # @param pathToModel Path to model to use for calibration
    # @param pathToScaler Path to scaler which is used to scale the data before prediction
    def fLoadTrafficModel(self, pathToModel, pathToScaler):
        logger.debug(f"Set up calibration model for OpenAir Cologne sensior with ID {self.ID} at location {self.location}")
        if os.path.isfile(pathToModel):
            self.trafficModel = SOAITrafficRegression()
            self.trafficModel.fLoad(pathToModel, pathToScaler)
        else:
            logger.warning(f"No traffic model found in path {pathToModel}. Set sensor as inactive.")
            self.fSetInactive()

    ## Sets a already loaded traffic model
    #
    # @param model Instance of the SOAIOpenAirCalibrationModel
    def fSetTrafficModel(self, model):
        if type(model).__name__ == "SOAITrafficRegression":
            self.trafficModel = model
        else:
            raise Exception(f"Traffic model needs to be of type SOAITrafficModel and not {type(model).__name__}")

    ## Returns the traffic model
    def fGetTrafficModel(self):
        return self.trafficModel

    ## Returns a boolean whether a traffic model is set
    def fHasTrafficModel(self):
        if self.trafficModel is not None:
            return True
        else:
            return False

    ## Converts one data sample to an NO2 value using the calibration model.
    #
    # This function takes care of the correct sequence.
    # @param dataDict Dictionary with the features {rgreen: x1, rorange: x2, rred: x3, rbrown: x4, hum: x5, temp: x6, wg: x7}
    def fDataToTraffic(self, dataDict):
        if self.trafficModel is None:
            logger.warning("No traffic model found. Is a traffic model available?")
            raise Exception("No traffic model found.")

        data = np.array([dataDict["rgreen"], dataDict["rorange"], dataDict["rred"], dataDict["rred"], dataDict["hum"], dataDict["temp"], dataDict["wg"]])
        data = data.reshape(1, -1)
        no2 = self.trafficModel.fPredict(data)

        return no2
