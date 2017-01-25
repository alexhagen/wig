# MCNP Companion

MCNP (Monte Carlo N Particle) software, from LLNL, is an incredible tool for
simulation of neutrons, photons, and electrons.  I use this extensively for my
research, and it does a great job at a very complex task.  Unfortunately, it's a
nightmare to use.  Basically uncompilable by real humans (and not mythical
sys-admins), finicky about input decks and spaces, and almost completely text
only, there are lots of improvements that could be made.

As of now, this package is in a really alpha stage.  I think only I can use it
because of it's finickiness.  But, it allows for quick (and semantic)
development of MCNP decks using a **pipeline** method.  The **pipeline** method
will be familiar to those that use MCNP a lot.  The steps in the pipeline are:

1. Geometry (create `geo`s)
2. Materials (create `matl`s)
3. Cells (combine ``geo``s as needed and apply `matl`s)
4. Physics (there's a pretty hands off way to define the common physics)
5. Sources (create `source`)
6. Tallies (there's pretty hands off way for some tally specs now)
7. Run

The pipeline method means that this package is very semantic, so instead of just typing in numbers separated by spaces, you actually assign variables and document things.  You can also script mcnp because of python, for example if you wanted to move a source throughout a bunch of different simulations.  Finally, this code will, if you have the proper requirements, render pretty pictures of your simulation.

## Example

Let's learn by doing.  Following is a cutesy little example:

```python

```
