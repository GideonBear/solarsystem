from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pprint import pprint

import requests
from astropy.time import Time
from more_itertools import grouper

URL = "https://ssd.jpl.nasa.gov/api/horizons.api"


def format_time(time: datetime) -> str:
    return time.strftime(f"\'%Y-%m-%d %H:%M:%S.%f\'")


class Planet(Enum):
    MERCURY = 199
    VENUS = 299
    EARTH = 399
    MARS = 499
    JUPITER = 599
    SATURN = 699
    URANUS = 799
    NEPTUNE = 899

@dataclass
class Query:
    planet: Planet
    start_time: datetime
    stop_time: datetime
    step_size: str

    def get(self):
        data = requests.get(URL, params={
            "COMMAND": str(self.planet.value),
            "OBJ_DATA": "NO",
            "EPHEM_TYPE": "VECTORS",
            "CENTER": "500@0",
            "START_TIME": format_time(self.start_time),
            "STOP_TIME": format_time(self.stop_time),
            "STEP_SIZE": self.step_size,
        }).json()

        if "error" in data:
            raise Exception(data["error"])
        result = data["result"]

        _, result = result.split("$$SOE")
        result, _ = result.split("$$EOE")
        result = result.strip()

        result = (line.strip() for line in result.split("\n"))
        result = grouper(result, 4, incomplete="strict")
        result = [Datapoint.from_lines(part) for part in result]

        return result


@dataclass
class Datapoint:
    time: datetime
    # km
    x: float
    y: float
    z: float
    # km/s
    vx: float
    vy: float
    vz: float

    @classmethod
    def from_lines(cls, lines):
        if not len(lines) == 4:
            raise Exception(lines)

        time, xyz, vxvyvz, _ = lines

        time, _ = time.split("=")
        time = time.strip()
        time = Time(time, format="jd", scale="tdb").to_datetime()

        _, x, y, z = xyz.split("=")
        x = float(x.replace("Y", "").strip())
        y = float(y.replace("Z", "").strip())
        z = float(z.strip())

        _, vx, vy, vz = vxvyvz.split("=")
        vx = float(vx.replace("VY", "").strip())
        vy = float(vy.replace("VZ", "").strip())
        vz = float(vz.strip())

        return cls(time, x, y, z, vx, vy, vz)
