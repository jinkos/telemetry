from collections import namedtuple

import parse

GPSData = namedtuple("GPSData",
                     [
                         "description",
                         "timestamp",
                         "precision",
                         "fix",
                         "latitude",
                         "longitude",
                         "altitude",
                         "speed_2d",
                         "speed_3d",
                         "units",
                         "npoints"
                     ])


def extract_gps_blocks(stream):
    """ Extract GPS data blocks from binary stream
    This is a generator on lists `KVLItem` objects. In
    the GPMF stream, GPS data comes into blocks of several
    different data items. For each of these blocks we return a list.
    Parameters
    ----------
    stream: bytes
        The raw GPMF binary stream
    Returns
    -------
    gps_items_generator: generator
        Generator of lists of `KVLItem` objects
    """
    for s in parse.filter_klv(stream, "STRM"):
        content = []
        is_gps = False
        for elt in s.value:
            content.append(elt)
            if elt.key == "GPS5":
                is_gps = True
        if is_gps:
            yield content


def parse_gps_block(gps_block):
    """Turn GPS data blocks into `GPSData` objects
    Parameters
    ----------
    gps_block: list of KVLItem
        A list of KVLItem corresponding to a GPS data block.
    Returns
    -------
    gps_data: GPSData
        A GPSData object holding the GPS information of a block.
    """
    block_dict = {
        s.key: s for s in gps_block
    }

    gps_data = block_dict["GPS5"].value * 1.0 / block_dict["SCAL"].value

    latitude, longitude, altitude, speed_2d, speed_3d = gps_data.T

    return GPSData(
        description=block_dict["STNM"].value,
        timestamp=block_dict["GPSU"].value,
        precision=block_dict["GPSP"].value / 100.,
        fix=block_dict["GPSF"].value,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        speed_2d=speed_2d,
        speed_3d=speed_3d,
        units=block_dict["UNIT"].value,
        npoints=len(gps_data)
    )

GYROData = namedtuple("GYROData",
                     [
                         "description",
                         "gy_z",
                         "gy_x",
                         "gy_y",
                         "cumulative_points",
                         "npoints"
                     ])

def parse_gyro_block(gyro_block):
    """Turn GPS data blocks into `GPSData` objects
    Parameters
    ----------
    gps_block: list of KVLItem
        A list of KVLItem corresponding to a GPS data block.
    Returns
    -------
    gps_data: GPSData
        A GPSData object holding the GPS information of a block.
    """
    block_dict = {
        s.key: s for s in gyro_block
    }

    gyro_data = block_dict["GYRO"].value * 1.0 / block_dict["SCAL"].value

    gy_z, gy_x, gy_y = gyro_data.T

    return GYROData(
        description=block_dict["STNM"].value,
        gy_z=gy_z,
        gy_x=gy_x,
        gy_y=gy_y,
        cumulative_points=block_dict["TSMP"].value,
        npoints = len(gyro_data)
    )


ACCLData = namedtuple("ACCLData",
                     [
                         "description",
                         "acc_z",
                         "acc_x",
                         "acc_y",
                         "cumulative_points",
                         "npoints"
                     ])

def parse_accl_block(accl_block):
    """Turn GPS data blocks into `GPSData` objects
    Parameters
    ----------
    gps_block: list of KVLItem
        A list of KVLItem corresponding to a GPS data block.
    Returns
    -------
    gps_data: GPSData
        A GPSData object holding the GPS information of a block.
    """
    block_dict = {
        s.key: s for s in accl_block
    }

    accl_data = block_dict["ACCL"].value * 1.0 / block_dict["SCAL"].value

    acc_z, acc_x, acc_y = accl_data.T

    return ACCLData(
        description=block_dict["STNM"].value,
        acc_z=acc_z,
        acc_x=acc_x,
        acc_y=acc_y,
        cumulative_points=block_dict["TSMP"].value,
        npoints = len(accl_data)
    )

