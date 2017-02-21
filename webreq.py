import datetime

import requests
import grequests

from adapter import MyHttpAdapter


class WebRequest:

    def __init__(self, urls, concurrent_limit=3):
        self.concurrent_limit = concurrent_limit

        requests_adapter = MyHttpAdapter(
            pool_connections=self.concurrent_limit,
            pool_maxsize=self.concurrent_limit,
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
        self.unsent_requests = (grequests.get(url,
                                 hooks={'response': self.handle_response},
                                 session=requests_session) for url in urls)

    def map(self):
        print("Mapping unsent requests to pool")
        grequests.map(self.unsent_requests, size=self.concurrent_limit)

    def handle_response(self, *args, **kwargs):
        #print(data[:100])
        print(args)
        print(kwargs)


if __name__ == "__main__":
    urls = [
        'http://www.petsmart.com/bird/food-and-care/food/#page_name=global&link_section=menu&link_name=bird_food',
        'http://www.petsmart.com/reptile/food-and-care/health-and-wellness/#page_name=global&link_section=menu&link_name=reptile_health_wellness',
        'http://docs.python-requests.org/en/master/_modules/requests/adapters/',
        'http://stackoverflow.com/questions/16015749/in-what-way-is-grequests-asynchronous',
        'http://stackoverflow.com/questions/20247354/limiting-throttling-the-rate-of-http-requests-in-grequests',
    ]
    wr = WebRequest(urls)
    wr.map()
    print("Done.")
