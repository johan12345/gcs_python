import datetime as dt
import json
import os
from typing import List

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from astropy import units
from matplotlib import colors
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Button
from sunpy import log
from sunpy.map import Map
from sunpy.net import helioviewer

from gcs import gcs_mesh_sunpy
from utils.widgets import SliderAndTextbox

matplotlib.use('Qt5Agg')

hv = helioviewer.HelioviewerClient()
straight_vertices, front_vertices, circle_vertices = 10, 10, 20
filename = 'gcs_params.json'

# disable sunpy warnings
log.setLevel('ERROR')


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


def save_params(params):
    with open(filename, 'w') as file:
        json.dump(params, file)


def load_params():
    if os.path.exists(filename):
        with open(filename) as file:
            return json.load(file)
    else:
        # start with default values
        return {
            'half_angle': 25,
            'height': 10,
            'kappa': 0.25,
            'lat': 0,
            'lon': 0,
            'tilt': 0
        }


def gcs_gui(date: dt.datetime, spacecraft: List[str], runndiff: bool = False):
    fig = plt.figure(figsize=(5 * (len(spacecraft) + 1), 5))
    spec = GridSpec(ncols=len(spacecraft) + 1, nrows=7, figure=fig)

    params = load_params()
    s_half_angle = SliderAndTextbox(fig, spec[0, 0], 'Half angle', 0, 90, valinit=params['half_angle'])
    s_height = SliderAndTextbox(fig, spec[1, 0], 'Height', 0, 24, valinit=params['height'])
    s_kappa = SliderAndTextbox(fig, spec[2, 0], '$\kappa$', 0, 1, valinit=params['kappa'])
    s_lat = SliderAndTextbox(fig, spec[3, 0], 'Latitude', -90, 90, valinit=params['lat'])
    s_lon = SliderAndTextbox(fig, spec[4, 0], 'Longitude', 0, 360, valinit=params['lon'])
    s_tilt = SliderAndTextbox(fig, spec[5, 0], 'Tilt angle', -90, 90, valinit=params['tilt'])
    sliders = s_half_angle, s_height, s_kappa, s_lat, s_lon, s_tilt

    b_save = Button(fig.add_subplot(spec[6, 0]), 'Save')

    mesh_plots = []
    axes = []
    images = []
    for i, sc in enumerate(spacecraft):
        image = load_image(sc, date, runndiff)
        images.append(image)

        ax = fig.add_subplot(spec[:, i + 1], projection=image)
        axes.append(ax)

        image.plot(ax, cmap='Greys_r', norm=colors.Normalize(vmin=-30, vmax=30) if runndiff else None)

    def plot_mesh(*_):
        half_angle = np.radians(s_half_angle.val)
        height = s_height.val
        kappa = s_kappa.val
        lat = np.radians(s_lat.val)
        lon = np.radians(s_lon.val)
        tilt = np.radians(s_tilt.val)

        for i, (image, ax) in enumerate(zip(images, axes)):
            # create GCS mesh
            mesh = gcs_mesh_sunpy(date, half_angle, height, straight_vertices, front_vertices, circle_vertices, kappa,
                                  lat, lon, tilt)

            if len(mesh_plots) <= i:
                # new plot
                p = ax.plot_coord(mesh, '.', ms=2, color='blue', scalex=False, scaley=False)[0]
                mesh_plots.append(p)
            else:
                # update plot
                p = mesh_plots[i]

                frame0 = mesh.frame.transform_to(image.coordinate_frame)
                xdata = frame0.spherical.lon.to_value(units.deg)
                ydata = frame0.spherical.lat.to_value(units.deg)
                p.set_xdata(xdata)
                p.set_ydata(ydata)
                ax.draw_artist(p)

        fig.canvas.update()
        fig.canvas.flush_events()

    def get_params_dict():
        return {
            'half_angle': s_half_angle.val,
            'height': s_height.val,
            'kappa': s_kappa.val,
            'lat': s_lat.val,
            'lon': s_lon.val,
            'tilt': s_tilt.val
        }

    def save(*_):
        save_params(get_params_dict())
        plt.close(fig)

    plot_mesh()
    for slider in sliders:
        slider.on_changed(plot_mesh)
    b_save.on_clicked(save)

    fig.canvas.draw()
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    spacecraft = 'STA', 'SOHO'
    date = dt.datetime(2020, 4, 15, 5, 30)
    gcs_gui(date, spacecraft, runndiff=True)
