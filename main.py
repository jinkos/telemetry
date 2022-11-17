from gps_data_extractor import extract_gps_locations_from_video
import ffmpeg
import cProfile
import struct
import numpy as np
from collections import namedtuple
import datetime

from JE_ffprobe import JE_FFProbe
import parse
import gps
from np_telem import NPGPS, NPACCL, NPGYRO

should_profile = False

def find_gpmf_stream(fname):
    """ Find the reference to the GPMF Stream in the video file
    Parameters
    ----------
    fname: str
        The input file
    Returns
    -------
    stream_info: dict
        The GPMF Stream info.
    Raises
    ------
    RuntimeError: If no stream found.
    """
    probe = ffmpeg.probe(fname)

    for s in probe["streams"]:
        if s["codec_tag_string"] == "gpmd":
            return s

    raise RuntimeError("Could not find GPS stream")

def extract_gpmf_stream(fname, verbose=False):
    """Extract GPMF binary data from video files
    Parameters
    ----------
    fname: str
        The input file
    verbose: bool, optional (default=False)
        If True, display ffmpeg messages.
    Returns
    -------
    gpmf_data: bytes
        The raw GPMF binary stream
    """
    stream_info = find_gpmf_stream(fname)
    stream_index = stream_info["index"]
    return ffmpeg.input(fname)\
        .output("pipe:", format="rawvideo", map="0:%i" % stream_index, codec="copy")\
        .run(capture_stdout=True, capture_stderr=not verbose)[0]



def run():

    probe = JE_FFProbe("data/family_crossing.MP4")
    probe.log()

    probe = JE_FFProbe("data/hermionie.MP4")
    probe.log()

    probe = JE_FFProbe("data/aisin_straight.mp4")
    probe.log()

def run_nextbase():
    gps_list, video_start_timestamp = extract_gps_locations_from_video("data/family_crossing.MP4")
    print(gps_list[:2])
    print("Done!")

def ceil4(x):
    """ Find the closest greater or equal multiple of 4
    Parameters
    ----------
    x: int
        The size
    Returns
    -------
    x_ceil: int
        The closest greater integer which is a multiple of 4.
    """
    return (((x - 1) >> 2) + 1) << 2

num_types = {
    "d": ("float64", "d"),
    "f": ("float32", "f"),
    "b": ("int8", "b"),
    "B": ("uint8", "B"),
    "s": ("int16", "h"),
    "S": ("uint16", "H"),
    "l": ("int32", "i"),
    "L": ("uint32", "I"),
    "j": ("int64", "q"),
    "J": ("uint64", "Q")
}

def get_DEVC_list(x, suffix=""):

    DEVC_list = []

    start = 0
    while start < len(x):
        head = struct.unpack(">cccccBH", x[start: start + 8])
        fourcc = (b"".join(head[:4])).decode()
        type_str, size, repeat = head[4:]
        type_str = type_str.decode()
        start += 8
        payload_size = ceil4(size * repeat)
        raw_payload = x[start: start + payload_size]
        DEVC_list.append(raw_payload)
        start += payload_size
        print(suffix, fourcc, type_str, payload_size)

    return DEVC_list

def parse_DEVC(x):

    STRM_list = []

    start = 0
    while start < len(x):
        head = struct.unpack(">cccccBH", x[start: start + 8])
        fourcc = (b"".join(head[:4])).decode()
        type_str, size, repeat = head[4:]
        type_str = type_str.decode()
        start += 8
        payload_size = ceil4(size * repeat)
        raw_payload = x[start: start + payload_size]
        if fourcc == "STRM":
            STRM_list.append(raw_payload)
        start += payload_size

        if type_str == 'c':
            print(raw_payload.decode("latin1"))
        else:
            print(fourcc, type_str, payload_size)

    return STRM_list

def parse_STRM(x):

    start = 0
    while start < len(x):
        head = struct.unpack(">cccccBH", x[start: start + 8])
        fourcc = (b"".join(head[:4])).decode()
        type_str, size, repeat = head[4:]
        type_str = type_str.decode()
        start += 8
        payload_size = ceil4(size * repeat)
        raw_payload = x[start: start + payload_size]
        # if fourcc == "STRM":
        #     STRM_list.append(raw_payload)
        start += payload_size

        if type_str == 'c':
            print(raw_payload.decode("latin1"))
        else:
            print(fourcc, type_str, payload_size)


def get_blocks_from_stream(stream):

    accl_blocks = []
    gyro_blocks = []
    gps_blocks = []

    for s in parse.filter_klv(stream, "STRM"):
        content = []
        block_type = None
        for elt in s.value:
            content.append(elt)
            if elt.key == "GPS5":
                block_type = "GPS5"
            if elt.key == "GPS5":
                block_type = "GPS5"
            if elt.key == "ACCL":
                block_type = "ACCL"
            if elt.key == "GYRO":
                block_type = "GYRO"
        if block_type == "GPS5":
            gps_blocks.append(content)
        if block_type == "ACCL":
            accl_blocks.append(content)
        if block_type == "GYRO":
            gyro_blocks.append(content)

    return accl_blocks, gyro_blocks, gps_blocks

GPSItem = namedtuple("GPSItem",
                     [
                         "latitude",
                         "longitude",
                         "altitude",
                         "speed_2d",
                         "speed_3d",
                     ])

def get_gps_list_from_blocks(gps_blocks):

    timestamp_indexes = []
    timestamp_timestamps = []
    items = []

    index = 0
    for block in gps_blocks:
        # for kvl_item in block:
        #     if kvl_item.key == "GPSU":
        #         timestamp = kvl_item.value
        #     if kvl_item.key == "GPS5":
        #         data = kvl_item.value

        parsed_block = gps.parse_gps_block(block)
        timestamp_indexes.append(index)
        timestamp_timestamps.append(parsed_block.timestamp)
        for i in range(parsed_block.npoints):
            item = GPSItem(parsed_block.latitude[i], parsed_block.longitude[i], parsed_block.altitude[i], parsed_block.speed_2d[i], parsed_block.speed_3d[i])
            items.append(item)
        index += parsed_block.npoints

    print(timestamp_indexes)
    print(timestamp_timestamps)
    print(items[0])
    print(items[-1])

    return timestamp_indexes, timestamp_timestamps, items

GYROItem = namedtuple("GYROItem",
                     [
                         "gy_z",
                         "gy_x",
                         "gy_y",
                     ])

def get_gyro_list_from_blocks(timestamp_timestamps, gyro_blocks):

    timestamp_indexes = []
    items = []

    index = 0
    for block in gyro_blocks:

        parsed_block = gps.parse_gyro_block(block)
        timestamp_indexes.append(index)
        for i in range(parsed_block.npoints):
            item = GYROItem(parsed_block.gy_z[i], parsed_block.gy_x[i], parsed_block.gy_y[i])
            items.append(item)
        index += parsed_block.npoints

    print(timestamp_indexes)
    print(timestamp_timestamps)
    print(items[0])
    print(items[-1])

    return timestamp_indexes, timestamp_timestamps, items

ACCLItem = namedtuple("ACCLItem",
                     [
                         "acc_z",
                         "acc_x",
                         "acc_y",
                     ])

def get_accl_list_from_blocks(timestamp_timestamps, accl_blocks):

    timestamp_indexes = []
    items = []

    index = 0
    for block in accl_blocks:

        parsed_block = gps.parse_accl_block(block)
        timestamp_indexes.append(index)
        for i in range(parsed_block.npoints):
            item = ACCLItem(parsed_block.acc_z[i], parsed_block.acc_x[i], parsed_block.acc_y[i])
            items.append(item)
        index += parsed_block.npoints

    print(timestamp_indexes)
    print(timestamp_timestamps)
    print(items[0])
    print(items[-1])

    return timestamp_indexes, timestamp_timestamps, items

def calc_timestamp_steps(timestamp_indexes, timestamp_timestamps, items):

    timestamp_steps = []
    last_i = None
    last_t = None
    for i, t in zip(timestamp_indexes, timestamp_timestamps):
        t = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f").timestamp()
        if last_i is not None:
            timestamp_steps.append((t - last_t) / (i - last_i))
        else:
            first_t = t
        last_i, last_t = i, t
    timestamp_steps.append(np.median(timestamp_steps))

    return timestamp_steps

def run_gopro_gps():

    probe = JE_FFProbe("data/hermionie.MP4")
    probe.log()
    stream = probe.extract_bin_stream("gpmd")

    accl_blocks, gyro_blocks, gps_blocks = get_blocks_from_stream(stream)

    timestamp_indexes, timestamp_timestamps, items = get_gps_list_from_blocks(gps_blocks)
    timestamp_steps = calc_timestamp_steps(timestamp_indexes, timestamp_timestamps, items)
    np_gps = NPGPS(timestamp_indexes, timestamp_timestamps, items, timestamp_steps)
    np_gps.log()

    timestamp_indexes, timestamp_timestamps, items = get_gyro_list_from_blocks(timestamp_timestamps, gyro_blocks)
    timestamp_steps = calc_timestamp_steps(timestamp_indexes, timestamp_timestamps, items)
    np_gyro = NPGYRO(timestamp_indexes, timestamp_timestamps, items, timestamp_steps)
    np_gyro.log()

    timestamp_indexes, timestamp_timestamps, items = get_accl_list_from_blocks(timestamp_timestamps, accl_blocks)
    timestamp_steps = calc_timestamp_steps(timestamp_indexes, timestamp_timestamps, items)
    np_accl = NPACCL(timestamp_indexes, timestamp_timestamps, items, timestamp_steps)
    np_accl.log()

    return


    DEVC_list = get_DEVC_list(stream)
    print(len(DEVC_list))
    print("=======")
    STRM_list = parse_DEVC(DEVC_list[0])
    for strm in STRM_list:
        print("=======")
        parse_STRM(strm)

    print("Done!")


if __name__ == "__main__":

    if should_profile:
        cProfile.run("run()")
    else:
        run_gopro_gps()

