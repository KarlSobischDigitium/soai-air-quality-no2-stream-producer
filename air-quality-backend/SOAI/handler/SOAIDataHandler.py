import logging

logger = logging.getLogger()


## Class which is the base of the different handlers. At the moment the SOAIDBHandler and SOAIDiskHandler exists.
class SOAIDataHandler:

    ## Constructor
    def __init__(self):
        pass

    ## This function applies general rules to the OpenAirCologne data.
    #
    # These rules need to be fullfilled in every case, whether the data is loaded from the disk or DB.
    # @param data Pandas data frame with data.
    # @param selectValidData Boolean if only valid data shall be loaded
    # @returns A checked and updated pandas data frame.
    def _fCheckOpenAir(self, data, selectValidData=True):
        data = data.rename(columns={"feed": "sensorID"})

        data = data.assign(sensorID=lambda d: d["sensorID"].str.split('-').map(lambda x: x[0]))
        data = data.sort_values("timestamp").reset_index(drop=True)

        # If set to True unvalid data will be discarded
        if selectValidData:
            logger.info("Select only valid data with query {hum <= 100 and r1!=-1 and r2!=-1}")
            data = data.query("hum <= 100 and r1!=-1 and r2!=-1")
            data = data.reset_index(drop=True)

        return data

    ## This function applies general rules to the Lanuv data.
    #
    # These rules need to be fullfilled in every case, whether the data is loaded from the disk or DB.
    # @param data Pandas data frame with data.
    # @param selectValidData Boolean if only valid sensor data shall be loaded
    # @returns A checked and updated pandas data frame.
    def _fCheckLanuv(self, data, selectValidData=True):
        data = data.rename(columns={"station": "sensorID"})

        data = data.sort_values("timestamp").reset_index(drop=True)

        if selectValidData is True:
            logger.warning("Select valid data is set to true, but no rules for valid data are given.")

        return data

    ## Dummy function for traffic data
    def _fCheckTraffic(self, data, selectValidData=True):
        data = data.sort_values("date").reset_index(drop=True)

        if selectValidData is True:
            logger.warning("Select valid data is set to true, but no rules for valid data are given.")

        return data
