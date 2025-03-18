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
relative to any body, from any time. I started looking if it has an API, to automate fetching values and
loading them into the model.

I wrote a client for the API that is capable of getting position and velocity data of any planet.
I will then put this in the format that Coach 7 understands, and also use it to compare to the results of the modelling.

## Writing the model
