import numpy as np
import pickle
from scipy import stats
import os
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from matplotlib import cm

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
xmin, zmin = x.min(), z.min()
xmax, zmax = x.max(), z.max()
xi, yi, zi = np.mgrid[xmin:xmax:2j, 0.:0.:1j, zmin:zmax:2j]
# coords = np.vstack([item.ravel() for item in [xi, yi, zi]])
# density = 1.0E10 * 0.000115 * kde(coords).reshape(xi.shape)
xi = np.arange(x.min(), x.max(), 100)
zi = np.arange(z.min(), z.max(), 100)
X, Z = np.meshgrid(xi, zi)
ys = 1.0E10 * 0.000115 * np.array([kde((xii, 0., zii)) for xii,zii in zip(np.ravel(X), np.ravel(Z))])
Y = ys.reshape(X.shape)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
concrete = ax.plot([-100, 100, 100, -100, -100], [0, 0, 0, 0, 0], [-15, -15, 0, 0, -15], 'k-')
subfloor = ax.plot([-100, 100, 100, -100, -100], [0, 0, 0, 0, 0], [-115, -115, -15, -15, -115], 'k-')
ax.set_xlim(-150, 100)
ax.set_ylim(-100, 100)
ax.set_zlim(-300, 100)
plt.show()
