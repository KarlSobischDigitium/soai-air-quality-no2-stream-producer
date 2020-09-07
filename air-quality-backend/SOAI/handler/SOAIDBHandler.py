from .SOAIDataHandler import SOAIDataHandler
from .SOAIDiskHandler import SOAIDiskHandler

import numpy as np
import pandas as pd
from influxdb import DataFrameClient
import time
import datetime
import os
import logging

logger = logging.getLogger()


## Class which handles the loading of data from a database.
class SOAIDBHandler(SOAIDataHandler):

    ## Constructor
    #
    # Sets the permission to use the database to False by default
    def __init__(self):
        self.permissionDB = False

    ## Sets up a client to a database. has to be called before a query is performed.
    def fSetupDB(self, host=os.environ.get("OAC_HOST"), port=os.environ.get("OAC_PORT"), database=os.environ.get("OAC_DB")):
        self.host = host
        self.port = port
        self.database = database

        self.permissionDB = True

    ## Query the databse. Only word if fSetupDB was called.
    def __fQueryInflux(self, query: str) -> dict:
        if self.permissionDB is True:
            logger.debug(f"Perform the query {query} to the database.")

            client = DataFrameClient(host=self.host, port=self.port, database=self.database)
            result = client.query(query)
            client.close()
        else:
            logger.error("No permission to connect to the database.")
            result = None

        return result

    ## Get the data for Lanuv sensors in the time frame now()-dStart to now()-dEnd
    def __fGetLanuvData(self, dStart, dEnd=0):
        lanuv_dict = self.__fQueryInflux("SELECT station, NO, OZON, NO2 AS no2, "
                                         "WRI AS wr, WGES AS wg, LTEM AS temp, "
                                         "WTIME as wtime, RFEU as hum "
                                         "FROM lanuv_f2 "
                                         f"WHERE time >= now() - "f"{dStart}d "
                                         "AND time <= now() - "f"{dEnd}d ")

        if len(lanuv_dict) == 0:
            logger.error(f"No data was found for time range now-{dStart} - now-{dEnd}. Return empty data frame.")
            return pd.DataFrame()

        # make clean data frame
        df_lanuv = lanuv_dict['lanuv_f2'] \
            .rename_axis('timestamp').reset_index()

        df_lanuv = df_lanuv[df_lanuv.timestamp.dt.minute == 0]
        df_lanuv = df_lanuv[df_lanuv.timestamp.dt.second == 0]

        df_lanuv = df_lanuv.assign(timestamp=pd.to_datetime(df_lanuv.timestamp.astype(np.int64) // 10 ** 6, unit='ms', utc=True))
        return df_lanuv

    ## Get the data for OpenAir Cologne sensors in the time frame now()-dStart to now()-dEnd
    def __fGetOpenAirData(self, dStart, dEnd=0, granularity="1h"):
        openair_dict = self.__fQueryInflux("SELECT "
                                           "median(hum) AS hum, median(pm10) AS pm10, "
                                           "median(pm25) AS pm25, median(r1) AS r1, "
                                           "median(r2) AS r2, median(rssi) AS rssi, "
                                           "median(temp) AS temp "
                                           "FROM all_openair "
                                           f"WHERE time >= now() - "f"{dStart}d "
                                           "AND time <= now() - "f"{dEnd}d "
                                           f"GROUP BY feed, time({granularity}) fill(-1)")
        if len(openair_dict) == 0:
            logger.error(f"No data was found for time range now-{dStart} - now-{dEnd}. Return empty data frame.")
            return pd.DataFrame()

        # clean dictionary keys
        openair_dict_clean = {k[1][0][1]: openair_dict[k]
                              for k in openair_dict.keys()}

        # initialize empty data frame
        df_openair = pd.DataFrame()

        # fill data frame with data from all frames
        # OPTIONAL: replace for-loop with map-reduce
        for feed in list(openair_dict_clean.keys()):
            df_feed = pd.DataFrame.from_dict(openair_dict_clean[feed]) \
                .assign(feed=feed) \
                .rename_axis('timestamp').reset_index()
            df_openair = df_openair.append(df_feed)

        # shift timestamp one hour into the future
        df_openair_shifted = df_openair \
            .assign(timestamp=lambda d: d.timestamp + pd.Timedelta(granularity))

        return df_openair_shifted

    ## Load data of the OpenAirCologne sensors from the DB
    #
    # @param dStart The amount of days in the past to start (interpreted now() - dStart)
    # @param dStep The amount of days which is fetched at once from the DB
    # @param granularity Granularity of the data as string (e.g. 1h or 5m)
    def fGetOpenAir(self, dStart, dStep=31, granularity="1h"):
        if dStep > 31:
            logger.error("In order not to overuse the data base the step size is set to a monthly frequency.")
            dStep = 31

        df = pd.DataFrame()
        for d in range(dStart, 0, -dStep):

            if (d - dStep) >= 0:
                logger.info(f"Load from DB from now-{d}d to now-{d-dStep}d.")
                df = df.append(self.__fGetOpenAirData(d, d - dStep, granularity), ignore_index=True)
            else:
                logger.info(f"Load from DB from now-{d}d to now-0d.")
                df = df.append(self.__fGetOpenAirData(d, 0, granularity), ignore_index=True)
                break

            # Be nice to the DB
            time.sleep(10)

        # Check the OpenAir data
        df = self._fCheckOpenAir(df)

        if df is None:
            logger.error("No data was found for the last {dStart} days.")
        else:
            logger.info(f"Loaded {len(df)} rows for the last {dStart} days.")

        df = df.set_index("timestamp", drop=True)

        return df

    ## Load data of the Lanuv sensors from the DB
    #
    # @param dStart The amount of days in the past to start (interpreted now() - dStart)
    # @param dStep The amount of days which is fetched at once from the DB
    def fGetLanuv(self, dStart, dStep=31):
        if dStep > 31:
            logger.error("In order not to overuse the data base the step size is set to a monthly frequency.")
            dStep = 31

        df = pd.DataFrame()
        for d in range(dStart, 0, -dStep):
            if (d - dStep) >= 0:
                logger.info(f"Load from DB from now-{d}d to now-{d-dStep}d.")
                df = df.append(self.__fGetLanuvData(d, d - dStep), ignore_index=True)
            else:
                logger.info(f"Load from DB from now-{d}d to now-0d.")
                df = df.append(self.__fGetLanuvData(d, 0), ignore_index=True)
                break

            # Be nice to the DB
            time.sleep(10)

        # Check the Lanuv data
        df = self._fCheckLanuv(df)

        if df is None:
            logger.error("No data was found for the last {dStart} days.")
        else:
            logger.info(f"Loaded {len(df)} rows for the last {dStart} days.")

        df = df.set_index("timestamp", drop=True)

        return df

    ## Update the data on the disk
    #
    # @param folderOpenAir Folder to OpenAir data
    # @param folderLanuv Folder to Lanuv data
    def fUpdateDiskData(self, folderOpenAir=os.environ.get("SOAI") + "/data/openair", folderLanuv=os.environ.get("SOAI") + "/data/lanuv"):
        diskHandler = SOAIDiskHandler()

        dfOpenAir = diskHandler.fGetOpenAir(os.environ.get("SOAI") + "/data/openair/", selectValidData=True)
        dfLanuv = diskHandler.fGetLanuv(os.environ.get("SOAI") + "/data/lanuv/")

        day1 = dfOpenAir.index.max().to_pydatetime().replace(tzinfo=None)
        day2 = datetime.datetime.now()
        days = (day2 - day1).days
        dfOpenAir_fromDB = self.fGetOpenAir(dStart=days)

        day1 = dfLanuv.index.max().to_pydatetime().replace(tzinfo=None)
        day2 = datetime.datetime.now()
        days = (day2 - day1).days
        dfLanuv_fromDB = self.fGetLanuv(dStart=days)

        i = 0
        while True:
            if os.path.exists(folderOpenAir + f"/df_openair{i}.parquet"):
                i += 1
            else:
                break

        dfOpenAir_fromDB.reset_index().to_parquet(folderOpenAir + f"/df_openair{i}.parquet")

        i = 0
        while True:
            if os.path.exists(folderLanuv + f"/df_lanuv{i}.parquet"):
                i += 1
            else:
                break

        dfLanuv_fromDB.reset_index().to_parquet(folderLanuv + f"/df_lanuv{i}.parquet")
