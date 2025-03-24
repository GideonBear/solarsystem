from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import sqrt, log
from sys import stderr
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
MERCURY = Planet(api.Planet.MERCURY, "mercury", "grey", 3.302e23, 2439.4e3)
VENUS = Planet(api.Planet.VENUS, "venus", "brown", 48.685e23, 6051.84e3)
EARTH = Planet(api.Planet.EARTH, "earth", "blue", 5.97219e24, 6371.01e3)
MARS = Planet(api.Planet.MARS, "mars", "red", 6.4171e23, 3389.92e3)
JUPITER = Planet(api.Planet.JUPITER, "jupiter", "yellow", 18.9819e26, 69911e3)
SATURN = Planet(api.Planet.SATURN, "saturn", "orange", 5.6834e26, 58232e3)
URANUS = Planet(api.Planet.URANUS, "uranus", "cyan", 86.813e24, 25362e3)
NEPTUNE = Planet(api.Planet.NEPTUNE, "neptune", "blue", 102.409e24, 24624e3)


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
    def from_datapoint(cls, planet: Planet, datapoint: Datapoint) -> Self:
        return cls(
            planet,
            datapoint.x,
            datapoint.y,
            datapoint.z,
            datapoint.vx,
            datapoint.vy,
            datapoint.vz,
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

    def dist_tot(self, other: Self | Datapoint) -> float:
        # a^2 + b^2 + c^2 = d^2
        return sqrt(
              pow(abs(self.x - other.x), 2)
            + pow(abs(self.y - other.y), 2)
            + pow(abs(self.z - other.z), 2)
        )

    def vel_diff_tot(self, other: Self | Datapoint) -> float:
        # a^2 + b^2 + c^2 = d^2
        return sqrt(
            pow(abs(self.vx - other.vx), 2)
            + pow(abs(self.vy - other.vy), 2)
            + pow(abs(self.vz - other.vz), 2)
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


def check_accuracy(body: Body, data: Datapoint) -> None:
    pos_diff = body.dist_tot(data)
    pos_oom = max(abs(x) for x in (data.x, data.y, data.z))
    pos_acc = pos_diff / pos_oom
    vel_diff = body.vel_diff_tot(data)
    vel_oom = max(abs(x) for x in (data.vx, data.vy, data.vz))
    vel_acc = vel_diff / vel_oom

    print(f"    {body.name:>7}:", end="", file=stderr)
    for (diff, oom, acc) in ((pos_diff, pos_oom, pos_acc), (vel_diff, vel_oom, vel_acc)):
        print(
            f"    Position: absolute difference {diff:e} at oom {oom:e} inaccuracy {f"{acc:%}":>11}",
            end="",
            file=stderr,
        )
        print(f"{diff:e},{oom:e},{acc:e},", end="")
    print(file=stderr)


def main() -> None:
    # Start values
    t = 0.0  # model time in seconds
    dt = 60 * 60 * 24  # model dt (step size) in seconds

    # min start_time: 1750
    start_time = datetime(1900, 1, 2, 3, 4, 5)  # 2025-01-02 03:04:05
    current_time = start_time  # real time current
    check_start_time = datetime(1900, 1, 2, 3, 4, 5)
    # check_start_time = start_time
    # For 1750: max 5000-10000 (* 60 * 60 * 24)
    dcheck_ratio = 365 * 10  # How many model steps should pass before doing another check
    dcheck = timedelta(seconds=dt * dcheck_ratio)  # thus this is the time between each check
    checks = 25  # checks to be done (should not be higher than 25)
    t_tot = (check_start_time - start_time).total_seconds() + (dt * dcheck_ratio * checks)  # total model time
    times = [start_time] + [check_start_time + (i * dcheck) for i in range(checks)]

    plot_on_check = True  # Whether to plot for each check
    plot_on_interval = None  # On which interval of dt to plot, if any

    # Body initialization

    planets = (MERCURY, VENUS, EARTH, MARS, JUPITER, SATURN, URANUS, NEPTUNE)
    bodies: list[tuple[Body, dict[datetime, Datapoint] | None]] = [
        (Body(SUN, 0, 0, 0, 0, 0, 0), None),
    ]

    for planet in planets:
        assert planet.api_planet
        data = api.Query(planet.api_planet, times).get()
        bodies.append((
            Body.from_datapoint(planet, data[start_time]),
            data,
        ))

    # Plot initialization

    # mplstyle.use('fast')

    fig, axes = plt.subplots(
        1,
        3,
        subplot_kw={"projection": "3d"},
        figsize=(100, 100),
    )

    sizes = (1e13, 1e12, 4e11)  # Sizes of the subgraphs
    axes = list(zip(axes, sizes))

    print("time,", end="")
    for body, _data in bodies:
        if body.planet == SUN:
            continue
        print(f"{body.name}_pos_diff,{body.name}_pos_oom,{body.name}_pos_acc,", end="")
        print(f"{body.name}_vel_diff,{body.name}_vel_oom,{body.name}_vel_acc,", end="")
    print()

    i = 0
    while t < t_tot:
        i += 1

        if current_time in bodies[1][1]:
            dtime = current_time - start_time
            print(f"===== Inaccuracies at {dtime}", file=stderr)
            print(f"{current_time},", end="")
            for body, data in bodies:  # type: ignore
                if body.planet == SUN:
                    # Always 0, 0, 0, 0, 0, 0
                    continue
                check_accuracy(body, data[current_time])
            print()
            print(file=stderr)

        # Advance time
        t += dt
        current_time += timedelta(seconds=dt)

        # Update positions and velocities

        for body, _data in bodies:
            if body.planet == SUN:
                # Skip sun gravity to keep it centered
                continue

            for other, _data in bodies:
                # Apply gravity from all other bodies (incl. the sun)
                if other == body:
                    continue

                FG = other.gravitational_force(body)
                FG_decomposed = Force.from_res(other, body, FG)
                body.apply_force(FG_decomposed, dt)

            body.update_position(dt)

        # Plot

        if (plot_on_check and current_time in bodies[1][1]) or (plot_on_interval and i % plot_on_interval == 0):
            for ax, size in axes:
                for body, data in bodies:  # type: ignore
                    display_size = max(
                        log(body.r, 1.3),
                        10,
                    ) / 10
                    ax.plot(
                        body.x, body.y, body.z,
                        marker="o",
                        markersize=display_size,
                        color=body.color,
                    )
                    if data and current_time in data:
                        this = data[current_time]
                        ax.plot(
                            this.x, this.y, this.z,
                            marker="o",
                            markersize=display_size,
                            color=body.color,
                            alpha=0.5,
                        )

                ax.set_xlim((-size / 2, size / 2))
                ax.set_ylim((-size / 2, size / 2))
                ax.set_zlim((-size / 2, size / 2))

            plt.pause(0.5)
            for ax, size in axes:
               ax.clear()

    # plt.show()


if __name__ == "__main__":
    main()
