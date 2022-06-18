import argparse
import datetime as dt
import json
import os
import sys
from typing import List

import matplotlib
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QComboBox
from astropy import units
from astropy.coordinates import concatenate
from matplotlib import colors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from sunpy import log
from sunpy.coordinates import get_horizons_coord
from sunpy.map import Map

from gcs.geometry import gcs_mesh_sunpy, apex_radius
from gcs.utils.helioviewer import get_helioviewer_client
from gcs.utils.widgets import SliderAndTextbox

matplotlib.use('Qt5Agg')

hv = get_helioviewer_client()

straight_vertices, front_vertices, circle_vertices = 10, 10, 20
filename = 'gcs_params.json'
draw_modes = ['off', 'point cloud', 'grid']

# disable sunpy warnings
log.setLevel('ERROR')


def running_difference(a, b):
    return Map(b.data * 1.0 - a.data * 1.0, b.meta)


def load_image(spacecraft: str, detector: str, date: dt.datetime, runndiff: bool):
    if spacecraft == 'STA':
        observatory = 'STEREO_A'
        instrument = 'SECCHI'
        if detector not in ['COR1', 'COR2']:
            raise ValueError(f'unknown detector {detector} for spacecraft {spacecraft}.')
    elif spacecraft == 'STB':
        observatory = 'STEREO_B'
        instrument = 'SECCHI'
        if detector not in ['COR1', 'COR2']:
            raise ValueError(f'unknown detector {detector} for spacecraft {spacecraft}.')
    elif spacecraft == 'SOHO':
        observatory = 'SOHO'
        instrument = 'LASCO'
        if detector not in ['C2', 'C3']:
            raise ValueError(f'unknown detector {detector} for spacecraft {spacecraft}.')
    else:
        raise ValueError(f'unknown spacecraft: {spacecraft}')

    f = download_helioviewer(date, observatory, instrument, detector)

    if runndiff:
        f2 = download_helioviewer(date - dt.timedelta(hours=1), observatory, instrument, detector)
        return running_difference(f2, f)
    else:
        return f


def download_helioviewer(date, observatory, instrument, detector):
    file = hv.download_jp2(date, observatory=observatory, instrument=instrument, detector=detector)
    f = Map(file)

    if observatory == 'SOHO':
       # add observer location information:
       soho = get_horizons_coord('SOHO', f.date)
       f.meta['HGLN_OBS'] = soho.lon.to('deg').value
       f.meta['HGLT_OBS'] = soho.lat.to('deg').value
       f.meta['DSUN_OBS'] = soho.radius.to('m').value

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


class GCSGui(QtWidgets.QMainWindow):
    def __init__(self, date: dt.datetime, spacecraft: List[str], runndiff: bool = False,
            detector_stereo: str = 'COR2', detector_soho='C2'):
        super().__init__()
        self._spacecraft = spacecraft
        self._date = date
        self._runndiff = runndiff
        self._detector_stereo = detector_stereo
        self._detector_soho = detector_soho

        self._root = QtWidgets.QWidget()
        self.setCentralWidget(self._root)
        self._mainlayout = QtWidgets.QHBoxLayout(self._root)

        self._figure = Figure(figsize=(5 * len(spacecraft), 5))
        canvas = FigureCanvas(self._figure)
        self._mainlayout.addWidget(canvas, stretch=5)
        self.addToolBar(NavigationToolbar(canvas, self))
        self._current_draw_mode = None

        self.create_widgets()

        self.make_plot()
        self.show()

    def create_widgets(self):
        params = load_params()
        self._s_half_angle = SliderAndTextbox('Half angle, \u03B1 [°]', 0, 90, params['half_angle'])
        self._s_height = SliderAndTextbox('Apex Height, R\u2090\u209A\u2091\u2093 [Rs]', 0, 24, params['height'])
        self._s_kappa = SliderAndTextbox('Aspect Ratio, \u03BA', 0, 1, params['kappa'])
        self._s_lat = SliderAndTextbox('Heliographic Latitude, \u03B8 [°]', -90, 90, params['lat'])
        self._s_lon = SliderAndTextbox('Stonyhurst Longitude, \u03C6 [°]', 0, 360, params['lon'])
        self._s_tilt = SliderAndTextbox('Tilt angle, \u03B3 [°]', -90, 90, params['tilt'])
        sliders = self._s_half_angle, self._s_height, self._s_kappa, self._s_lat, self._s_lon, self._s_tilt

        layout = QtWidgets.QVBoxLayout()
        for slider in sliders:
            layout.addWidget(slider)
            slider.valueChanged.connect(self.plot_mesh)

        # add checkbox to enable or disable plot
        cb_mode_label = QLabel()
        cb_mode_label.setText('Display mode')
        layout.addWidget(cb_mode_label)
        self._cb_mode = QComboBox()
        for mode in draw_modes:
            self._cb_mode.addItem(mode)
        self._cb_mode.setCurrentIndex(2)
        layout.addWidget(self._cb_mode)
        self._cb_mode.currentIndexChanged.connect(self.plot_mesh)

        # add labels for useful quantities
        self._l_radius = QLabel()
        layout.addWidget(self._l_radius)

        b_save = QtWidgets.QPushButton('Save')
        b_save.clicked.connect(self.save)
        layout.addWidget(b_save)
        layout.addStretch(1)

        self._mainlayout.addLayout(layout, stretch=1)

    def make_plot(self):
        fig = self._figure
        spacecraft = self._spacecraft
        date = self._date
        runndiff = self._runndiff
        spec = GridSpec(ncols=len(spacecraft), nrows=1, figure=fig)

        axes = []
        images = []
        self._mesh_plots = []
        for i, sc in enumerate(spacecraft):
            detector = self._detector_stereo if sc in ['STA', 'STB'] else self._detector_soho
            image = load_image(sc, detector, date, runndiff)
            images.append(image)

            ax = fig.add_subplot(spec[:, i], projection=image)
            axes.append(ax)

            image.plot(axes=ax, cmap='Greys_r', norm=colors.Normalize(vmin=-30, vmax=30) if runndiff else None)

            if i == len(spacecraft) - 1:
                # for last plot: move labels to the right
                ax.coords[1].set_ticks_position('r')
                ax.coords[1].set_ticklabel_position('r')
                ax.coords[1].set_axislabel_position('r')
        self._bg = fig.canvas.copy_from_bbox(fig.bbox)
        self._images = images
        self._axes = axes

        self.plot_mesh()

        fig.canvas.draw()
        fig.tight_layout()

    def plot_mesh(self):
        fig = self._figure
        half_angle = np.radians(self._s_half_angle.val)
        height = self._s_height.val
        kappa = self._s_kappa.val
        lat = np.radians(self._s_lat.val)
        lon = np.radians(self._s_lon.val)
        tilt = np.radians(self._s_tilt.val)

        # calculate and show quantities
        ra = apex_radius(half_angle, height, kappa)
        self._l_radius.setText('Apex cross-section radius: {:.2f} Rs'.format(ra))

        # check if plot should be shown
        draw_mode = draw_modes[self._cb_mode.currentIndex()]
        if draw_mode != self._current_draw_mode:
            for plot in self._mesh_plots:
                plot.remove()
            self._mesh_plots = []
            fig.canvas.draw()
            self._current_draw_mode = draw_mode
            if draw_mode == 'off':
                return

        # create GCS mesh
        mesh = gcs_mesh_sunpy(self._date, half_angle, height, straight_vertices, front_vertices, circle_vertices,
                              kappa, lat, lon, tilt)
        if draw_mode == 'grid':
            mesh2 = mesh.reshape((front_vertices + straight_vertices) * 2 - 3, circle_vertices).T.flatten()
            mesh = concatenate([mesh, mesh2])

        for i, (image, ax) in enumerate(zip(self._images, self._axes)):
            if len(self._mesh_plots) <= i:
                # new plot
                style = {
                    'grid': '-',
                    'point cloud': '.'
                }[draw_mode]
                params = {
                    'grid': dict(lw=0.5),
                    'point cloud': dict(ms=2)
                }[draw_mode]
                p = ax.plot_coord(mesh, style, color='blue', scalex=False, scaley=False, **params)[0]
                self._mesh_plots.append(p)
            else:
                # update plot
                p = self._mesh_plots[i]

                frame0 = mesh.frame.transform_to(image.coordinate_frame)
                xdata = frame0.spherical.lon.to_value(units.deg)
                ydata = frame0.spherical.lat.to_value(units.deg)
                p.set_xdata(xdata)
                p.set_ydata(ydata)
                ax.draw_artist(p)

        fig.canvas.draw()

    def get_params_dict(self):
        return {
            'half_angle': self._s_half_angle.val,
            'height': self._s_height.val,
            'kappa': self._s_kappa.val,
            'lat': self._s_lat.val,
            'lon': self._s_lon.val,
            'tilt': self._s_tilt.val
        }

    def save(self):
        save_params(self.get_params_dict())
        self.close()


def main():
    parser = argparse.ArgumentParser(description='Run the GCS GUI', prog='gcs_gui')
    parser.add_argument('date', type=lambda d: dt.datetime.strptime(d, '%Y-%m-%d %H:%M'),
                        help='Date and time for the coronagraph images. Format: "yyyy-mm-dd HH:MM" (with quotes). '
                             'The closest available image will be loaded for each spacecraft.')
    parser.add_argument('spacecraft', type=str, nargs='+', choices=['STA', 'STB', 'SOHO'],
                        help='List of spacecraft to use.')
    parser.add_argument('-rd', '--running-difference', action='store_true',
                        help='Whether to use running difference images')
    parser.add_argument('-soho', type=str, default='C2', choices=['C2', 'C3'],
                        help='Which coronagraph to use at SOHO/LASCO.')
    parser.add_argument('-stereo', type=str, default='COR2', choices=['COR1', 'COR2'],
                        help='Which coronagraph to use at STEREO.')
    args = parser.parse_args()
    qapp = QtWidgets.QApplication(sys.argv)
    app = GCSGui(args.date, args.spacecraft, args.running_difference, detector_stereo=args.stereo,
                 detector_soho=args.soho)
    app.show()
    qapp.exec_()


if __name__ == '__main__':
    main()

