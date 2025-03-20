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
    times: Sequence[datetime]

    def get(self) -> dict[datetime, Datapoint]:
        resp = requests.get(URL, params={
            "COMMAND": str(self.planet.value),
            "OBJ_DATA": "NO",
            "EPHEM_TYPE": "VECTORS",
            "CENTER": "500@10",  # This is the sun, not the solar system barycentre, so that the sun does not have to be calculated separately
            # "START_TIME": format_time(self.start_time),
            # "STOP_TIME": format_time(self.stop_time),
            # "STEP_SIZE": self.step_size,
            "TLIST": " ".join(format_time(time) for time in self.times),
        })
        if not resp.status_code == 200:
            raise Exception(resp)
        data = resp.json()

        if "error" in data:
            raise Exception(data["error"])
        result_s: str = data["result"]

        _, result_s = result_s.split("$$SOE")
        result_s, _ = result_s.split("$$EOE")
        result_s = result_s.strip()

        result = [
            Datapoint.from_lines(part) for part in grouper(
                (line.strip() for line in result_s.split("\n")),
                4, incomplete="strict"
            )
        ]

        assert len(result) == len(self.times)
        return dict(zip(self.times, result))


@dataclass
class Datapoint:
    # m
    x: float
    y: float
    z: float
    # m/s
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
        x = float(xs.replace("Y", "").strip()) * 1000
        y = float(ys.replace("Z", "").strip()) * 1000
        z = float(zs.strip()) * 1000

        _, vxs, vys, vzs = vxvyvz.split("=")
        vx = float(vxs.replace("VY", "").strip()) * 1000
        vy = float(vys.replace("VZ", "").strip()) * 1000
        vz = float(vzs.strip()) * 1000

        # print(f"{x=}")
        # print(f"{y=}")
        # print(f"{z=}")
        # print(f"{vx=}")
        # print(f"{vy=}")
        # print(f"{vz=}")
        return cls(x, y, z, vx, vy, vz)
