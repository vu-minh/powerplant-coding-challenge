"""Util method for parsing data from input json
"""


EPSILON = 1e-12


def dot(a, b):
    """Dot product, aka sum of product of each pair of elements in two lists"""
    return sum(a_i * b_i for a_i, b_i in zip(a, b))


def parse_payload(payload):
    """Parse json payload to create input array for the solver/algorithm"""
    expected_load = payload["load"]
    fuels = payload["fuels"]
    powerplants = payload["powerplants"]
    names = [p["name"] for p in powerplants]
    pminmax = [(p["pmin"], p["pmax"]) for p in powerplants]

    # get the fuel price for each powerplant type
    price_key_mapping = {
        "turbojet": "kerosine(euro/MWh)",
        "gasfired": "gas(euro/MWh)",
        "windturbine": "wind(%)",
    }
    get_price = lambda ptype: fuels.get(price_key_mapping.get(ptype, ""), 0)

    # get the real cost and efficiency of each powerplant
    efficiencies = [0] * len(powerplants)
    costs = [0] * len(powerplants)
    for i, p in enumerate(powerplants):
        cost_i = get_price(p["type"])
        if p["type"] == "windturbine":
            efficiencies[i] = cost_i / 100.0
            costs[i] = 0
        else:
            efficiencies[i] = max(p["efficiency"], EPSILON)
            costs[i] = cost_i / efficiencies[i]

    return names, costs, efficiencies, pminmax, expected_load
