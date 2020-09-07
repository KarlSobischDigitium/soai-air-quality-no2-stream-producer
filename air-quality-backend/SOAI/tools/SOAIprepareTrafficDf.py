import pandas as pd
from tqdm import tqdm
import os

class SOAIprepareTrafficDf:

  def __init__(self, choosenSensor, zippedTrafficFilesPath, pixelsAroundSensor):
    self.choosenSensor = choosenSensor
    self.zippedTrafficFilesPath = zippedTrafficFilesPath
    self.zippedTrafficFiles = [f for f in os.listdir(os.path.join(os.environ.get("SOAI"), zippedTrafficFilesPath)) if os.path.isfile(os.path.join(os.environ.get("SOAI"), zippedTrafficFilesPath, f))]
    self.pixelsAroundSensor = pixelsAroundSensor

  def prepare(self):

    sensorPixelLocation = ["807f16fc",2081,288],["807f6eb8",991,1779],["807f6cec",1822,2407],["807f6940",2151,1309],["807f6b16",2234,2740],["807f4474",1250,292],["807f6774",2134,602],["807f3b50",3875,3883],["807f8be6",2027,55],["807f75e8",2241,680],["807f8844",3126,192],["807f77b4",475,1035],["807f52e8",1878,1287],["807f584c",2325,2441],["807f8498",3345,351],["807f798a",3077,251],["807f65b2",1171,1165],["807f5112",108472,104071],["807f0fb8",2027,55],["807f7b56",1199,503],["807f4640",852,1246],["807f8664",1324,2293],["807f395c",1604,2130],["807f49e2",2169,1301],["807f5a18",1040,499],["807f80f6",1203,658],["807f118e",1573,1401],["807f5680",221,3247],["807f1c6a",1171,1353],["VKTU",2089,766],["RODE",2727,2889],["VKCL",3182,190]

    for sensor in sensorPixelLocation:
        if sensor[0] == self.choosenSensor:
            sensorX = sensor[2]
            sensorY = sensor[1]
            break

    dataTrafficRaw = pd.DataFrame()
    dataTrafficFilter = pd.DataFrame()

    for file in tqdm(self.zippedTrafficFiles):
        dataTrafficRaw = pd.read_csv(os.path.join(os.environ.get("SOAI"), self.zippedTrafficFilesPath, file), compression='gzip', sep=",")

        dataTrafficReduced = dataTrafficRaw[\
                                        ((dataTrafficRaw['green_X'] >= sensorX - self.pixelsAroundSensor) & (dataTrafficRaw['green_X'] <= sensorY + self.pixelsAroundSensor) &\
                                          (dataTrafficRaw['green_Y'] >= sensorY - self.pixelsAroundSensor) & (dataTrafficRaw['green_Y'] <= sensorY + self.pixelsAroundSensor)) | \
                                        ((dataTrafficRaw['orange_X'] >= sensorX - self.pixelsAroundSensor) & (dataTrafficRaw['orange_X'] <= sensorX + self.pixelsAroundSensor) &\
                                          (dataTrafficRaw['orange_Y'] >= sensorY - self.pixelsAroundSensor) & (dataTrafficRaw['orange_Y'] <= sensorY + self.pixelsAroundSensor)) | \
                                        ((dataTrafficRaw['red_X'] >= sensorX - self.pixelsAroundSensor) & (dataTrafficRaw['red_X'] <= sensorX + self.pixelsAroundSensor) &\
                                          (dataTrafficRaw['red_Y'] >= sensorY - self.pixelsAroundSensor) & (dataTrafficRaw['red_Y'] <= sensorY + self.pixelsAroundSensor)) | \
                                        ((dataTrafficRaw['brown_X'] >= sensorX - self.pixelsAroundSensor) & (dataTrafficRaw['brown_X'] <= sensorX + self.pixelsAroundSensor) &\
                                          (dataTrafficRaw['brown_Y'] >= sensorY - self.pixelsAroundSensor) & (dataTrafficRaw['brown_Y'] <= sensorY + self.pixelsAroundSensor))
                                      ]

        dataTrafficFilter = dataTrafficFilter.append(dataTrafficReduced)

    dataTrafficFilter = dataTrafficFilter.drop(columns=["Unnamed: 0"], axis=1)

    return dataTrafficFilter
