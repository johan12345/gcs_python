from typing import List

import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.gridspec import GridSpec
import datetime as dt

from matplotlib.widgets import Slider
from sunpy.map import Map
from sunpy.net import helioviewer
import numpy as np

from gcs import gcs_mesh, rotate_mesh, gcs_mesh_sunpy
from utils.debounce import debounce

hv = helioviewer.HelioviewerClient()
straight_vertices, front_vertices, circle_vertices = 10, 10, 20

def running_difference(a, b):
    return Map(b.data * 1.0 - a.data * 1.0, b.meta)


def load_image(spacecraft: str, date: dt.datetime, runndiff: bool):
    if spacecraft == 'STA':
        observatory = 'STEREO_A'
        instrument = 'SECCHI'
        detector = 'COR2'
    elif spacecraft == 'STB':
        observatory = 'STEREO_B'
        instrument = 'SECCHI'
        detector = 'COR2'
    elif spacecraft == 'SOHO':
        observatory = 'SOHO'
        instrument = 'LASCO'
        detector = 'C3'
    else:
        raise ValueError(f'unrecognized spacecraft: {spacecraft}')
    f = Map(hv.download_jp2(date,
                            observatory=observatory,
                            instrument=instrument,
                            detector=detector))
    if runndiff:
        f2 = Map(hv.download_jp2(date - dt.timedelta(hours=1),
                                 observatory=observatory,
                                 instrument=instrument,
                                 detector=detector))
        return running_difference(f2, f)
    else:
        return f


def gcs_gui(date: dt.datetime, spacecraft: List[str], runndiff: bool = False):
    fig = plt.figure(figsize=(5 * (len(spacecraft) + 1), 5))
    spec = GridSpec(ncols=len(spacecraft) + 1, nrows=7, figure=fig)

    s_half_angle = Slider(fig.add_subplot(spec[0, 0]), 'Half angle', 0, 90, valinit=25)
    s_height = Slider(fig.add_subplot(spec[1, 0]), 'Height', 0, 24, valinit=8.79)
    s_kappa = Slider(fig.add_subplot(spec[2, 0]), '$\kappa$', 0, 1, valinit=0.26)
    s_lat = Slider(fig.add_subplot(spec[3, 0]), 'Latitude', -90, 90, valinit=-1)
    s_lon = Slider(fig.add_subplot(spec[4, 0]), 'Longitude', 0, 360, valinit=354)
    s_tilt = Slider(fig.add_subplot(spec[5, 0]), 'Tilt angle', -90, 90, valinit=5)
    sliders = s_half_angle, s_height, s_kappa, s_lat, s_lon, s_tilt

    mesh_plots = []
    axes = []
    images = []
    for i, sc in enumerate(spacecraft):
        image = load_image(sc, date, runndiff)
        images.append(image)

        ax = fig.add_subplot(spec[:, i + 1], projection=image)
        axes.append(ax)

        image.plot(ax, cmap='Greys_r', norm=colors.Normalize(vmin=-30, vmax=30) if runndiff else None)

    @debounce(0.2, fig)
    def plot_mesh(*_):
        half_angle = np.radians(s_half_angle.val)
        height = s_height.val
        kappa = s_kappa.val
        lat = np.radians(s_lat.val)
        lon = np.radians(s_lon.val)
        tilt = np.radians(s_tilt.val)

        # delete previous plots
        for p in mesh_plots:
            p.remove()
            del p
        mesh_plots.clear()

        for image, ax in zip(images, axes):
            mesh = gcs_mesh_sunpy(date, half_angle, height, straight_vertices, front_vertices, circle_vertices, kappa,
                                  lat, lon, tilt)

            p = ax.plot_coord(mesh.transform_to(image.coordinate_frame), '.', ms=2, color='blue', scalex=False, scaley=False)
            mesh_plots.append(p[0])

    plot_mesh()
    for slider in sliders:
        slider.on_changed(plot_mesh)

    fig.canvas.draw()
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    spacecraft = 'STA', 'SOHO'
    date = dt.datetime(2020, 4, 15, 6, 54)
    gcs_gui(date, spacecraft, runndiff=True)
