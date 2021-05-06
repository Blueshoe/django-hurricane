import logging

import tornado.ioloop

from hurricane.testing.actors import K8sServer

if __name__ == "__main__":
    logging.info("Started K8s server")
    app = K8sServer().make_http_receiver_app()
    app.listen(8072)
    tornado.ioloop.IOLoop.current().start()
