from gcs import gcs_mesh
import matplotlib.tri as mtri
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111, projection=Axes3D.name)

mesh, u, v = gcs_mesh(np.radians(25), 1, 20, 20, 20, 0.3)
tri = mtri.Triangulation(u, v)

ax.plot_trisurf(*mesh.T, triangles=tri.triangles)
ax.set_xlim3d([-1, 1])
ax.set_ylim3d([-1, 1])
ax.set_zlim3d([0, 1])
ax.set_box_aspect([1, 1, 0.5])

plt.show()
