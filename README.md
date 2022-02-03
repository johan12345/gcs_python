GCS in Python
=============
[![DOI](https://zenodo.org/badge/297350666.svg)](https://zenodo.org/badge/latestdoi/297350666)

Python 3 implementation of the Graduated Cylindrical Shell model (GCS, [Thernisien, 2011](https://dx.doi.org/10.1088%2F0067-0049%2F194%2F2%2F33)).
Based on the existing IDL implementation in [SolarSoft](https://www.lmsal.com/solarsoft/)
(`cmecloud.pro`, `shellskeleton.pro`).

The code in `gcs/geometry.py` provides the basic implementation of the GCS geometry, while the Qt-based GUI in
`gcs/gui.py` uses [SunPy](https://sunpy.org/) and Matplotlib to plot the model on top of coronagraph images provided by
[Helioviewer.org](https://www.helioviewer.org/).

A more detailed description of the GCS model, this Python implementation and its validation is given in
[this excerpt](/doc/gcs_implementation_forstner_phd_2021.pdf?raw=true) from
[my PhD thesis](https://nbn-resolving.org/urn:nbn:de:gbv:8:3-2021-00166-5).

![Screenshot](/img/screenshot.png?raw=true)

Note
----

This code is still in a quite early stage. It has been compared with the original IDL/SolarSoft version to verify the results, but only for a few case studies.
Please be careful when using it and compare to IDL when in doubt.

If you find a bug, run into technical problems during the installation, or have suggestions for improvement, please create a
GitHub [issue](https://github.com/johan12345/gcs_python/issues/new). As I have since left the Heliophysics field and am no longer actively using the tool myself, I can't promise timely responses. But it is still preferrable compared to writing me an email in private, as other users can also help you.

If you have fixed a bug or implemented improvements, please feel free to open a [Pull Request](https://github.com/johan12345/gcs_python/compare)!

If you use this code in a publication, please cite it using [the DOI generated by Zenodo](https://zenodo.org/badge/latestdoi/297350666). I would also appreciate it if you <a class="u-email Link--primary " href="mailto:&#x6a;&#x6f;&#x68;&#x61;&#x6e;&#x2e;&#x66;&#x6f;&#x72;&#x73;&#x74;&#x6e;&#x65;&#x72;&#x40;&#x67;&#x6d;&#x61;&#x69;&#x6c;&#x2e;&#x63;&#x6f;&#x6d;">drop me an email</a> and tell me what you used it for :)

How to install and run the GUI
------------------------------
Python 3.7 or later and Git are required for installation.
```
# install GCS
pip3 install git+https://github.com/johan12345/gcs_python.git

# run GCS GUI, providing a date/time and the spacecraft to use
gcs_gui "2020-04-15 06:00" STA SOHO
```

Information on the available command line arguments for the GUI is given when you run the help option:
```shell script
gcs_gui -h
```

How to use the GCS geometry in your own plotting code
-----------------------------------------------------
Simply install GCS (as seen above) and use
```python
import gcs.geometry
```
to import the code from the GCS package. You can find some examples what you can do with it in the files
`sample.py` and `sample_sunpy.py`.

Development setup
-----------------
First, clone the git repository:
```shell script
git@github.com:johan12345/gcs_python.git
```

It is recommended to use a [virtual environment](https://docs.python.org/3/tutorial/venv.html) so that the
Python packages you install as dependencies of GCS don't interfere with your globally installed packages.
On some Linux distributions, the additional `python3-venv` package needs to be installed for this to work.

```shell script
python3 -m venv env
. env/bin/activate
```

Then, install the dependencies:
```shell script
# install requirements
python3 -m pip install --upgrade pip setuptools
pip3 install -r requirements.txt
```

and test the GUI using
```shell script
python -m gcs.gui "2020-04-15 06:00" STA SOHO
```
