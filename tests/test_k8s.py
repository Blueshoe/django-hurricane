import requests

from hurricane.testing.testcases import HurricaneK8sServerTest


class HurricaneK8sServerTests(HurricaneK8sServerTest):
    @HurricaneK8sServerTest.cycle_server
    def test_k8s(self):
        response = requests.get("http://localhost:8072/k8s", timeout=5)
        out, err = self.driver.get_output(read_all=True)

        self.assertIn("Started K8s server", out)
        self.assertIn("Request count", out)
        self.assertEqual(response.status_code, 200)
