import logging

from locust import HttpUser, between, events, task
from locust.contrib.fasthttp import FastHttpUser


class HurricaneWebsiteUser(FastHttpUser):
    wait_time = between(5, 15)
    url = "/"
    weight = 1

    @task
    def request(self):
        self.client.get(self.url)


class MediumHurricaneWebsiteUser(HurricaneWebsiteUser):
    url = "/medium"
    weight = 3


class HeavyHurricaneWebsiteUser(HurricaneWebsiteUser):
    url = "/heavy"
    weight = 1


@events.quitting.add_listener
def _(environment, **kw):
    logging.info(f"Average response time: {environment.stats.total.avg_response_time}")
    logging.info(f"95th percentile response time: {environment.stats.total.get_response_time_percentile(0.95)}")
    if environment.stats.total.fail_ratio > 0.025:
        logging.error("Test failed due to failure ratio > 2.5%")
        environment.process_exit_code = 1
    elif environment.stats.total.avg_response_time > 300:
        logging.error("Test failed due to average response time ratio > 300 ms")
        environment.process_exit_code = 1
    elif environment.stats.total.get_response_time_percentile(0.95) > 900:
        logging.error("Test failed due to 95th percentile response time > 900 ms")
        environment.process_exit_code = 1
    else:
        environment.process_exit_code = 0
