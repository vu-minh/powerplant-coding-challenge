from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import utils
import solver


def create_response(payload):
    """Create response message for the input payload (dict).
    Parse the input for the input arrays and pass them to the algorithm.
    Handle response message and create a dict for the response message.
    """
    names, costs, efficiencies, pminmax, expected_load = utils.parse_payload(payload)
    prods, dispatching_order, solved, total_load = solver.greedy_solver(
        costs, efficiencies, pminmax, expected_load
    )

    if solved:
        message = [
            {"name": names[i], "p": prods[i] * efficiencies[i]}
            for i in dispatching_order
        ]
    else:
        message = {
            f"Message": "Infeasible problem: can not achieve {expected_load:.2f}"
            + f"Actual load generated: {total_load:.2f}"
        }
    return message


class Endpoint(BaseHTTPRequestHandler):
    """Endpoint class to serve HTTP request"""

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_POST(self):
        if (
            self.path != "/productionplan"
            or self.headers.get("content-type") != "application/json"
        ):
            self.send_error(400, "Use endpoint `/productionplan` and json payload")
            return

        length = int(self.headers.get("content-length"))
        payload_string = self.rfile.read(length).decode("utf-8")
        payload = json.loads(payload_string)

        message = create_response(payload)
        self._set_headers()
        self.wfile.write(bytes(json.dumps(message, indent=2), "utf8"))


if __name__ == "__main__":
    with HTTPServer(("", 8888), Endpoint) as server:
        print("Endpoint started")
        server.serve_forever()
        print("Endpoint stoped")
