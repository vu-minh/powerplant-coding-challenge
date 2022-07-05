"""Util method for parsing data from input json
"""
import math

EPSILON = 1e-12


def sumprod(*vecs):
    print(vecs)
    """Sum product of any input vectors `x, y, z,...`, which is Σ x_i * y_i * z_i * ..."""
    return sum(math.prod(ei) for ei in zip(*vecs))


def parse_payload(payload, CO2=False):
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
        "co2": "co2(euro/ton)",
    }
    get_price = lambda ptype: fuels.get(price_key_mapping.get(ptype, ""), 0)
    get_co2_price = lambda ptype: get_price("co2") if ptype == "gasfired" else 0

    # get the real cost and efficiency of each powerplant
    efficiencies = [0] * len(powerplants)
    costs = [0] * len(powerplants)
    for i, p in enumerate(powerplants):
        # fuel cost to generate 1MWh electricity, taking into account CO2 price if specified
        cost_i = get_price(p["type"]) + (0.3 * get_co2_price(p["type"]) if CO2 else 0)
        if p["type"] == "windturbine":
            efficiencies[i] = cost_i / 100.0
            costs[i] = 0
        else:
            efficiencies[i] = max(p["efficiency"], EPSILON)
            costs[i] = cost_i / efficiencies[i]

    return names, costs, efficiencies, pminmax, expected_load
