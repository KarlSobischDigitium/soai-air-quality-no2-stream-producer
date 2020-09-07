from SOAI.models.SOAIOpenAirCalibrationModel import SOAIOpenAirCalibrationModel

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option("display.max_rows", 10000)


## Calibrate sensors
class SOAICalibrator:

    ## initiallize variables
    def __init__(self, sensorToCalibrate, sensorCounterpart, OpenAirSensorID):
        self.dfOpenAir = sensorToCalibrate
        self.dfLanuv = sensorCounterpart
        self.OpenAirSensorID = OpenAirSensorID

    ## preprocess data and create model
    def calibrate(self, epochs=100, learningRate=0.005):

        """Merge the OpenAir Cologn and Lanuv data in one data frame"""
        self.dfCombined = pd.DataFrame(index=self.dfOpenAir.index)
        self.dfCombined["hum"] = self.dfOpenAir["hum"]
        self.dfCombined["temp"] = self.dfOpenAir["temp"]
        self.dfCombined["r2"] = self.dfOpenAir["r2"]
        self.dfCombined["no2"] = self.dfLanuv["no2"]
        self.dfCombined = self.dfCombined.dropna()

        """Train calibration model (NN)"""
        # Select features and scale them
        fHum = self.dfCombined["hum"].values
        fTemp = self.dfCombined["temp"].values
        fR2 = self.dfCombined["r2"].values

        features = np.vstack([fHum, fTemp, fR2]).T
        target = self.dfCombined["no2"].values

        self.calibModel = SOAIOpenAirCalibrationModel()
        self.sucess, self.historyCallback, self.evaluatedModel, self.predictionTarget, self.testTarget = self.calibModel.fTrain(features, target, epochs=epochs, learningRate=learningRate)

    ## plot the preprocessed input
    def plotPreprocessedInput(self, savePath, geoDistance, LanuvSensorID):

        # Plot the data for a intermediate check
        plt.subplot(3, 2, 1)
        self.dfLanuv["no2"].plot(title="Lanuv")

        plt.subplot(3, 2, 3)
        self.dfOpenAir["r2"].plot(figsize=(20, 10), linewidth=1, fontsize=20, title="OpenAir")  #(lambda x: x/10-90)

        plt.subplot(3, 2, 5)
        dfLanuvNorm = (self.dfLanuv["no2"] - self.dfLanuv["no2"].mean()) / (self.dfLanuv["no2"].max() - self.dfLanuv["no2"].min())
        dfOpenAirNorm = (self.dfOpenAir["r2"] - self.dfOpenAir["r2"].mean()) / (self.dfOpenAir["r2"].max() - self.dfOpenAir["r2"].min())
        dfLanuvNorm.plot()
        dfOpenAirNorm.plot()

        plt.subplot(3, 2, 6)
        stringBuffer = self.dfCombined.describe()
        plotText = f"OpenAir: {self.OpenAirSensorID}\nLanuv:{LanuvSensorID}\nAccuracy:{self.evaluatedModel}\ngeoDistance: {geoDistance}\ninfo:\n{stringBuffer}"
        plt.text(0.05, 0.095, plotText, fontsize=20)

        plt.savefig(f"{savePath}/1_plot_{self.OpenAirSensorID}.png")

        # Plot data without time dimension
        plt.figure(figsize=(20, 10))

        plt.subplot(3, 1, 1)
        plt.title("Lanuv")
        plt.plot(self.dfCombined["no2"].values)

        plt.subplot(3, 1, 2)
        plt.title("OpenAir")
        plt.plot(self.dfCombined["r2"].values)  # apply(lambda x: x/10-90).values) # Again a very rough approximation to scale and shift by eye

        plt.subplot(3, 1, 3)
        dfLanuvNormCombined = (self.dfCombined["no2"].values - self.dfCombined["no2"].values.mean()) / (self.dfCombined["no2"].values.max() - self.dfCombined["no2"].values.min())
        dfOpenAirNormCombined = (self.dfCombined["r2"].values - self.dfCombined["r2"].values.mean()) / (self.dfCombined["r2"].values.max() - self.dfCombined["r2"].values.min())
        plt.plot(dfLanuvNormCombined)
        plt.plot(dfOpenAirNormCombined)

        plt.savefig(f"{savePath}/2_dataWithoutDimensions_{self.OpenAirSensorID}.png")

        plt.figure(figsize=(20, 10))
        plt.scatter(self.dfCombined["r2"].values, self.dfCombined["no2"].values)
        plt.savefig(f"{savePath}/3_scatterDataWithoutDimensions{self.OpenAirSensorID}.png")

    # plot the model
    def plotModel(self, savePath):

        plt.figure(figsize=(20, 10))
        plt.plot(self.historyCallback.history["loss"])
        plt.plot(self.historyCallback.history["val_loss"])
        plt.gca().legend(('loss', 'val_loss'))
        plt.savefig(f"{savePath}/4_resultTraining_{self.OpenAirSensorID}.png")

        plt.figure(figsize=(20, 10))
        plt.plot(self.testTarget)
        plt.plot(self.predictionTarget)
        plt.gca().legend(('testTarget', 'predictionTarget'))
        plt.savefig(f"{savePath}/5_prediction_{self.OpenAirSensorID}.png")


def main():
    print("This is a class!")


if __name__ == '__main__':
    main()
