from sunpy.net.helioviewer import HelioviewerClient


def get_helioviewer_client():
    hv = HelioviewerClient()
    if not _is_online(hv):
        # fall back to mirror server
        print("https://www.helioviewer.org/ seems to be offline,"
              "switching to mirror at https://helioviewer.ias.u-psud.fr/")
        hv = HelioviewerClient("https://helioviewer-api.ias.u-psud.fr/")
    return hv


def _is_online(hv: HelioviewerClient):
    try:
        return hv.is_online()
    except:
        return False