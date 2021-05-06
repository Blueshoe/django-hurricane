import asyncio
import logging

import tornado.web


class K8sServerMetricsHandler(tornado.web.RequestHandler):
    """This handler reports current usage statistics to Kubernetes"""

    logger = logging.getLogger()

    def get(self):
        # write custom metrics to MetricsAPI in the future
        request_queue_length = len(asyncio.all_tasks())
        self.logger.info(f"Request count: {request_queue_length}")
        self.write(f"{request_queue_length}".encode())
