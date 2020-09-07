

## Class which represents a general sensor
class SOAISensor():

    ## Sets general parameters of a sensor
    #
    # @param sensorType Type of the sensor e.g. "OpenAirCologne" or "Lanuv". The type is normally set by inherited classes.
    # @param ID ID (sensorID) of the sensor
    # @param location Location of the sensor given as tuple (latitude, longitude)
    def __init__(self, sensorType, ID, location):
        self.ID = ID
        self.location = location
        self.active = False  # By default a sensor is not active
        self.type = sensorType

    def fGetID(self):
        return self.ID

    def fGetLocation(self):
        return self.location

    def fSetActive(self):
        self.active = True

    def fSetInactive(self):
        self.active = False

    def fIsActive(self):
        return self.active

    def fGetType(self):
        return self.type
