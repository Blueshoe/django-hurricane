import re

from hurricane.kubernetes import K8sServerMetricsHandler
from hurricane.testing import HurricanServerTest


class HurricanStartServerTests(HurricanServerTest):

    probe_route = "/probe"
    alive_route = "/alive"
    startup_route = "/startup"
    ready_route = "/ready"
    starting_message = "Tornado-powered Django web server"
    starting_management_commands_message = "Starting execution of management commands"
    starting_http_message = "Starting HTTP Server on port 8000"

    @HurricanServerTest.cycle_server
    def test_default_startup(self):
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
        self.assertIn(
            "Starting probe application running on port 8001 with route liveness-probe: /alive, readiness-probe: /ready, startup-probe: /startup",
            out,
        )
        self.assertIn(self.starting_http_message, out)

    @HurricanServerTest.cycle_server(args=["--port", "8085"])
    def test_port_startup(self):
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
        self.assertIn(
            "Starting probe application running on port 8086 with route liveness-probe: /alive, readiness-probe: /ready, startup-probe: /startup",
            out,
        )

    @HurricanServerTest.cycle_server(args=["--no-probe"])
    def test_no_probe(self):
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
        self.assertIn("No probe application running", out)

    @HurricanServerTest.cycle_server(args=["--startup-probe", "probe", "--probe-port", "8090"])
    def test_probe_startup(self):
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
        self.assertIn("Starting probe application running on port 8090 with route", out)
        res = self.probe_client.get(self.probe_route)
        self.assertEqual(res.status, 200)
        res = self.probe_client.post(self.probe_route, data=None)
        self.assertEqual(res.status, 200)

    @HurricanServerTest.cycle_server(args=["--startup-probe", "probe", "--probe-port", "8000", "--port", "8000"])
    def test_probe_integrated_startup(self):
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
        self.assertIn("running integrated on port 8000", out)
        res = self.probe_client.get(self.probe_route)
        self.assertEqual(res.status, 200)

    @HurricanServerTest.cycle_server(args=["--no-metrics", "--probe-port", "8090"])
    def test_nometrics_startup(self):
        res = self.probe_client.get(self.alive_route)
        self.assertEqual(res.status, 200)
        self.assertIn("alive", res.text)

    @HurricanServerTest.cycle_server
    def test_request(self):
        res = self.app_client.get("/")
        out, err = self.driver.get_output(read_all=True)
        self.assertEqual(res.status, 200)
        self.assertIn("200 GET / ", out)
        self.assertIn("Hello world", res.text)

    @HurricanServerTest.cycle_server(args=["--static", "--media"])
    def test_serve_statics_and_media(self):
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
        self.assertIn(
            "Starting probe application running on port 8001 with route liveness-probe: /alive, readiness-probe: /ready, startup-probe: /startup",
            out,
        )
        self.assertIn(" Serving static files under /static/", out)
        self.assertIn("Serving media files under /media/", out)

    @HurricanServerTest.cycle_server
    def test_metrics_request(self):
        self.app_client.get("/")
        res = self.probe_client.get(self.alive_route)
        self.assertEqual(res.status, 200)
        self.assertIn("Average response time:", res.text)

    def _get_timing_from_string(self, string: str) -> str:
        m = re.compile(r"(?P<value>[0-9]*\.[0-9]{2})ms")
        match = m.search(string)
        if match:
            return match.group("value")

    @HurricanServerTest.cycle_server
    def test_metrics_average_response_time(self):
        self.app_client.get("/")
        self.app_client.get("/")
        self.app_client.get("/")
        out, err = self.driver.get_output(read_all=True)
        result = 0
        for line in out.split("\n"):
            timing = self._get_timing_from_string(line)
            if timing:
                result += float(timing)
        result /= 3
        res = self.probe_client.get(self.alive_route)

        timing = float(self._get_timing_from_string(res.text))
        self.assertEqual(res.status, 200)
        self.assertAlmostEqual(result, timing, 1)

    @HurricanServerTest.cycle_server
    def test_log_outputs(self):
        out, err = self.driver.get_output(read_all=True)
        res = self.app_client.get("/doesnotexist")
        self.assertEqual(res.status, 404)
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(" 404 GET /doesnotexist", out)
        res = self.app_client.get("/")
        self.assertEqual(res.status, 200)

    @HurricanServerTest.cycle_server
    def test_head_request(self):
        res = self.app_client.head("/")
        self.assertEqual(res.status, 200)
        self.assertEqual(res.text, "")

    @HurricanServerTest.cycle_server(args=["--autoreload"])
    def test_autoreload(self):
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
        self.assertIn("Autoreload was performed", out)
        self.assertIn(self.starting_http_message, out)

    @HurricanServerTest.cycle_server(args=["--command", "makemigrations", "--probe-port", "8090"])
    def test_startup_with_single_management_command(self):
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
        self.assertIn("Starting probe application running on port 8090", out)
        self.assertIn(self.starting_management_commands_message, out)
        self.assertIn(self.starting_http_message, out)

        res = self.probe_client.get(self.startup_route)
        self.assertEqual(res.status, 200)
        res = self.probe_client.post(self.startup_route, data=None)
        self.assertEqual(res.status, 200)
        res = self.probe_client.get(self.alive_route)
        self.assertEqual(res.status, 200)
        res = self.probe_client.get(self.ready_route)
        self.assertEqual(res.status, 200)
        res = self.app_client.get("/")
        self.assertEqual(res.status, 200)

    @HurricanServerTest.cycle_server(
        args=["--command", "makemigrations", "--command", "makemigrations", "--probe-port", "8090"]
    )
    def test_startup_with_multiple_management_commands(self):
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
        self.assertIn("Starting probe application running on port 8090 with route", out)
        self.assertIn(self.starting_management_commands_message, out)
        self.assertIn("No changes detected", out)
        self.assertIn(self.starting_http_message, out)

        res = self.probe_client.get(self.startup_route)
        self.assertEqual(res.status, 200)
        res = self.probe_client.post(self.startup_route, data=None)
        self.assertEqual(res.status, 200)
        res = self.probe_client.get(self.alive_route)
        self.assertEqual(res.status, 200)
        res = self.probe_client.get(self.ready_route)
        self.assertEqual(res.status, 200)
        res = self.app_client.get("/")
        self.assertEqual(res.status, 200)

    @HurricanServerTest.cycle_server(args=["--command", "migrates", "--probe-port", "8090"])
    def test_startup_failing_management_command(self):
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
        self.assertIn(
            "Starting probe application running on port 8090 with route liveness-probe: /alive, readiness-probe: /ready, startup-probe: /startup",
            out,
        )
        self.assertIn(self.starting_management_commands_message, out)
        self.assertIn("ERROR", out)

    @HurricanServerTest.cycle_server(args=["--webhook-url", "http://localhost:8074/webhook"])
    def test_webhook_no_endpoint(self):
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
        self.assertIn("Sending webhook to http://localhost:8074/webhook has failed", out)

    @HurricanServerTest.cycle_server(args=["--command", "migrates", "--webhook-url", "http://localhost:8074/webhook"])
    def test_startup_failed_command_webhook_no_endpoint(self):
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
        self.assertIn("Sending webhook to http://localhost:8074/webhook has failed", out)
        self.assertIn("Loop will be closed", out)

    @HurricanServerTest.cycle_server
    def test_duplicate_registration(self):
        from hurricane.metrics import registry
        from hurricane.metrics.requests import RequestCounterMetric

        try:
            registry.register(RequestCounterMetric)
        except Exception as e:
            exception = e
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
        self.assertIn("Metric ID (request_counter) is already registered.", str(exception))

    @HurricanServerTest.cycle_server
    def test_registration_metrics_wrong_key(self):
        class TestWrongKey:
            code = "test"

        from hurricane.metrics import registry

        registry.unregister(TestWrongKey)
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)

    @HurricanServerTest.cycle_server
    def test_unregistering_metrics(self):
        from hurricane.metrics import registry
        from hurricane.metrics.requests import RequestCounterMetric

        registry.unregister(RequestCounterMetric)
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)

    @HurricanServerTest.cycle_server
    def test_duplicate_registration_webhooks(self):
        from hurricane.webhooks import webhook_registry
        from hurricane.webhooks.webhook_types import StartupWebhook

        m = webhook_registry.get(StartupWebhook.code)

        try:
            webhook_registry.register(StartupWebhook)
        except Exception as e:
            exception = e
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(m.code, out)
        self.assertIn(self.starting_message, out)
        self.assertIn("Webhook Code (startup) is already registered.", str(exception))

    @HurricanServerTest.cycle_server
    def test_registration_webhooks_wrong_key(self):
        class TestWrongKey:
            code = "test"

        from hurricane.webhooks import webhook_registry

        webhook_registry.unregister(TestWrongKey)
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)

    @HurricanServerTest.cycle_server
    def test_unregistering_webhooks(self):
        from hurricane.webhooks import webhook_registry
        from hurricane.webhooks.webhook_types import StartupWebhook

        webhook_registry.unregister(StartupWebhook)
        out, err = self.driver.get_output(read_all=True)
        self.assertIn(self.starting_message, out)
