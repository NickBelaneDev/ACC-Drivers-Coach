import json

setup_path = "src/assets/setups/placeholder_setup.json"

with open(setup_path, "r") as _setup:
    setup = json.load(_setup)
    print(setup)

class ACCSetup:
    def __init__(self, setup_file=setup_path):
        """Can be seen as a parser for ACC-Setup Files."""
        with open(setup_file, "r") as _sf:
            self.setup_file = json.load(_sf)

    def get_fuel_per_lap(self):
        return round(self.setup_file["basicSetup"]["tyres"]["strategy"]["fuelPerLap"], 2)

    def get_car_name(self):
        return self.setup_file["carName"]

    def get_mechanical_balance(self) -> dict:
        """Returns the mechanical balance parameters of the setup File:
            aRBFront, aRBRear, wheelRateFront, wheelRateRear, bumpStopRateFront, bumpStopRateRear,
            brakeBias, drivetrain, steerRatio

            :return: dictionary{"setup_parameter": value}
        """

        mech_balance = {}

        mech_balance["aRBFront"] = self.setup_file["advancedSetup"]["mechanicalBalance"]["aRBFront"]
        mech_balance["aRBRear"] = self.setup_file["advancedSetup"]["mechanicalBalance"]["aRBRear"]
        mech_balance["wheelRateFront"] = self.setup_file["advancedSetup"]["mechanicalBalance"]["wheelRate"][0]
        mech_balance["wheelRateRear"] = self.setup_file["advancedSetup"]["mechanicalBalance"]["wheelRate"][2]

        mech_balance["drivetrain"] = self.setup_file["advancedSetup"]["drivetrain"]

        mech_balance["brakeBias"] = self.setup_file["advancedSetup"]["mechanicalBalance"]["brakeBias"]
        mech_balance["steerRatio"] = self.setup_file["basicSetup"]["alignment"]["steerRatio"]
        return mech_balance

    def get_aero(self):
        """Returns the Aero Parameters of the setup

        """

        aero = {}
        aero["rideHeightFront"] = self.setup_file["advancedSetup"]["aeroBalance"]["rideHeight"][0]
        aero["rideHeightRear"] = self.setup_file["advancedSetup"]["aeroBalance"]["rideHeight"][2]
        aero["rearWing"] = self.setup_file["advancedSetup"]["aeroBalance"]["rearWing"]
        aero["brakeDuctFront"] = self.setup_file["advancedSetup"]["aeroBalance"]["brakeDuct"][0]
        aero["brakeDuctRear"] = self.setup_file["advancedSetup"]["aeroBalance"]["brakeDuct"][1]

        return aero

    def get_tyres_and_alignment(self) -> dict:
        """Returns the tyrePressure as well as camber, toe, casterLF and casterRF of the Setup File
            tyrePressure map = [LF, RF, LR, RR]
            :return:  tyrePressure, camberFront, camberRear, toeFront, toeRear, caster
        """


        tyres = {"tyrePressure": self.setup_file["basicSetup"]["tyres"]["tyrePressure"],
                 "camberFront": self.setup_file["basicSetup"]["alignment"]["camber"][0],
                 "camberRear": self.setup_file["basicSetup"]["alignment"]["camber"][2],
                 "toeFront": self.setup_file["basicSetup"]["alignment"]["toe"][0],
                 "toeRear": self.setup_file["basicSetup"]["alignment"]["toe"][2],
                 "caster": self.setup_file["basicSetup"]["alignment"]["casterLF"]
                 }
        return tyres

    def get_electronics(self) -> dict:
        """Returns the Electronics of the Setup File."""
        electronics = self.setup_file["basicSetup"]["electronics"]

        return electronics

    def get_dampers(self) -> dict:
        """Returns all Damper Parameters of the Setup File.

        :return: bumpSlowFront, bumpSlowRear, bumpFastFront, bumpFastRear, reboundSlowFront,
                 reboundSlowRear, reboundFastFront, reboundFastRear, bumpStopRateFront, bumpStopRateRear
        """
        dampers = {
            "bumpSlowFront": self.setup_file["advancedSetup"]["dampers"]["bumpSlow"][0],
            "bumpSlowRear": self.setup_file["advancedSetup"]["dampers"]["bumpSlow"][2],
            "bumpFastFront": self.setup_file["advancedSetup"]["dampers"]["bumpFast"][0],
            "bumpFastRear": self.setup_file["advancedSetup"]["dampers"]["bumpFast"][2],

            "reboundSlowFront": self.setup_file["advancedSetup"]["dampers"]["reboundSlow"][0],
            "reboundSlowRear": self.setup_file["advancedSetup"]["dampers"]["reboundSlow"][2],
            "reboundFastFront": self.setup_file["advancedSetup"]["dampers"]["reboundFast"][0],
            "reboundFastRear": self.setup_file["advancedSetup"]["dampers"]["reboundFast"][2],

            "bumpStopRateFront": self.setup_file["advancedSetup"]["mechanicalBalance"]["bumpStopRateUp"][0],
            "bumpStopRateRear": self.setup_file["advancedSetup"]["mechanicalBalance"]["bumpStopRateUp"][2]
        }

        return dampers

    def get_setup(self) -> dict:
        """Returns the Setup."""
        setup: dict = {}

        setup["carName"] = self.get_car_name()

        setup["tyres_and_alignment"] = self.get_tyres_and_alignment()
        setup["electronics"] = self.get_electronics()
        setup["mechanical_balance"] = self.get_mechanical_balance()
        setup["dampers"] = self.get_dampers()
        setup["aero"] = self.get_aero()

        return setup


    def set_new_setup(self, setup_path: str) -> dict:
        """Replaces the current used Setup File with a new one."""
        with open(setup_path, "r") as _s:
            self.setup_file = json.load(_s)
        return self.setup_file

def get_setup() -> str:
    """
    This function returns the complete Setup.JSON from a race car in Assetto Corsa Competizione as a string.
    Notes:
        - die Reihenfolge der Reifen in den Listen ist immer [LF, RF, LR, RR]
    :return: complete Setup from a race car in Assetto Corsa Competizione
    """
    acc_setup = ACCSetup()

    return json.dumps(acc_setup.get_setup())

if __name__ == "__main__":


    acc_setup = ACCSetup(setup_path)
    print(get_setup())
