import numpy as np
import logging
import geopy.distance
import os
import pickle
from pathlib import Path

from SOAI.handler.SOAIDiskHandler import SOAIDiskHandler
from SOAI.tools.SOAICalibrator import SOAICalibrator

logger = logging.getLogger()


# load data and use calibration class for each sensor
def main():
    # Create folder structure
    if os.path.exists(Path(os.environ.get("SOAI_MODEL_PATH") + "/temp")) is False:
        os.mkdir(Path(os.environ.get("SOAI_MODEL_PATH") + "/temp"))
        os.mkdir(Path(os.environ.get("SOAI_MODEL_PATH") + "/temp/plots"))
        logger.info(f"Create temporary folder to save models into.")

    if os.path.exists(Path(os.environ.get("SOAI_MODEL_PATH") + "/temp/plots/")) is False:
        os.mkdir(Path(os.environ.get("SOAI_MODEL_PATH") + "/temp/plots"))
        logger.info(f"Create folder to save plots into.")

    # Clear log
    if os.path.exists(Path(os.environ.get("SOAI_MODEL_PATH") + "/temp/result.txt")):
        os.remove(Path(os.environ.get("SOAI_MODEL_PATH") + "/temp/result.txt"))

    # Get data
    dataHandler = SOAIDiskHandler()
    dfOpenAir = dataHandler.fGetOpenAir(os.environ.get("SOAI") + "/data/openair/", selectValidData=True)
    dfOpenAirLocation = dataHandler.fGetOpenAirSensors()
    dfLanuv = dataHandler.fGetLanuv(os.environ.get("SOAI") + "/data/lanuv/", selectValidData=True)
    dfLanuvLocation = dataHandler.fGetLanuvSensors()

    # Remove unecessary information and set time as an index
    dfOpenAir = dfOpenAir.drop(["pm10", "pm25", "rssi"], axis=1)
    dfLanuv = dfLanuv.drop(["NO", "OZON"], axis=1)

    # Get a list of tuples (lat, lon) for each sensor
    openAirLocations = list(zip(dfOpenAirLocation["lat"], dfOpenAirLocation["lon"]))
    lanuvLocations = list(zip(dfLanuvLocation["lat"], dfLanuvLocation["lon"]))

    # Find the closest lanuv station to EACH openair sensor using a distance matrix and then calibrate
    # Loop through all openair locations
    for counter, openSensor in enumerate(openAirLocations):

        # Find closest lanuv sensor to openair sensor
        distanceList = np.zeros((len(lanuvLocations)))
        for countLanuv, lanuvSensor in enumerate(lanuvLocations, 0):  # For each sensor from Lanuv
            distanceList[countLanuv] = geopy.distance.geodesic(openSensor, lanuvSensor).m  # Calcualate the distance
        lanuvSensor = np.where(distanceList == distanceList.min())

        # Select only data of the closest pair
        OpenAirSensorID = dfOpenAirLocation.iloc[counter]["sensorID"]
        LanuvSensorID = dfLanuvLocation.iloc[lanuvSensor[0][0]]["sensorID"]
        singleDfOpenAir = dfOpenAir[dfOpenAir["sensorID"] == OpenAirSensorID]
        singleDfLanuv = dfLanuv[dfLanuv["sensorID"] == LanuvSensorID]

        # Downsample the data
        singleDfOpenAir = singleDfOpenAir.resample("1h").mean()
        singleDfLanuv = singleDfLanuv.resample("1h").mean()

        # Make sure that both data sets start and finish at the same time values (are of the same length)
        timeMin = max(singleDfOpenAir.index.min(), singleDfLanuv.index.min())
        timeMax = min(singleDfOpenAir.index.max(), singleDfLanuv.index.max())

        singleDfLanuv = singleDfLanuv.loc[(singleDfLanuv.index >= timeMin) & (singleDfLanuv.index <= timeMax)]
        singleDfOpenAir = singleDfOpenAir.loc[(singleDfOpenAir.index >= timeMin) & (singleDfOpenAir.index <= timeMax)]

        singleDfLanuv = singleDfLanuv.between_time("22:00:00", "06:00:00")  # TEMP: Test if calibration is improved
        singleDfOpenAir = singleDfOpenAir.between_time("22:00:00", "06:00:00")  # TEMP: Test if calibration is improved

        # Create model, if openair & lanuv values are not empty
        if singleDfOpenAir.empty is False and singleDfLanuv.empty is False:
            calibration = SOAICalibrator(singleDfOpenAir, singleDfLanuv, OpenAirSensorID)
            calibration.calibrate(epochs=100, learningRate=0.005)
            calibration.plotPreprocessedInput(Path(os.environ.get("SOAI_MODEL_PATH") + "/temp/plots"), distanceList.min(), LanuvSensorID)
            calibration.plotModel(Path(os.environ.get("SOAI_MODEL_PATH") + "/temp/plots"))

            # Save results
            calibration.calibModel.model.save(os.environ.get("SOAI_MODEL_PATH") + f"/temp/{OpenAirSensorID}.h5")
            pickle.dump(calibration.calibModel.scaler, open(Path(os.environ.get("SOAI_MODEL_PATH") + f"/temp/{OpenAirSensorID}_scaler.sav"), 'wb'))
            with open(Path(os.environ.get("SOAI_MODEL_PATH") + "/temp/result.txt"), "a") as f:
                f.write(f"model saved - MSE: {calibration.evaluatedModel}; {OpenAirSensorID}, {LanuvSensorID}\n{singleDfOpenAir.describe()}\n\n\n\n")
            calibration.calibrate(epochs=200, learningRate=0.005)
            if calibration.sucess:
                calibration.plotPreprocessedInput(Path(os.environ.get("SOAI") + "/savedModels/calibrations/temp/plots"), distanceList.min(), LanuvSensorID)
                calibration.plotModel(Path(os.environ.get("SOAI") + "/savedModels/calibrations/temp/plots"))

                # Save results
                calibration.calibModel.model.save(os.environ.get("SOAI") + f"/savedModels/calibrations/temp/{OpenAirSensorID}.h5")
                pickle.dump(calibration.calibModel.scaler, open(Path(os.environ.get("SOAI") + f"/savedModels/calibrations/temp/{OpenAirSensorID}_scaler.sav"), 'wb'))
                with open(Path(os.environ.get("SOAI") + "/savedModels/calibrations/temp/result.txt"), "a") as f:
                    f.write(f"model saved - MSE: {calibration.evaluatedModel}; {OpenAirSensorID}, {LanuvSensorID}\n{singleDfOpenAir.describe()}\n\n\n\n")
            else:
                with open(Path(os.environ.get("SOAI") + "/savedModels/calibrations/temp/result.txt"), "a") as f:
                    f.write(f"no model created - empty DataFrame: {OpenAirSensorID}\n\n\n\n")

        # Save error, if dataframe of sensor es empty
        else:
            with open(Path(os.environ.get("SOAI_MODEL_PATH") + "/temp/result.txt"), "a") as f:
                f.write(f"no model created - empty DataFrame: {OpenAirSensorID}\n\n\n\n")


if __name__ == '__main__':
    main()
