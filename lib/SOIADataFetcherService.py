import logging
import simplejson
import os
import json

from SOAI.handler.SOAIDBHandler import SOAIDBHandler
from SOAI.handler.SOAIDiskHandler import SOAIDiskHandler
from SOAI.sensors.SOAISensorNetwork import SOAISensorNetwork


logger = logging.getLogger()


class SOIADataFetcherService():

  def update_sensor_setwork(self):
    self.soaiSensorNetwork = SOAISensorNetwork(os.getenv('SENSOR_NETWORK_CONFIG_PATH'))
    self.soaiSensorNetwork.fCheckNetwork()

  def fetch_data(self):
    sOAIDBHandler = SOAIDBHandler()
    sOAIDBHandler.fSetupDB()
    sOAIDiskHandler = SOAIDiskHandler()

    mapping_frame_oac = sOAIDiskHandler.fGetOpenAirSensors()

    look_back_range_in_days = 10

    data_oac = sOAIDBHandler.fGetOpenAir(look_back_range_in_days)
    data_oac = self.soaiSensorNetwork.fDataToNO2(data_oac)

    data_lanuv = sOAIDBHandler.fGetLanuv(look_back_range_in_days)
    mapping_frame_lanuv = sOAIDiskHandler.fGetLanuvSensors()

    sensor_no = []
    sensor_no2 = []
    sensor_ozon = []

    sensor_type = []
    sensor_id = []
    sensor_lat = []
    sensor_lon = []

    logger.debug('process oac data')

    # process openaircologne data
    for index, row in mapping_frame_oac.iterrows():
      data_station = data_oac[data_oac['sensorID'] == row['sensorID']]

      sensor_type.append('openair_cologne')
      sensor_id.append(row['sensorID'])
      sensor_lat.append(row['lat'])
      sensor_lon.append(row['lon'])

      if data_station.shape[0] > 0:
        sensor_no2.append(data_station['no2'].iloc[-1])
      else:
        sensor_no2.append(-1)

      sensor_ozon.append(-1)
      sensor_no.append(-1)

    logger.debug('process lanuf data')

    # process lanuf data
    for index, row in mapping_frame_lanuv.iterrows():
      data_station = data_lanuv[data_lanuv['sensorID'] == row['sensorID']]

      sensor_type.append('lanuv')
      sensor_id.append(row['sensorID'])
      sensor_lat.append(row['lat'])
      sensor_lon.append(row['lon'])

      if data_station.shape[0] > 0:
        sensor_no.append(data_station['NO'].iloc[-1])
        sensor_no2.append(data_station['no2'].iloc[-1])
        sensor_ozon.append(data_station['OZON'].iloc[-1])
      else:
        sensor_no2.append(-1)

    print(sensor_no2)

    data = {
      'sensors': {
        'sensor_type': json.loads(simplejson.dumps(sensor_type, ignore_nan=True)),
        'sensor_id': json.loads(simplejson.dumps(sensor_id, ignore_nan=True)),
        'lat': json.loads(simplejson.dumps(sensor_lat, ignore_nan=True)),
        'lon': json.loads(simplejson.dumps(sensor_lon, ignore_nan=True)),
        'no': json.loads(simplejson.dumps(sensor_no, ignore_nan=True)),
        'no2': json.loads(simplejson.dumps(sensor_no2, ignore_nan=True)),
        'ozon': json.loads(simplejson.dumps(sensor_ozon, ignore_nan=True)),
      }
    }
    logger.debug(simplejson.dumps(sensor_no2, ignore_nan=True))
    return data
