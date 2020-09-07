# OpenAir Cologne

### School of AI Cologne project in cooperation with OpenAir Cologne.

-------------------

## Run the Code

In order to run the project perform the following steps:
- Make sure you have *git* installed
- Clone the repository with **git clone https://gitlab.com/N.Stausberg/openair-cologne**
- Change to a unique branch with **git checkout -b someName**
- Inside the downloaded repository create logging folder **mkdir logs**
- Install all packages with **pip3 install -r requirements.txt** e.g in some virtual enviroment
- *Optional* install SOAI package with **pip3 install -e .**
- Set up the DB by including some enviroment variables in your *.bashrc\_profile*. The values can be found on the Trello board.
	**export OAC\_HOST="INFLUX DB ADDRESS"**
	**export OAC\_PORT="IINFLUX PORT"**
	**export OAC\_DB="IINFLUX DB NAME"**
- Download the *savedModels* folder (https://drive.google.com/open?id=1N7HErGvTEkgeP-AFburLsJjOM9atfw9A) and set a *SOAI_MODEL_PATH* environment variable to the folder of the saved models.
- Run **python example.ipynb**

There is a doxygen available it can be found at openair-cologne/SOAI/documentation/html/index.html.

------------------

## Informations about the sensors

The following data is available:
- **feed** - sensor id
- **hum** - humidity
- **temp** - temperature
- **pm10** and **pm25** - measurments of particulate matter
- **r1** and **r2** - measurments of NO2
- **rssi** - ?

Following issues are known:
- Sometime very high **hum** values can ocurre. Most likely due to hardware issues of the sensors.
- No measurment values for **pm10** and **pm25** since no sensors for particulate matter are available.
- High temperature values since the sensor misses a proper calibration, but it should be at least proportional to the real temperature.
- The resistor used for measurment value **r1** is wrong. Therefore **r2** is more reliable.
