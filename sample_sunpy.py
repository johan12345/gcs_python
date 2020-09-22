from astropy.coordinates import SkyCoord
from sunpy.coordinates import sun, frames
from sunpy.map import Map
from sunpy.net import helioviewer

from gcs import gcs_mesh, rotate_mesh
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

# create GCS mesh
half_angle = 25
height = 8.79
kappa = 0.26
lat = np.radians(-1)
lon = np.radians(354)
tilt = np.radians(5)

mesh, u, v = gcs_mesh(half_angle, height, 20, 20, 20, kappa)
mesh = rotate_mesh(mesh, [lat, lon, tilt])

# download STEREO-A COR2 image
date = dt.datetime(2020, 4, 15, 6, 54)
hv = helioviewer.HelioviewerClient()
f = hv.download_jp2(date, observatory='STEREO_A', instrument='SECCHI', detector='COR2')
map = Map(f)

# plot image
fig = plt.figure()
ax = plt.subplot(projection=map)

map.plot(cmap='Greys_r')

# transform GCS mesh into correct coordinates and plot
mesh_coord = SkyCoord(*(mesh.T[[2, 1, 0], :] * sun.constants.radius), frame=frames.HeliographicStonyhurst, obstime=date, representation_type='cartesian')

ax.plot_coord(mesh_coord, '.', ms=3)

plt.show()