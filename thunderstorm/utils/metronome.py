import time
import binascii


class Metronome(object):
    """
    """

    def __init__(self, tick_time, beat_times_every_day):
        """
        tick_time: int (minutes) trigger every n minutes
        beat_times_every_day: int  the func should run n times every day
        """
        self.fetch_times_factor = int(24 * 60 * 60 / beat_times_every_day / (tick_time * 60))
        self.now_remainder = int(time.time() / (tick_time * 60)) % self.fetch_times_factor

    def beat_it(self, uuid):
        crc = binascii.crc32(uuid.bytes)
        obj_remainder = crc % self.fetch_times_factor
        if self.now_remainder == obj_remainder:
            return True
        return False
