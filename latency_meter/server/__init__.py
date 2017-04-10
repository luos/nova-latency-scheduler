import BaseHTTPServer
import SimpleHTTPServer
import SocketServer
import threading
from BaseHTTPServer import BaseHTTPRequestHandler
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingTCPServer, TCPServer


class MeasurementHandler():
    data = {}

    def record_measurement(self, measurement):
        """

        :type measurement: Measurement
        """
        self.data[measurement.from_host] = {
            measurement.to_host: measurement.average_latency
        }

    def get_measurements_from_host(self, host):
        return self.data[host]


class Measurement():
    def __init__(self, from_host, to_host, average_latency):
        self.average_latency = average_latency
        self.to_host = to_host
        self.from_host = from_host


class MeasurementRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        print("blah")

    def handle_one_request(self):
        print("handing request")
        BaseHTTPRequestHandler.handle_one_request(self)

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("hello world")
        print(self.raw_requestline)
        print(self.request)
        self.wfile.close()


class Httpserver(TCPServer):
    allow_reuse_address = 1

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True, logger=None):
        TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.logger = logger
        logger.debug("GLLS Inicialized server")


def start_server(port=9913, logger=None):
    http_handler = MeasurementRequestHandler
    server = Httpserver(('0.0.0.0', port), http_handler, logger=logger)
    logger.debug("Listening on " + str(port))
    try:
        server.serve_forever()
    except KeyboardInterrupt as e:
        logger.debug("GLLS Shutting down")
        logger.debug("GLLS " + e.message)
        server.server_close()
        server.shutdown()


def start_server_on_other_thread(logger):
    logger.debug("GLLS Server started")
    thread = threading.Thread(target=lambda: start_server(logger=logger))
    thread.start()


class MockLogger():
    def debug(self, string):
        print(string)
