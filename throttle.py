import datetime


class BurstThrottle(object):
    max_hits = None
    hits = None
    burst_window = None
    total_window = None
    timestamp = None

    def __init__(self, max_hits, burst_window, wait_window):
        self.max_hits = max_hits
        self.hits = 0
        self.burst_window = burst_window
        self.total_window = burst_window + wait_window
        self.timestamp = datetime.datetime.min

    def throttle(self):
        now = datetime.datetime.utcnow()
        if now < self.timestamp + self.total_window:
            if (now < self.timestamp + self.burst_window) and (self.hits < self.max_hits):
                self.hits += 1
                return datetime.timedelta(0)
            else:
                return self.timestamp + self.total_window - now
        else:
            self.timestamp = now
            self.hits = 1
            return datetime.timedelta(0)
