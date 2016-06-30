#import matplotlib
#matplotlib.use("Qt4Agg")
#import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy import stats

with open("photo.out_temp", "w"):
    pass

with open("archive/clinac_no_target_h2_photo.out", "r") as f:
    cleanstring = f.read().replace("\n", " ").replace("_", "\n")
    with open("photo.out_temp", "a") as f2:
        f2.write(cleanstring)

E_p, _, zaid, x, y, z, _, _, _, _, _, _, ux, uy, uz, _, _ = \
    np.loadtxt("photo.out_temp", unpack=True)

xyz = np.vstack([x,y,z])
kde = stats.gaussian_kde(xyz)
print "got kde"

# Evaluate kde on a grid
xmin, ymin, zmin = x.min(), y.min(), z.min()
xmax, ymax, zmax = x.max(), y.max(), z.max()
xi, yi, zi = np.mgrid[xmin:xmax:30j, ymin:ymax:30j, zmin:zmax:30j]
coords = np.vstack([item.ravel() for item in [xi, yi, zi]])
print "got coords"
density = kde(coords).reshape(xi.shape)
