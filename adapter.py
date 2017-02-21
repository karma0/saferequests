import datetime

from requests.adapters import HTTPAdapter, DEFAULT_POOLSIZE, \
                                DEFAULT_RETRIES, DEFAULT_POOLBLOCK
import requests
import grequests

from throttle import BurstThrottle

DEFAULT_BURST_WINDOW = datetime.timedelta(seconds=5)
DEFAULT_WAIT_WINDOW = datetime.timedelta(seconds=15)
CONCURRENT_LIMIT = 3


class MyHttpAdapter(HTTPAdapter):
    throttle = None

    def __init__(self, pool_connections=DEFAULT_POOLSIZE,
                 pool_maxsize=DEFAULT_POOLSIZE, max_retries=DEFAULT_RETRIES,
                 pool_block=DEFAULT_POOLBLOCK, burst_window=DEFAULT_BURST_WINDOW,
                 wait_window=DEFAULT_WAIT_WINDOW):
        self.throttle = BurstThrottle(pool_maxsize, burst_window, wait_window)
        super(MyHttpAdapter, self).__init__(
                pool_connections=pool_connections, pool_maxsize=pool_maxsize,
                max_retries=max_retries, pool_block=pool_block)

    def send(self, request, stream=False, timeout=None, verify=True,
            cert=None, proxies=None):
        request_successful = False
        response = None
        while not request_successful:
            wait_time = self.throttle.throttle()
            while wait_time > datetime.timedelta(0):
                gevent.sleep(wait_time.total_seconds(), ref=True)
                wait_time = self.throttle.throttle()

            response = super(MyHttpAdapter, self).send(
                            request, stream=stream, timeout=timeout,
                            verify=verify, cert=cert, proxies=proxies)

            if response.status_code != 429:
                request_successful = True

        return response


if __name__ == "__main__":
    urls = [
        'http://www.petsmart.com/bird/food-and-care/food/#page_name=global&link_section=menu&link_name=bird_food',
        'http://www.petsmart.com/reptile/food-and-care/health-and-wellness/#page_name=global&link_section=menu&link_name=reptile_health_wellness',
        'http://docs.python-requests.org/en/master/_modules/requests/adapters/'
    ]

    def handle_response(*args, **kwargs):
        #print(data[:100])
        print(args)
        print(kwargs)

    print("Creating adapter")

    requests_adapter = adapter.MyHttpAdapter(
        pool_connections=CONCURRENT_LIMIT,
        pool_maxsize=CONCURRENT_LIMIT,
        max_retries=0,
        pool_block=False,
        burst_window=datetime.timedelta(seconds=5),
        wait_window=datetime.timedelta(seconds=20))

    print("Creating session")
    requests_session = requests.session()

    print("Mounting adapters")
    requests_session.mount('http://', requests_adapter)
    requests_session.mount('https://', requests_adapter)

    print("Setting up unsent requests")
    unsent_requests = (grequests.get(url,
                                 hooks={'response': handle_response},
                                 session=requests_session) for url in urls)

    print("Mapping unsent requests to pool")
    grequests.map(unsent_requests, size=CONCURRENT_LIMIT)

    print("Done.")
