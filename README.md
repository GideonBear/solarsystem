# solarsystem


This report was written during my work on this project, and serves as documentation of my process.

## Idea
My idea is to build a model of our solar system. Using my (basic) knowledge of gravitational forces, simply model
all the planets and see how accurate it is. For that I would need a database
containing position and velocity of all the planets. Then I would want to see how accurate my model is,
and how long it takes for significant inaccuracies to take place.

## Getting the data
I decided on getting position and velocities relative to the sun, as that's the most logical.
I did some searching around and found this database from NASA, the [Horizons System](https://ssd.jpl.nasa.gov/horizons/).
Its data is available via a simple web-app, which is perfect. It delivers X, Y, and Z-values for position and velocity
relative to any body, from any time (within a certain time-frame). I started looking if it has an API, to automate fetching values and
loading them into the model.

I wrote a client for the API that is capable of getting position and velocity data of any planet.
I will then put this in the format that Coach 7 understands, and also use it to compare to the results of the modelling.

## Writing the model
I started up Coach 7 and did the Constructing Text model tutorial.
Actually, scrap that. Coach doesn't even contain 3d graphs; I'll just use Python for the model as well.
I'll use matplotlib to show some nice 3d-models to be able to sanity-check without needing to run the numbers every time.

First I started coding up the gravitational force formula, and the logic for decomposing those forces, so that
they can be turned into x-, y-, and z-accelerations

After some time, I now have the classes `Body`, representing a bodies mass, and position and velocity in all three dimensions,
and `Force`, representing a force in all three dimensions. I can calculate the gravitational force of a body on another body,
decompose it, then apply it to the body.

I then fetched and hardcoded the mass of all 9 bodies (incl. sun).

After some time, and only(!) two small bugs I am now looking at a live 3d representation of Mercury circling around the sun!
I am extremely surprised that there were no real issues, and that all the formulas were correct the first time.
This saves a lot of time. Adding the other planets is easy enough.

## Inaccuracies

I also made a system to see my model and the actual data diverge.

After making the model apply gravity from every body to every other body, Mercury is still very inaccurate,
but the far-away planets are fine.

I just realized I should probably render the actual positions as well, that would be fun! I made them render
transparently, which showed inaccuracies visually nicely.

I noticed two types of inaccuracies:

### Cyclic inaccuracies
Some inaccuracies were purely cyclic, and disappeared after a full cycle was done. For example, in the first cycle
Venus reached a positional inaccuracy of up to 5.41e09 m, but after a full cycle this was back to 3.47e08 m.

### Permanent inaccuracies
There was also a noticeable permanent inaccuracy over longer periods of time. For example, Venus got an inaccuracy of 5.21e09 m
at its lowest in its cycle after 25 years, which was only 5.81e08 m after a single year. I will call this
lowest inaccuracy in its cycle the permanent inaccuracy.

### Different planets
The inaccuracies (mostly the permanent ones) differed wildly between planets.
Mercury for example, developed a permanent inaccuracy of 4.20e10 m after only a year,
which is insanely high given that the length of the orbit is only around 3.5e11 m.
However, far-away planets like neptune only reach that order of magnitude after 15-25 years; which then still is very
small compared to the orbit length of 2.80e13 m.

## Sources of inaccuracies and influence of step size
I think the major source of inaccuracy here is that I am completely disregarding any pull that the planets have on the sun.
This probably especially affect Mercury, which is the closest to the sun.
[TODO: STEP SIZE TESTEN EN VERGELIJKEN MET CIJFERS HIERBOVEN]

## Conclusion
