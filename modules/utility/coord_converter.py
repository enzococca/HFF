"""Coordinate parsing + conversion (DDM / DMS / DD / UTM).

Pure functions, no GUI. Used by the QGIS plugin's CoordConverterDialog
(gui/coord_converter_dialog.py) and mirrored by the Telegram bot's
/coords handler.

Input formats accepted by parse_coordinate:
  DDM: "N 34 01.825" or "34°01.825'N"
  DMS: "34 1 49.5 N" or "34°1'49.5\"N"
  DD : "34.030417" or "34.030417 N"

UTM uses pyproj when available (same engine as QGIS); otherwise falls
back to pure-Python WGS84 formulas (Karney/USGS Bulletin 1532, ~mm
precision within ~30° of the zone's central meridian).
"""
from __future__ import annotations

import math
import re

try:
    from pyproj import Transformer
    HAS_PYPROJ = True
except ImportError:
    HAS_PYPROJ = False


# ---------------------------------------------------------------------------
# UTM
# ---------------------------------------------------------------------------

def utm_zone_from_lon(lon: float) -> int:
    """Standard UTM zone (1-60) for a given longitude."""
    return int((lon + 180) / 6) + 1


def _utm_pure_python(lat: float, lon: float, zone: int, northern: bool):
    """WGS84 → UTM without external deps. Karney/USGS series."""
    a = 6378137.0
    f = 1 / 298.257223563
    k0 = 0.9996

    e2 = f * (2 - f)
    e_p2 = e2 / (1 - e2)

    lon0 = math.radians((zone - 1) * 6 - 180 + 3)
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    N = a / math.sqrt(1 - e2 * math.sin(lat_rad) ** 2)
    T = math.tan(lat_rad) ** 2
    C = e_p2 * math.cos(lat_rad) ** 2
    A = math.cos(lat_rad) * (lon_rad - lon0)

    M = a * (
        (1 - e2/4 - 3*e2**2/64 - 5*e2**3/256) * lat_rad
        - (3*e2/8 + 3*e2**2/32 + 45*e2**3/1024) * math.sin(2*lat_rad)
        + (15*e2**2/256 + 45*e2**3/1024) * math.sin(4*lat_rad)
        - (35*e2**3/3072) * math.sin(6*lat_rad)
    )

    easting = k0 * N * (
        A
        + (1 - T + C) * A**3 / 6
        + (5 - 18*T + T**2 + 72*C - 58*e_p2) * A**5 / 120
    ) + 500000.0

    northing = k0 * (
        M + N * math.tan(lat_rad) * (
            A**2 / 2
            + (5 - T + 9*C + 4*C**2) * A**4 / 24
            + (61 - 58*T + T**2 + 600*C - 330*e_p2) * A**6 / 720
        )
    )

    if not northern:
        northing += 10000000.0
    return easting, northing


def latlon_to_utm(lat: float, lon: float, zone: int | None = None):
    """(lat, lon) WGS84 → (easting, northing, zone, hemisphere_letter).
    If zone is None, derive from longitude."""
    if zone is None:
        zone = utm_zone_from_lon(lon)
    northern = lat >= 0
    hemi = 'N' if northern else 'S'

    if HAS_PYPROJ:
        epsg = 32600 + zone if northern else 32700 + zone
        transformer = Transformer.from_crs(
            'EPSG:4326', f'EPSG:{epsg}', always_xy=True,
        )
        easting, northing = transformer.transform(lon, lat)
    else:
        easting, northing = _utm_pure_python(lat, lon, zone, northern)
    return easting, northing, zone, hemi


# ---------------------------------------------------------------------------
# Parse + format
# ---------------------------------------------------------------------------

def parse_coordinate(text: str) -> float:
    """Recognize DDM, DMS or DD; return decimal degrees."""
    if not text or not text.strip():
        raise ValueError("Empty string")

    s = text.strip().upper()
    hemisphere = 1
    m = re.search(r'[NSEW]', s)
    if m:
        if m.group() in ('S', 'W'):
            hemisphere = -1
        s = re.sub(r'[NSEW]', '', s).strip()

    numbers = re.findall(r'-?\d+\.?\d*', s)
    if not numbers:
        raise ValueError(f"No numbers found in: {text}")

    nums = [float(n) for n in numbers]

    if len(nums) == 1:
        dd = nums[0]
    elif len(nums) == 2:
        deg, minutes = nums
        dd = abs(deg) + minutes / 60.0
        if deg < 0:
            dd = -dd
    elif len(nums) == 3:
        deg, minutes, seconds = nums
        dd = abs(deg) + minutes / 60.0 + seconds / 3600.0
        if deg < 0:
            dd = -dd
    else:
        raise ValueError(f"Unrecognized format: {text}")

    return dd * hemisphere


def dd_to_ddm(dd: float, is_lat: bool = True) -> str:
    h = ('N' if dd >= 0 else 'S') if is_lat else ('E' if dd >= 0 else 'W')
    a = abs(dd)
    deg = int(a)
    minutes = (a - deg) * 60
    return f"{h} {deg:02d}°{minutes:06.3f}'"


def dd_to_dms(dd: float, is_lat: bool = True) -> str:
    h = ('N' if dd >= 0 else 'S') if is_lat else ('E' if dd >= 0 else 'W')
    a = abs(dd)
    deg = int(a)
    mf = (a - deg) * 60
    m = int(mf)
    s = (mf - m) * 60
    return f"{h} {deg:02d}°{m:02d}'{s:05.2f}\""


# ---------------------------------------------------------------------------
# All-formats helper (used by both QGIS dialog and Telegram bot)
# ---------------------------------------------------------------------------

def convert_all(lat_text: str, lon_text: str, zone: int | None = None) -> dict:
    """Parse two coordinate strings and return every format.
    Raises ValueError on bad input or out-of-range values.

    Result keys: lat_dd, lon_dd, dd, ddm, dms, gis (lon, lat for QGIS),
    utm_zone, utm_hemi, utm_easting, utm_northing, utm_text, epsg,
    epsg_text, gmaps_url, auto_zone (the unforced zone).
    """
    lat_dd = parse_coordinate(lat_text)
    lon_dd = parse_coordinate(lon_text)
    if not -90 <= lat_dd <= 90:
        raise ValueError(f"Latitude out of range (-90/+90): {lat_dd}")
    if not -180 <= lon_dd <= 180:
        raise ValueError(f"Longitude out of range (-180/+180): {lon_dd}")

    auto_zone = utm_zone_from_lon(lon_dd)
    easting, northing, used_zone, hemi = latlon_to_utm(lat_dd, lon_dd, zone)
    epsg = (32600 + used_zone) if hemi == 'N' else (32700 + used_zone)

    return {
        "lat_dd": lat_dd,
        "lon_dd": lon_dd,
        "dd": f"{lat_dd:.6f}, {lon_dd:.6f}",
        "ddm": f"{dd_to_ddm(lat_dd, True)}   {dd_to_ddm(lon_dd, False)}",
        "dms": f"{dd_to_dms(lat_dd, True)}   {dd_to_dms(lon_dd, False)}",
        "gis": f"{lon_dd:.6f}, {lat_dd:.6f}",
        "utm_zone": used_zone,
        "utm_hemi": hemi,
        "utm_easting": easting,
        "utm_northing": northing,
        "utm_text": f"{used_zone}{hemi}  E={easting:.2f}  N={northing:.2f}",
        "epsg": epsg,
        "epsg_text": f"EPSG:{epsg}  ({easting:.0f}, {northing:.0f})",
        "gmaps_url": f"https://maps.google.com/?q={lat_dd:.6f},{lon_dd:.6f}",
        "auto_zone": auto_zone,
    }
