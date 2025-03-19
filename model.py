from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import sqrt, log
from typing import Self

import matplotlib.pyplot as plt
import matplotlib.style as mplstyle

import api
from api import Datapoint


# All values are in standard SI units


G = 6.67430e-11


@dataclass
class Planet:
    api_planet: api.Planet | None
    name: str
    color: str
    mass: float
    radius: float

# Values from Horizons, and verified in BiNaS
SUN = Planet(None, "sun", "yellow", 1988410e24, 695700e3)  # None, because it's only used for fetching position/velocity data, which is 0
MERCURY = Planet(api.Planet.MERCURY, "mercury", "red", 3.302e23, 2439.4e3)
VENUS = Planet(api.Planet.VENUS, "venus", "black", 48.685e23, 6051.84e3)
EARTH = Planet(api.Planet.EARTH, "earth", "black", 5.97219e24, 6371.01e3)
MARS = Planet(api.Planet.MARS, "mars", "black", 6.4171e23, 3389.92e3)
JUPITER = Planet(api.Planet.JUPITER, "jupiter", "black", 18.9819e26, 69911e3)
SATURN = Planet(api.Planet.SATURN, "saturn", "black", 5.6834e26, 58232e3)
URANUS = Planet(api.Planet.URANUS, "uranus", "black", 86.813e24, 25362e3)
NEPTUNE = Planet(api.Planet.NEPTUNE, "neptune", "black", 102.409e24, 24624e3)


@dataclass
class Body:
    planet: Planet
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float

    @classmethod
    def from_planet_time(cls, planet: Planet, time: datetime) -> Self:
        if planet.api_planet:
            datapoint = api.Query(planet.api_planet, time).get()
            return cls.from_datapoint(
                planet,
                datapoint,
            )
        else:
            return cls(
                planet,
                0, 0, 0, 0, 0, 0,
            )

    @classmethod
    def from_datapoint(cls, planet: Planet, datapoint: Datapoint) -> Self:
        # Make sure to convert from km and km/s of the Datapoint
        return cls(
            planet,
            datapoint.x * 1000,
            datapoint.y * 1000,
            datapoint.z * 1000,
            datapoint.vx * 1000,
            datapoint.vy * 1000,
            datapoint.vz * 1000,
        )

    @property
    def name(self) -> str:
        return self.planet.name

    @property
    def color(self) -> str:
        return self.planet.color

    @property
    def m(self) -> float:
        return self.planet.mass

    @property
    def r(self) -> float:
        return self.planet.radius

    def update_position(self, dt: float) -> None:
        # x1 = x0 + v * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt

    def apply_force(self, F: Force, dt: float) -> None:
        # F = m * a
        ax = F.x / self.m
        ay = F.y / self.m
        az = F.z / self.m

        # v1 = v0 + a * dt
        self.vx += ax * dt
        self.vy += ay * dt
        self.vz += az * dt

    def dist_tot(self, other: Self) -> float:
        # a^2 + b^2 + c^2 = d^2
        return sqrt(
              pow(abs(self.x - other.x), 2)
            + pow(abs(self.y - other.y), 2)
            + pow(abs(self.z - other.z), 2)
        )

    def gravitational_force(self, other: Self) -> float:
        # print(self.dist_tot(other))
        return G * self.m * other.m / pow(self.dist_tot(other), 2)  # FG = m1 * m2 / r^2


@dataclass
class Force:
    x: float
    y: float
    z: float

    @classmethod
    def from_res(cls, body_from: Body, body_to: Body, Ftot: float) -> Self:
        dist_tot = body_from.dist_tot(body_to)

        dist_x = body_from.x - body_to.x
        dist_y = body_from.y - body_to.y
        dist_z = body_from.z - body_to.z

        # x_angle = arccos(dist_x / dist_tot)
        # x = Ftot * cos(x_angle)
        x = Ftot * (dist_x / dist_tot)
        y = Ftot * (dist_y / dist_tot)
        z = Ftot * (dist_z / dist_tot)

        return cls(x, y, z)


def main() -> None:
    # Start values
    t = 0.0
    dt = 60 * 60 * 24

    time = datetime(2025, 1, 2, 3, 4, 5)  # 2025-01-02 03:04:05

    sun = Body.from_planet_time(SUN, time)
    mercury = Body.from_planet_time(MERCURY, time)

    mplstyle.use('fast')

    size = 1e12

    fig, ax = plt.subplots(
        1,
        1,
        subplot_kw={"projection": "3d"},
        figsize=(100, 100),
    )

    i = 0
    while t < 100000 * dt:
        i += 1

        # Advance time
        t += dt

        # Update positions and velocities

        FGsm = sun.gravitational_force(mercury)
        FGsm_decomposed = Force.from_res(sun, mercury, FGsm)
        mercury.apply_force(FGsm_decomposed, dt)
        mercury.update_position(dt)

        # Plot

        if i % 1234000 == 0:
            def plot(body: Body) -> None:
                display_size = max(
                    log(body.r, 1.3),
                    10,
                ) / 5
                ax.plot(
                    body.x, body.y, body.z,
                    marker="o",
                    markersize=display_size,
                    color=body.color,
                )

            plot(sun)
            plot(mercury)

            ax.set_xlim((-size / 2, size / 2))
            ax.set_ylim((-size / 2, size / 2))
            ax.set_zlim((-size / 2, size / 2))
            plt.pause(0.0001)
            ax.clear()

    # plt.show()


if __name__ == "__main__":
    main()
