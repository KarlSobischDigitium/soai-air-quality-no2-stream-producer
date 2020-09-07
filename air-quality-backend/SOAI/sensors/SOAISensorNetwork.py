from .SOAIOpenAirSensor import SOAIOpenAirSensor
from .SOAILanuvSensor import SOAILanuvSensor

import pandas as pd
import logging
import numpy as np
import os
import geopy.distance
logger = logging.getLogger()


## Class which represents a sensor network
#
# It takes care of loading all the sensor from som configuration file and manages the communication between them and to the outside.
class SOAISensorNetwork():

    # This list correspond to the type of sensors which are available in this network. Other types of sensors in the configuration file will be skipped.
    sensorTypes = ["OpenAirCologne", "Lanuv"]

    ## Initializes the network with sensors from the configuration file.
    #
    # The configuration file needs to be written in a very specific form. The columns are seperated by whitespaces and in the following order:
    #   Sensor type | ID | Laitude | Longitude | Active | Sensor calibration (optional)
    #
    # Valid values are:
    #   Sensor type: OpenAirCologne, Lanuv
    #   ID: String containing the ID
    #   Latitude: Value of latitude
    #   Longitude: Value of longitude
    #   Active: 1 for active or 0 for inactive
    #   Sensor calibration: Path to the calibration model for OpenAirCologn sensors
    #
    # @param pathToConfigFile Path and filename of the configuration file
    def __init__(self, pathToConfigFile):
        self.listSensors = []

        with open(pathToConfigFile) as f:
            for line in f:
                configs = line.rstrip('\n').split(" ")
                if len(configs) < 3:
                    logger.error(f"The following line can not be used to set up a sensor: {line}")
                    continue

                sensorType = configs[0]
                sensorID = configs[1]
                sensorLocation = (float(configs[2]), float(configs[3]))
                active = int(configs[4])

                if sensorType == "OpenAirCologne":
                    sensorTEMP = SOAIOpenAirSensor(sensorID, sensorLocation)

                    # By default the sensors are not active
                    if active == 1:
                        sensorTEMP.fSetActive()

                    # If a path is available from the config file set the calibration model
                    if len(configs) > 5:
                        pathModel = os.environ.get("SOAI") + "/" + configs[5] + "/" + sensorID + ".h5"
                        pathScaler = os.environ.get("SOAI") + "/" + configs[5] + "/" + sensorID + "_scaler.sav"
                        sensorTEMP.fLoadCalibration(pathModel, pathScaler)

                    self.listSensors.append(sensorTEMP)

                elif sensorType == "Lanuv":
                    sensorTEMP = SOAILanuvSensor(sensorID, sensorLocation)
                    if active == 1:
                        sensorTEMP.fSetActive()
                    self.listSensors.append(sensorTEMP)

                else:
                    logger.error(f"Sensor type is not known. Skip line {line}.")

    ## Set up the traffic models using a configuration file.
    #
    # The configuration file needs to be written in a very specific form. The columns are seperated by whitespaces and in the following order:
    #   Sensor type | ID | Traffic regression
    #
    # @param pathToConfigFile Path and filename of the configuration file for traffic models
    def fSetUpTrafficModels(self, pathToConfigFile):
        with open(pathToConfigFile) as f:
            for line in f:
                configs = line.rstrip('\n').split(" ")
                if len(configs) < 3:
                    logger.error(f"The following line can not be used to set up a sensor: {line}")
                    continue

                sensorType = configs[0]
                sensorID = configs[1]
                pathModel = os.environ.get("SOAI") + "/" + configs[2] + "/" + sensorID + ".h5"
                pathScaler = os.environ.get("SOAI") + "/" + configs[2] + "/" + sensorID + "_scaler.sav"

                self.fFindSensorFromID(sensorType, sensorID).fLoadTrafficModel(pathModel, pathScaler)

    ## Check if a given sensor type is available in the sensor network
    #
    # @param sensorType Name of the sensor type (e.g. OpenAirCologne, Lanuv)
    def fCheckSensorType(self, sensorType):
        if sensorType not in self.sensorTypes:
            return False
        else:
            return True

    ## Checks if the sensors are set up correctly
    #
    # Checks if a sensor is marked as active (see config file) and for the OpenAirCologne sensors if a calibration model is set
    def fCheckNetwork(self):

        for sensorType in self.sensorTypes:
            countActive = 0
            countSum = 0
            countWronglyActive = 0

            for sensor in self.listSensors:

                if sensor.fGetType() == sensorType:
                    countSum += 1

                    if sensor.fIsActive() is True:
                        countActive += 1

                        if sensorType == "OpenAirCologne" and sensor.fHasCalibration() is False:
                            countWronglyActive += 1
                            logger.error(f"OpenAirCologne sensor {sensor.fGetID()} is active but does not have a calibration model set. Set as inactive.")
                            sensor.fSetInactive()

            logger.info(f"Status of {sensorType} sensors:\n\t{countActive} of {countSum} are active.\n\t{countWronglyActive} of these have an error.")

    ## Returns the corresponding sensor
    #
    # @param ID of the sensor
    def fFindSensorFromID(self, ID):
        for sensor in self.listSensors:
            if sensor.fGetID() == ID:
                return sensor

        logger.warning(f"Sensor with ID {ID} not found in network.")
        return None

    ## Returns the N sensors which are closest to a specific location
    #
    # @param lat Latitude
    # @param lon Longitude
    # @param sensorTypes Types of the sensors which shall be considered
    # @param N Number of nearest sensors which shall be returned
    def fFindSensorFromLocation(self, lat, lon, sensorTypes=["OpenAirCologne", "Lanuv"], N=1):
        listSensorLocations = [sensor.fGetLocation() for sensor in self.listSensors if sensor.fGetType() in sensorTypes]
        distanceList = np.array([geopy.distance.vincenty(listSensorLocations[i], (lat, lon)).m for i in range(len(listSensorLocations))])

        idxSmallest = np.argpartition(distanceList, N)[:N]
        logger.debug(f"Return the {N} closest sensors to point ({lat}, {lon}) which have index {idxSmallest}.")

        return [self.listSensors[i] for i in idxSmallest], distanceList[idxSmallest]

    ## Returns the N sensor pairs which are closest to each other
    #
    # TODO This is a mess of lists and np.arrays.
    # @param sensorType1 Type of sensors 1
    # @param sensorType2 Type of sensors 2
    # @param N Number of sensor pairs to return
    def fGetSmallestSensorPairs(self, sensorType1="OpenAirCologne", sensorType2="Lanuv", N=1):
        if self.fCheckSensorType(sensorType1) is False:
            raise Exception(f"Sensor type {sensorType1} is not known.")
        if self.fCheckSensorType(sensorType2) is False:
            raise Exception(f"Sensor type {sensorType2} is not known.")

        listSensorsType1 = np.array([sensor for sensor in self.listSensors if sensor.fGetType() == sensorType1])
        listSensorsType2 = np.array([sensor for sensor in self.listSensors if sensor.fGetType() == sensorType2])

        locationsType1 = np.array([sensor.fGetLocation() for sensor in listSensorsType1])
        locationsType2 = np.array([sensor.fGetLocation() for sensor in listSensorsType2])

        # For each sensor of type 1 calculate the clostest sensor of type 2
        distancePairs = np.zeros((len(locationsType1)))
        closestSensorType2List = []
        for count1, location1 in enumerate(locationsType1, 0):

            distanceList = np.zeros((len(locationsType2)))

            for count2, location2 in enumerate(locationsType2, 0):
                distanceList[count2] = geopy.distance.vincenty(location1, location2).m

            idxSmallest = np.argmin(distanceList)
            closestSensorType2List.append(listSensorsType2[idxSmallest])
            distancePairs[count1] = distanceList[idxSmallest]
            logger.debug(f"For sensor of type {sensorType1} at location {location1} the distances to sensors of type {sensorType2} are {distanceList}.")

        idxSmallest = np.argpartition(np.array(distancePairs), N)[:N]

        return listSensorsType1[idxSmallest], np.array(closestSensorType2List)[idxSmallest], distancePairs[idxSmallest]

    ## Gets a data frame with measurments and converts the measurments to NO2 values
    #
    # @param data Pandas data frame with at least the columns OpenAirCologne: ID (sensorID) | r2 | temp | hum; Lanuv: no2
    # @returns dataNO2 Same data frame as data but with an additional column no2 for the NO2 values
    def fDataToNO2(self, data):
        if isinstance(data, pd.DataFrame) is False:
            logger.error("Data has to be give as a pandas data frame.")
            raise Exception("Data has to be give as a pandas data frame.")

        # A column with name "sensorID" has to exist
        if "sensorID" not in data.columns:
            logger.error("No column with sensorID's were found.")
            raise Exception("No column with sensorID's were found.")

        # Convert the data to NO2 measurments using the sensor network
        no2 = np.ones((len(data))) * (-1)  # Default values which are filled in the next for loop
        for ID in data["sensorID"].unique():
            dataTEMP = data[data["sensorID"] == ID]
            indexTEMP = data["sensorID"] == ID
            indexTEMP = [i for i, x in enumerate(indexTEMP.values) if x]

            sensor = self.fFindSensorFromID(ID)
            no2TEMP = np.ones((len(dataTEMP))) * (-1)

            if sensor is None:
                logger.info(f"Skip non-existing sensor with ID {ID}")
            else:
                if sensor.fIsActive() is False:
                    logger.info(f"Skip unactive sensor with ID {ID}")
                else:
                    # Iterate over data frame with rows as dicts and get prediction
                    countTEMP = 0
                    for k, row in dataTEMP.iterrows():
                        no2TEMP[countTEMP] = sensor.fDataToNO2(row)
                        countTEMP += 1

                no2[indexTEMP] = no2TEMP

        data["no2"] = no2

        return data

    ## Given a location with latitude and longitude a NO2 value is returned by interpolation between sensors
    #
    # @param lat Latitude
    # @param lon Longitude
    # @param data Pandas data frame with at least the columns OpenAirCologne: ID (sensorID) | r2 | temp | hum; Lanuv: no2. Attention! Every sensor needs to be unique since the data is interpreted at one timestamp.
    # @param sensorTypes Type of sensors to consider
    def fLocationToNO2(self, lat, lon, data, sensorTypes=["OpenAirCologne", "Lanuv"]):
        sensors = [sensor for sensor in self.listSensors if sensor.fGetType() in sensorTypes]

        sensorLocations = [sensor.fGetLocation() for sensor in sensors]
        distanceList = [geopy.distance.vincenty(sensorLocations[i], (lat, lon)).m for i in range(len(sensorLocations))]

        # Get the no2 data of all sensors
        dataNO2 = self.fDataToNO2(data)

        # Check for consistency and save no2 values in list corresponding to the sensors list created above
        no2Values = []
        for sensor in sensors:
            dataNO2_sensor = dataNO2[dataNO2["sensorID"] == sensor.fGetID()]
            if len(dataNO2_sensor) == 0:
                continue
            elif len(dataNO2_sensor) > 1:
                logger.error(f"Data frame exhibits non unique sensors. The data can not be interpreted as one timestamp.")
                raise Exception(f"Data frame exhibits non unique sensors. The data can not be interpreted as one timestamp.")
            else:
                no2Values.append(dataNO2_sensor["no2"])
        no2Values = np.array(no2Values)

        if min(distanceList) == 0:
            return no2Values[np.argmin(np.array(distanceList))]

        # Weight the mean value with the inverse distance
        meanNO2 = 0
        for no2, distance in zip(no2Values, distanceList):
            meanNO2 += 1 / distance * no2
        meanNO2 = meanNO2 / sum([1 / distance for distance in distanceList])

        return meanNO2
