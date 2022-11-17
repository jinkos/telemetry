import numpy as np


class NPGPS:

    def __init__(self, timestamp_indexes, timestamp_timestamps, items, timestamp_steps):

        msecs, lat, long, elev = [], [], [], []

        def get_next_block_item_index(block_index, timestamp_indexes):

            if block_index + 1 >= len(timestamp_indexes):
                return 1000000000

            return timestamp_indexes[block_index + 1]

        block_index = 0
        next_block_item_index = get_next_block_item_index(block_index, timestamp_indexes)
        msec = 0
        time_step = timestamp_steps[block_index]
        for i, item in enumerate(items):

            if i == next_block_item_index:
                block_index += 1
                next_block_item_index = get_next_block_item_index(block_index, timestamp_indexes)
                time_step = timestamp_steps[block_index]

            msecs.append(msec)
            lat.append(item.latitude)
            long.append(item.longitude)
            elev.append(item.altitude)
            msec += time_step

        self.np_msecs = np.array(msecs)
        self.np_lat = np.array(lat)
        self.np_long = np.array(long)
        self.np_elev = np.array(elev)

    def log(self):

        for msec, lat, long, elev in zip(self.np_msecs, self.np_lat, self.np_long, self.np_elev):
            print(msec, lat, long, elev)


class NPGYRO:

    def __init__(self, timestamp_indexes, timestamp_timestamps, items, timestamp_steps):

        msecs, gy_z, gy_x, gy_y = [], [], [], []

        def get_next_block_item_index(block_index, timestamp_indexes):

            if block_index + 1 >= len(timestamp_indexes):
                return 1000000000

            return timestamp_indexes[block_index + 1]

        block_index = 0
        next_block_item_index = get_next_block_item_index(block_index, timestamp_indexes)
        msec = 0
        time_step = timestamp_steps[block_index]
        for i, item in enumerate(items):

            if i == next_block_item_index:
                block_index += 1
                next_block_item_index = get_next_block_item_index(block_index, timestamp_indexes)
                time_step = timestamp_steps[block_index]

            msecs.append(msec)
            gy_z.append(item.gy_z)
            gy_x.append(item.gy_x)
            gy_y.append(item.gy_y)
            msec += time_step

        self.np_msecs = np.array(msecs)
        self.np_z = np.array(gy_z)
        self.np_x = np.array(gy_x)
        self.np_y = np.array(gy_y)

    def log(self):

        for msec, z, x, y in zip(self.np_msecs, self.np_z, self.np_x, self.np_y):
            print(msec, z, x, y)


class NPACCL:

    def __init__(self, timestamp_indexes, timestamp_timestamps, items, timestamp_steps):

        msecs, acc_z, acc_x, acc_y = [], [], [], []

        def get_next_block_item_index(block_index, timestamp_indexes):

            if block_index + 1 >= len(timestamp_indexes):
                return 1000000000

            return timestamp_indexes[block_index + 1]

        block_index = 0
        next_block_item_index = get_next_block_item_index(block_index, timestamp_indexes)
        msec = 0
        time_step = timestamp_steps[block_index]
        for i, item in enumerate(items):

            if i == next_block_item_index:
                block_index += 1
                next_block_item_index = get_next_block_item_index(block_index, timestamp_indexes)
                time_step = timestamp_steps[block_index]

            msecs.append(msec)
            acc_z.append(item.acc_z)
            acc_x.append(item.acc_x)
            acc_y.append(item.acc_y)
            msec += time_step

        self.np_msecs = np.array(msecs)
        self.np_z = np.array(acc_z)
        self.np_x = np.array(acc_x)
        self.np_y = np.array(acc_y)

    def log(self):

        for msec, z, x, y in zip(self.np_msecs, self.np_z, self.np_x, self.np_y):
            print(msec, z, x, y)