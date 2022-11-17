import datetime
import os
import re
from typing import Dict, List

from JE_ffprobe import JE_FFProbe

def extract_gps_locations_from_video(video_path: str) -> List[Dict]:
    """
    Extracts the imu data from the video into a list of GPS locations
    :param video_path: (String) path to the video
    :return: (List[Dict]) of gps locations, example [{"latitude": 1, "longitude": 2, "timestamp": 0}].
    """

    probe = JE_FFProbe(video_path)
    byte_data = probe.extract_bin_stream("text")

    list_of_locations = _extract_gps_locations_from_byte_data(byte_data)

    # assuming the first location in the gps data is the start of the video
    video_start_timestamp = list_of_locations[0]["timestamp"]
    for location in list_of_locations:
        location["timestamp"] = location["timestamp"] - video_start_timestamp

    return list_of_locations, video_start_timestamp


def _convert_gps_to_decimal_degree(value, code):
    """
    Converts the GPRMC style gps coordinate to decimal degrees
    :param value: (String) GPRMC gps coordinate
    :param code: (String) Compass direction of coordinate (N, E, S, W)
    :return: (Float) decimal degree value of float
    """

    val_deg = float(value.split(".")[0][:-2])
    val_min = float(value.split(".")[0][-2:])  # two digits to left of decimal point
    val_sec = float(value.split(".")[1]) / 10 ** len(value.split(".")[1])

    if code in ["S", "W"]:
        sign = -1
    else:
        sign = 1

    coord_dd = (val_deg + val_min / 60 + val_sec / 60) * sign

    return coord_dd


def _get_gprmc_data(gprmc_bytes):
    """
    Extracts the GPRMC data from the bytes
    :param gprmc_bytes: (Bytes) of data
    :return: datetimestamp (datetime), float) latitude, (float) longitude, (String) speed, (String) degree
    """
    (
        utc,
        status,
        latitude,
        latitude_code,
        longitude,
        longitude_code,
        speed,
        degree,
        date,
        variation,
        code,
        checksum,
    ) = (
        str(gprmc_bytes).split("GPRMC,")[1].split(",")
    )
    datetimestamp = datetime.datetime.strptime(
        date + utc, "%d%m%y%H%M%S.%f"
    ).timestamp()
    latitude = _convert_gps_to_decimal_degree(latitude, latitude_code)
    longitude = _convert_gps_to_decimal_degree(longitude, longitude_code)
    return {
        "timestamp": datetimestamp,
        "latitude": latitude,
        "longitude": longitude,
        "bearing": _try_float(degree),
    }


def _check_imu_gps_data_in_binary(binary_file_path):
    """
    Validates if a binary file includes imu gps data
    :param binary_file_path: (String) path to binary file
    :return: (boolean) True if data found in the right format, False elsewise
    """
    # order is 480 bytes of imu (20x2x12bytes) followed by 128 bytes of gprmc and 128 bytes of gpgga
    with open(binary_file_path, "rb") as f:
        s = f.read()
    gprmc_index = s.find(b"$GPRMC")

    if gprmc_index < 480:
        return False

    return True


def _try_float(v):
    try:
        return float(v)
    except Exception:
        return None


def _extract_gps_locations_from_byte_data(byte_data):
    """
    Extracts IMU and GPS data from binary file
    :param file_path: (String) path to binary file
    :return: (List[Dict]) list of dicts, each dict is represent a gps location example [{"timestamp": 111, "latitude": 15.3,"longitude": 1.2,"bearing": .9}]
    """
    # order is 480 bytes of imu (20x2x12bytes) followed by 128 bytes of gprmc and 128 bytes of gpgga

    indices_of_GPRMC_bytes = [m.start() for m in re.finditer(b"\$GPRMC", byte_data)]
    gprmc_lines = [byte_data[index : index + 128] for index in indices_of_GPRMC_bytes]

    print(str(gprmc_lines[0]))

    gprmc_extracted_data = [_get_gprmc_data(gprmc_line) for gprmc_line in gprmc_lines]

    return gprmc_extracted_data
