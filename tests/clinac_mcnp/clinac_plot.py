import numpy as np
import pickle
from scipy import stats
import yt
import os
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

if not os.path.exists("./matrix.py_obj"):
    with open("photo.out_temp", "w"):
        pass

    with open("archive/clinac_no_target_h2_photo.out", "r") as f:
        cleanstring = f.read().replace("\n", " ").replace("_", "\n")
        with open("photo.out_temp", "a") as f2:
            f2.write(cleanstring)

    E_p, _, zaid, _, x, y, z, _, _, _, _, _, ux, uy, uz, _, _ = \
        np.loadtxt("photo.out_temp", unpack=True)
    print np.min(z), np.max(z)
    xyz = np.vstack([x, y, z])
    kde = stats.gaussian_kde(xyz)

    # Evaluate kde on a grid
    xmin, ymin, zmin = x.min(), y.min(), z.min()
    xmax, ymax, zmax = x.max(), y.max(), z.max()
    xi, yi, zi = np.mgrid[xmin:xmax:100j, ymin:ymax:100j, zmin:zmax:100j]
    coords = np.vstack([item.ravel() for item in [xi, yi, zi]])
    density = 1.0E10 * 0.000115 * kde(coords).reshape(xi.shape)
    print np.min(density)
    print np.max(density)
    data = dict(density=(density, "1/cm**3"))
    bbox = np.array([[xmin, xmax], [ymin, ymax], [zmin, zmax]])
    with open("./matrix.py_obj", "w") as pickle_file:
        pickle.dump((data, density, bbox), pickle_file)
else:
    with open("./matrix.py_obj", "r") as pickle_file:
        data, density, bbox = pickle.load(pickle_file)
ds = yt.load_uniform_grid(data, density.shape, length_unit="cm", bbox=bbox,
                          nprocs=20)


sphere = ds.sphere("max", (20.0, "cm"))
surface1 = ds.surface(sphere, "density", 1.0E0)
surface2 = ds.surface(sphere, "density", 1.0E-1)
surface3 = ds.surface(sphere, "density", 1.0E-2)
surface4 = ds.surface(sphere, "density", 1.0E-3)
#surface1.export_obj("density1e0", color_field="temperature")
#surface2.export_obj("density1en1", color_field="temperature")
#surface3.export_obj("density1en2", color_field="temperature")
#surface4.export_obj("density1en3", color_field="temperature")

# Color this isodensity surface according to the log of the temperature field
colors = yt.apply_colormap(surface2["density"], cmap_name="hot")

# Create a 3D matplotlib figure for visualizing the surface
fig = plt.figure()
ax = fig.gca(projection='3d')
p3dc1 = Poly3DCollection(surface2.triangles, linewidth=0.0)
p3dc2 = Poly3DCollection(surface3.triangles, linewidth=0.0)
p3dc3 = Poly3DCollection(surface4.triangles, linewidth=0.0)

#draw cube
x = []
y = []
z = []

# Set the surface colors in the right scaling [0,1]
#p3dc.set_facecolors(colors[0,:,:]/255.)
ax.add_collection(p3dc1)
ax.add_collection(p3dc2)
ax.add_collection(p3dc3)

# Let's keep the axis ratio fixed in all directions by taking the maximum
# extent in one dimension and make it the bounds in all dimensions
ax.auto_scale_xyz([-150., 100.], [-100., 100.], [-300., 100.])

# Save the figure
plt.savefig("%s_Surface.png" % ds)
'''
# mi, ma = ds.all_data().quantities.extrema('density')

mi = np.min(density)
ma = np.max(density)
tf = yt.ColorTransferFunction((mi, ma), grey_opacity=True)

# Choose a vector representing the viewing direction.
L = [0.5, 0.5, 0.5]
# Define the center of the camera to be the domain center
c = [0.0, 0.0, -130.]
# Define the width of the image
W = 3.0 * ds.domain_width[0]
# Define the number of pixels to render
Npixels = 1024

cm = yt.make_colormap([([227. / 255., 174. / 255., 36. / 255.], 10),
                       ('white', 10)], name='new_gold', interpolate=True)

cam = ds.camera(c, L, W, Npixels, tf, fields=['density'],
                north_vector=[0, 0, 1], steady_north=True,
                sub_samples=5, log_fields=[False])

cam.transfer_function.map_to_colormap(mi, ma, colormap='new_gold')
im = cam.snapshot(transparent=True)
im.write_png("volume.png", background=None)
print "saved camera?"
'''
