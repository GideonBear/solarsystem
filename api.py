from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Self

import requests
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
    time: datetime

    def get(self) -> Datapoint:
        data = requests.get(URL, params={
            "COMMAND": str(self.planet.value),
            "OBJ_DATA": "NO",
            "EPHEM_TYPE": "VECTORS",
            "CENTER": "500@10",  # This is the sun, not the solar system barycentre, so that the sun does not have to be calculated separately
            # "START_TIME": format_time(self.start_time),
            # "STOP_TIME": format_time(self.stop_time),
            # "STEP_SIZE": self.step_size,
            "TLIST": format_time(self.time),
        }).json()

        if "error" in data:
            raise Exception(data["error"])
        result: str = data["result"]

        _, result = result.split("$$SOE")
        result, _ = result.split("$$EOE")
        result = result.strip()

        result = (line.strip() for line in result.split("\n"))  # type: ignore
        result = grouper(result, 4, incomplete="strict")  # type: ignore
        result = [Datapoint.from_lines(part) for part in result]  # type: ignore

        assert len(result) == 1
        result = result[0]

        return result  # type: ignore


@dataclass
class Datapoint:
    # km
    x: float
    y: float
    z: float
    # km/s
    vx: float
    vy: float
    vz: float

    @classmethod
    def from_lines(cls, lines: Sequence[str]) -> Self:
        if not len(lines) == 4:
            raise Exception(lines)

        _, xyz, vxvyvz, _ = lines

        # time_s, _ = time_s.split("=")
        # time_s = time_s.strip()
        # time = Time(time_s, format="jd", scale="tdb").to_datetime()

        _, xs, ys, zs = xyz.split("=")
        x = float(xs.replace("Y", "").strip())
        y = float(ys.replace("Z", "").strip())
        z = float(zs.strip())

        _, vxs, vys, vzs = vxvyvz.split("=")
        vx = float(vxs.replace("VY", "").strip())
        vy = float(vys.replace("VZ", "").strip())
        vz = float(vzs.strip())

        # print(f"{x=}")
        # print(f"{y=}")
        # print(f"{z=}")
        # print(f"{vx=}")
        # print(f"{vy=}")
        # print(f"{vz=}")
        return cls(x, y, z, vx, vy, vz)
