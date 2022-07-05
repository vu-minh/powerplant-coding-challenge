import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

import utils
import solver


def create_response(payload):
    """Create response message for the input payload (dict).
    Parse the input for the input arrays and pass them to the algorithm.
    Handle response message and create a dict for the response message.
    """
    names, costs, efficiencies, pminmax, expected_load = utils.parse_payload(payload)
    prods, dispatching_order = solver.greedy_solver(
        costs, efficiencies, pminmax, expected_load
    )
    result = [
        {"name": names[i], "p": f"{(prods[i] * efficiencies[i]):.1f}"}
        for i in dispatching_order
    ]

    total_cost = utils.dot(prods, costs)
    total_prod = utils.dot(prods, efficiencies)
    solved = abs(total_prod - expected_load) <= utils.EPSILON

    logging.info(
        f"Problem {['not solved', 'solved'][int(solved)]} |"
        f" Generated load: {total_prod:.2f}, expected load: {expected_load:.2f},"
        f" Total cost: {total_cost:.2f}"
    )

    if not solved:
        msg_error = (
            f"Infeasible solution: can not achieve {expected_load:.2f}; "
            f"Actual load generated: {total_prod:.2f}"
        )
        logging.warning(msg_error)
        return {"Message": msg_error, "Result": result}

    return result


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
    # simple logging using the default root logger
    logging.basicConfig(level=logging.INFO)

    # custome HTTPServer on port 8888 to serve the endpoint
    with HTTPServer(("", 8888), Endpoint) as server:
        logging.info(
            "\nUsage: `curl -X POST localhost:8888/productionplan ` with json payload\n"
        )
        server.serve_forever()
