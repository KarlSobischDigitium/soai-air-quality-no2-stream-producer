from datetime import date
from SOAI.tools.SOAIprepareTrafficDf import SOAIprepareTrafficDf


def main():
    createNew = True
    choosenSensor = ["VKCL", "VKTU", "RODE"]
    zippedTrafficFilesPath = "./data/traffic/raw/"
    pixelsAroundSensor = [3, 5, 10, 20]

    if createNew is True:
        for sensor in choosenSensor:
            for pixels in pixelsAroundSensor:
                prepareTrafficDf = SOAIprepareTrafficDf(sensor, zippedTrafficFilesPath, pixels)
                dataTrafficFilter = prepareTrafficDf.prepare()
                dataTrafficFilter.to_csv(f"{sensor}_{pixels}_{date.today().strftime('%Y%m%d')}.csv", sep=",")


if __name__ == '__main__':
    main()
