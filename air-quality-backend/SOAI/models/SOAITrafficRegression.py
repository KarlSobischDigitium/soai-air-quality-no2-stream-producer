import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from SOAI.models.SOAITrafficModel import SOAITrafficModel

import logging
logger = logging.getLogger()


## Class which represents the regression model for traffic data
class SOAITrafficRegression(SOAITrafficModel):

    ## Initilizes a calibration model which is saved on disk
    def __init__(self):

        super().__init__()

    ## Function to train a regression model
    #
    # @param features Features for the calibration
    # @param target Target of the calibration (NO2 for example)
    # @param split Fraction which is taken as the test set
    # @returns  Parameters of the training process.
    def fTrain(self, dataSensor, dataTraffic, split=0.1, epochs=50, learningRate=0.005):
        for col in self.features + [self.target]:
            if col not in dataSensor.columns + dataTraffic.columns:
                raise Exception(f"Column {col} could not be found in training data.")

        features, target = self.fPreprocess(dataSensor, dataTraffic)

        self.scaler = StandardScaler()
        featuresScaled = self.scaler.fit_transform(features)

        self.model = self.fCreateModel(len(features), learningRate=learningRate, epochs=epochs)

        if len(featuresScaled) > 10:
            # Split in train and test set
            trainFeatures, testFeatures, trainTarget, testTarget = train_test_split(featuresScaled, target, test_size=split)
        else:
            success = False
            return success

        self.model.fit(trainFeatures, trainTarget, epochs=epochs, batch_size=10, validation_split=0.1)
        self.model.evaluate(testFeatures, testTarget)

    ## Creates and returns the model which is used for the calibration.
    def fCreateModel(self, nFeatures, learningRate=0.005, epochs=50):

        # Define NN via keras functional API
        input1 = tf.keras.Input(nFeatures)
        dense1 = tf.keras.layers.Dense(20, activation="relu")(input1)
        dense2 = tf.keras.layers.Dense(10, activation="relu")(dense1)
        dense3 = tf.keras.layers.Dense(5, activation="relu")(dense2)
        output1 = tf.keras.layers.Dense(1, activation="linear")(dense3)

        model = tf.keras.Model(inputs=[input1], outputs=[output1])
        model.compile(loss="mse", optimizer=tf.keras.optimizers.Adam(learningRate, decay=learningRate / epochs))

        return model
