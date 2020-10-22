from sunpy.map import Map
from sunpy.net import helioviewer

from gcs.geometry import gcs_mesh_sunpy
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

# create GCS mesh
date = dt.datetime(2020, 4, 15, 6, 54)
half_angle = 25
height = 8.79
kappa = 0.26
lat = np.radians(-1)
lon = np.radians(354)
tilt = np.radians(5)

mesh = gcs_mesh_sunpy(date, half_angle, height, 20, 20, 20, kappa, lat, lon, tilt)

# download STEREO-A COR2 image
hv = helioviewer.HelioviewerClient()
f = hv.download_jp2(date, observatory='STEREO_A', instrument='SECCHI', detector='COR2')
map = Map(f)

# plot image
fig = plt.figure()
ax = plt.subplot(projection=map)

map.plot(cmap='Greys_r')

# plot GCS mesh
ax.plot_coord(mesh, '.', ms=3)

plt.show()