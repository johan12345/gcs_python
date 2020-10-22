import numpy as np
from astropy.coordinates import SkyCoord
from numpy import pi, sin, cos, tan, arcsin, sqrt
from numpy.linalg import norm
from scipy.spatial.transform import Rotation
from sunpy.coordinates import frames, sun


def skeleton(alpha, distjunc, straight_vertices, front_vertices, k):
    """
    Compute the axis of the GCS CME model. Based on IDL version shellskeleton.pro
    https://hesperia.gsfc.nasa.gov/ssw/stereo/secchi/idl/scraytrace/shellskeleton.pro

    Parameters
    ----------
    alpha: width of CME (half angle)
    distjunc: CME height (in length units, e.g. solar radii)
    straight_vertices: number of vertices along straight edges
    front_vertices: number of vertices along front
    k: GCS ratio

    Returns
    -------

    """
    # compute entire loop lenght
    loop_length = distjunc * (1. + (alpha +pi / 2) * tan(alpha))
    # copute circular part half length
    circle_length = distjunc * np.tan(alpha) * (2. * alpha +pi) / 2

    gamma = arcsin(k)

    # calculate the points of the straight line part
    pRstart = np.array([0, sin(alpha), cos(alpha)])  # start on the limb
    pLstart = np.array([0, -sin(alpha), cos(alpha)])
    pslR = np.outer(np.linspace(0, distjunc, straight_vertices), np.array([0, sin(alpha), cos(alpha)]))
    pslL = np.outer(np.linspace(0, distjunc, straight_vertices), np.array([0, -sin(alpha), cos(alpha)]))
    rsl = tan(gamma) * norm(pslR, axis=1)
    casl = np.full(straight_vertices, -alpha)

    # calculate the points of the circular part
    beta = np.linspace(-alpha, pi / 2, front_vertices)
    hf = distjunc
    h = hf / cos(alpha)
    rho = hf * tan(alpha)

    X0 = (rho + h * k ** 2 * sin(beta)) / (1 - k ** 2)
    rc = sqrt((h ** 2 * k ** 2 - rho ** 2) / (1 - k ** 2) + X0 ** 2)
    cac = beta

    pcR = np.array([np.zeros(beta.shape), X0 * cos(beta), h + X0 * sin(beta)]).T
    pcL = np.array([np.zeros(beta.shape), -X0 * cos(beta), h + X0 * sin(beta)]).T

    r = np.concatenate((rsl, rc[1:], np.flipud(rc)[1:], np.flipud(rsl)[1:]))
    ca = np.concatenate((casl, cac[1:], pi-np.flipud(cac)[1:], pi-np.flipud(casl)[1:]))
    p = np.concatenate((pslR, pcR[1:], np.flipud(pcL)[1:], np.flipud(pslL)[1:]))

    return p, r, ca


def gcs_mesh(alpha, height, straight_vertices, front_vertices, circle_vertices, k):
    """
    Calculate GCS model mesh. Based on IDL version cmecloud.pro.
    https://hesperia.gsfc.nasa.gov/ssw/stereo/secchi/idl/scraytrace/cmecloud.pro

    Parameters
    ----------
    alpha: width of CME (half angle, in radians)
    height: CME height (in length units, e.g. solar radii)
    straight_vertices: number of vertices along straight edges
    front_vertices: number of vertices along front
    circle_vertices: number of vertices along each circle
    k: GCS ratio

    Returns
    -------
    GCS mesh (in length units, e.g. solar radii) in the following coordinate system (Heliographic Stonyhurst):
    - Z axis: Sun-Earth line projected onto Sun's equatorial plane
    - Y axis: Sun's north pole
    - Origin: center of the Sun

    """
    # calculate position

    # calculate height of skeleton depending on height of leading edge
    distjunc = height *(1-k)*cos(alpha)/(1.+sin(alpha))
    p, r, ca = skeleton(alpha, distjunc, straight_vertices, front_vertices, k)

    theta = np.linspace(0, 2 * pi, circle_vertices)
    pspace = np.arange(0, (front_vertices + straight_vertices) * 2 - 3)
    u, v = np.meshgrid(theta, pspace)
    u, v = u.flatten(), v.flatten()

    mesh = r[v, np.newaxis] * np.array([cos(u), sin(u) * cos(ca[v]), sin(u) * sin(ca[v])]).T + p[v]

    # mesh = np.concatenate([
    #    r * np.array([costheta, sintheta * cos(ca), sintheta * sin(ca)]).T + np.array([x, y, 0])
    #    for (x, y), r, ca in zip(p, r, ca)
    # ])

    return mesh, u, v


def rotate_mesh(mesh, neang):
    """
    Rotates the GCS mesh into the correct orientation

    Parameters
    ----------
    mesh GCS mesh, returned by gcs_mesh
    neang angles: longitude, latitude, and rotation angles (in radians)

    Returns
    -------
    rotated GCS mesh

    """
    return Rotation.from_euler('zyx', [neang[2], neang[1], neang[0]]).apply(mesh)


def gcs_mesh_rotated(alpha, height, straight_vertices, front_vertices, circle_vertices, k, lat, lon, tilt):
    """
    Calculate GCS model mesh and rotate it into the correct orientation.
    Convenience function that combines gcs_mesh and rotate_mesh.

    Parameters
    ----------
    alpha: width of CME (half angle, in radians)
    height: CME height (in length units, e.g. solar radii)
    straight_vertices: number of vertices along straight edges
    front_vertices: number of vertices along front
    circle_vertices: number of vertices along each circle
    k: GCS ratio
    lat: CME latitude in radians
    lon: CME longitude in radians (0 = Earth-directed)
    tilt: CME tilt angle in radians

    Returns
    -------
    rotated GCS mesh
    """
    mesh, u, v = gcs_mesh(alpha, height, straight_vertices, front_vertices, circle_vertices, k)
    mesh = rotate_mesh(mesh, [lon, lat, tilt])
    return mesh, u, v


def gcs_mesh_sunpy(date, alpha, height, straight_vertices, front_vertices, circle_vertices, k, lat, lon, tilt):
    """
    Provides the GCS model mesh in SunPy SkyCoord format. This can be directly plotted using SunPy.

    Parameters
    ----------
    date: date and time of observation (Python datetime instance)
    alpha: width of CME (half angle, in radians)
    height: CME height (in length units, e.g. solar radii)
    straight_vertices: number of vertices along straight edges
    front_vertices: number of vertices along front
    circle_vertices: number of vertices along each circle
    k: GCS ratio
    lat: CME latitude in radians
    lon: CME longitude in radians (0 = Earth-directed)
    tilt: CME tilt angle in radians

    Returns
    -------
    GCS mesh as SunPy SkyCoord
    """
    mesh, u, v = gcs_mesh_rotated(alpha, height, straight_vertices, front_vertices, circle_vertices, k, lat, lon, tilt)
    m = mesh.T[[2, 1, 0], :] * sun.constants.radius
    m[1, :] *= -1
    mesh_coord = SkyCoord(*(m), frame=frames.HeliographicStonyhurst,
                          obstime=date, representation_type='cartesian')
    return mesh_coord


def apex_radius(alpha, height, k):
    """
    Calculates the cross-section radius of the flux rope at the apex, based on GCS parameters alpha, height and kappa.

    Parameters
    ----------
    alpha: width of CME (half angle, in radians)
    height: CME height (in length units, e.g. solar radii)
    k: GCS ratio

    Returns
    -------
    apex radius (in length units, e.g. solar radii)
    """
    h = height * (1 - k) * cos(alpha) / (1. + sin(alpha))
    b = h / cos(alpha)
    rho = h * tan(alpha)
    return k * (b + rho) / (1 - k ** 2)
