# import matplotlib
# matplotlib.use("Qt4Agg")
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy import stats
import yt

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
xi, yi, zi = np.mgrid[xmin:xmax:10j, ymin:ymax:10j, zmin:zmax:50j]
coords = np.vstack([item.ravel() for item in [xi, yi, zi]])
density = kde(coords).reshape(xi.shape)
data = dict(density=(density, "1/cm**3"))
bbox = np.array([[xmin, xmax], [ymin, ymax], [zmin, zmax]])
ds = yt.load_uniform_grid(data, density.shape, length_unit="cm", bbox=bbox,
                          nprocs=20)

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
