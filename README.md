# solarsystem


This report was written during my work on this project, and serves as documentation of my process.

## Idea
My idea is to build a model of our solar system. Using my (basic) knowledge of gravitational forces, simply model
all the planets and see how accurate it is. For that I would need a database
containing position and velocity of all the planets. Then I would want to see how accurate my model is,
and how long it takes for significant inaccuracies to take place.

The solar system is easy to model, but hard to calculate due to a lot of different and constantly changing factors.
It is also almost impossible to do an experiment with gravity forces,
because the masses in the solar system are much larger than what we can manufacture here on Earth to test with.

## Getting the data
I decided on getting position and velocities relative to the sun, as that's the most logical.
I did some searching around and found this database from NASA, [JPL Horizons](https://ssd.jpl.nasa.gov/horizons/).
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

I then made a system to see my model and the actual data diverge, and realized I should probably
render the actual positions as well, that would be fun! I made them render transparently,
which showed inaccuracies visually nicely. I also have a text-based view of the inaccuracies, and it can export to csv.

I noticed two types of inaccuracies:

### Cyclic inaccuracies
Some inaccuracies were purely cyclic, and disappeared after a full cycle was done. For example, in the first cycle
Venus reached a positional inaccuracy of up to 2.37e08 m, but after a full cycle this was back to 5.99e07 m.

### Permanent inaccuracies
There was also a noticeable permanent inaccuracy over longer periods of time. For example, Venus got an inaccuracy of 1.19e09 m
at its lowest in its cycle after 25 years, which was only 8.81e07 m after a single year. I will call this
lowest inaccuracy in its cycle the permanent inaccuracy.

### Sources of inaccuracies and influence of step size
I think the major source of inaccuracy here is that I am completely disregarding any pull that the planets have on the sun.
This probably especially affect Mercury, which is the closest to the sun.

An obvious possible source of inaccuracy is the step size of the model. I am using an hour (60 * 60 s) as step size,
which makes the modelling process pretty fast. So, I tried reducing the step size to 1 minute (60 s). This took a really long time
(around 20 minutes on my home PC), and it actually did something. The permanent accuracy seemed to be worse somehow
(Venus' went up to 1.64e09 from 1.19e09), but Venus' cyclic accuracy went to at most 7.64e07 the first cycle, from the 2.37e08 when the
step size was 60 times higher.

Initially I had a step size of a day (60 * 60 * 24 s), but that resulted in wild inaccuracies (both permanent and cyclic),
especially Mercury, which had inaccuracies larger than its distance to the sun after only a year.

So I think most of the cyclic inaccuracy can be attributed simply to how detailed the model is.
Why the permanent inaccuracy gets worse though, is a mystery to me!

## Conclusion
It's pretty accurate! I'm happy with how it turned out, and actually shocked that the model worked on basically the first try.
