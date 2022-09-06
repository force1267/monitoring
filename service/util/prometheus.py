import prometheus_client
from prometheus_async.aio import count_exceptions as aio_count_exceptions, time as aio_time, \
    track_inprogress as aio_track_inprogress
from prometheus_client import push_to_gateway, Histogram, Counter, Gauge

from util import config as prom_config


class Prometheus:
    inprogress_tracker = Gauge
    counter_tracker = Counter
    duration_tracker = Histogram

    def __init__(self, mode, pull_host, pull_port, push_gateway_host):
        self.mode = mode
        self.pull_host = pull_host
        self.pull_port = pull_port
        self.push_gateway_host = push_gateway_host
        self.trackers = {}

    def push_metrics(self, job, registry):
        if self.mode == 'PUSH':
            push_to_gateway(self.push_gateway_host, job=job, registry=registry)

    def start_exporter(self):
        if self.mode == 'PULL':
            prometheus_client.start_http_server(port=self.pull_port, addr=self.pull_host)

    def get_tracker(self, key, tracker_type):
        tracker = self.trackers.get(key)
        if not tracker:
            tracker = tracker_type(key, key)
            self.trackers[key] = tracker
        return tracker

    def get_duration_tracker(self, key):
        key = '{key}_duration'.format(key=key)
        return self.get_tracker(key=key, tracker_type=Prometheus.duration_tracker)

    def get_inprogress_tracker(self, key):
        key = '{key}_inprogress'.format(key=key)
        return self.get_tracker(key=key, tracker_type=Prometheus.inprogress_tracker)

    def get_exceptions_tracker(self, key):
        key = '{key}_exceptions'.format(key=key)
        return self.get_tracker(key=key, tracker_type=Prometheus.counter_tracker)

    def get_counter_tracker(self, key):
        key = '{key}_count'.format(key=key)
        return self.get_tracker(key=key, tracker_type=Prometheus.counter_tracker)

    def increment_counter(self, key, amount=1):
        self.get_counter_tracker(key=key).inc(amount=amount)

    def increment_exception(self, key, amount=1):
        self.get_exceptions_tracker(key=key).inc(amount=amount)

    def increment_inprogress(self, key, amount=1):
        self.get_inprogress_tracker(key=key).inc(amount=amount)

    def decrement_inprogress(self, key, amount=1):
        self.get_inprogress_tracker(key=key).dec(amount=amount)

    def observe(self, key, amount):
        self.get_duration_tracker(key=key).observe(amount=amount)

    def track_duration(self, key):
        return self.get_duration_tracker(key=key).time()

    def track_inprogress(self, key):
        return self.get_inprogress_tracker(key=key).track_inprogress()

    def track_exceptions(self, key, exception=BaseException):
        return self.get_exceptions_tracker(key=key).count_exceptions(exception=exception)

    def async_track_duration(self, key, future=None):
        return aio_time(metric=self.get_duration_tracker(key=key), future=future)

    def async_track_inprogress(self, key, future=None):
        return aio_track_inprogress(metric=self.get_inprogress_tracker(key=key), future=future)

    def async_track_exceptions(self, key, future=None, exception=BaseException):
        return aio_count_exceptions(metric=self.get_exceptions_tracker(key=key), future=future, exc=exception)


prometheus = Prometheus(
    mode=prom_config.MODE,
    pull_host=prom_config.HOST,
    pull_port=prom_config.PORT,
    push_gateway_host=prom_config.METRICS_PUSH_GATEWAY_ADDRESS
)
