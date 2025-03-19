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
I am extremely suprised that there were no real issues, and that all the formulas were correct the first time.
This saves a lot of time.
