MCNP Companion
==============

MCNP (Monte Carlo N Particle) software, from LLNL, is an incredible tool
for simulation of neutrons, photons, and electrons. I use this
extensively for my research, and it does a great job at a very complex
task. Unfortunately, it's a nightmare to use. Basically uncompilable by
real humans (and not mythical sys-admins), finicky about input decks and
spaces, and almost completely text only, there are lots of improvements
that could be made.

This package will strive to solve a lot of these issues. First, this
package will provide a different way to compile than the (difficult)
``automake`` method that is currently shipped with MCNPX.

Secondly, this package will provide utilities to write input decks, a
utility to run your input decks either remotely or locally, and finally,
it will provide just a little visualization and results analysis.

Proposal for a generation script
--------------------------------

Ideally, a simple generation script would look like this:

.. code:: python

    import mcnp_companion

    # First, we initialize our scene and tell it that we'll use MCNPX
    scene = mcnp_companion(filename='example_scene', flavor='x',
                           comment='''An example scene to illustrate features of
                                      mcnp_companion''')

    # Now, we need to add all of our geometry to the scene
    geo = new geo()
    # Add a right plane parallelepiped
    gblock = geo.add_rpp(cx=1.0, cy=1.0, cz=1.0, lx=1.0, ly=2.0, lz=0.5,
                id='graphite-block')
    # Add a sphere
    asphere = geo.add_sph(c=(0., 0., 0.), r=20., id='universe')
    # Register this to the scene
    scene.geo(geo)

    # Now, we need to define a few materials
    graphite = new matl(chem_formula='C', id='graphite')
    air = new matl(atom_perc=[('H', 0.000151), ('N', 0.784437), ('O', 0.210750),
                              ('Ar', 0.004671)], id='air')
    # Register these to the scene
    scene.matl((graphite, matl))

    # Finally, we can use some automatic cell creation
    graphite_cell = new cell(gblock, graphite)
    air_cell = new cell(asphere, air)
    # register the cells to the scene
    scene.cells((graphite_cell, air_cell))

    # Add a source (otherwise why are you doing this?)
    clinac = new source(type='p', spectrum = [(0., 1., 2.), (0.9, 0.5, 0.1)],
                        shape='circle', dir='z-')

    # Now to add a few tally volumes
    det1 = new tally(cell=graphite_cell)
    det2 = new tally(c=(0., 0., 0.), r=1.)
    scene.tally((det1, det2))

    # Add some typical neutron physics - this will automatically fill
    scene.physics(nps=1E9)

    # Render the scene so you can see that you're doing it correctly
    scene.render('example_scene_render')

    # And, finally, run!
    scene.run(remote='ssh://ahagen@mars-ubuntu.dynu.com', sys='linux')

Now this doesn't exactly look like it'll save you any time compared to
writing an MCNP deck, but there are a couple things going on under the
hood that will save you plenty:

-  The rendering is better than VisEd, so it can be used for publishing
-  You can SCRIPT in Python, so running multiple similar tests should be
   easier
-  The ``matl`` module points out forgotten isotopes that might be
   important
-  The cells doing things themselves is WAY better
-  The physics are hands-off unless you're doing something esoteric
