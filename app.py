# Standalone Streamlit app for power plant production problem
# Only for a demo with a quick solution in a visual way

import json
from typing import Any
from dataclasses import dataclass
import streamlit as st
import solver


DATA_PATH = "example_payloads"
ASSETS_PATH = "assets"
EXAMPLE_PAYLOAD_PROFILE_IDS = (None, 1, 2, 3)
N_POWERPLANT_TO_SHOW_PER_ROW = 6
MIN_CAPACITY = 0.0
MAX_CAPACITY = 600.0


@dataclass
class Config:
    expected_load: int
    wind_power: float
    co2_price: float
    fuel_prices: Any


# load input data
def load_profile(profile_id=1):
    payload_file_name = f"{DATA_PATH}/payload{profile_id}.json"
    with open(payload_file_name, "r") as f:
        payload = json.load(f)

    # read config
    expected_load = payload["load"]
    fuels = payload["fuels"]
    fuel_prices = {
        "gasfired": fuels["gas(euro/MWh)"],
        "turbojet": fuels["kerosine(euro/MWh)"],
    }
    co2_price = fuels["co2(euro/ton)"]
    wind_power = fuels["wind(%)"] / 100.0
    config = Config(expected_load, wind_power, co2_price, fuel_prices)

    powerplants = payload["powerplants"]
    return payload, config, powerplants


def show_config(config, where=st):
    where.metric(label="Expected load", value=f"{config.expected_load} MWh")

    for fuel, price in config.fuel_prices.items():
        where.metric(label=f"Fuel price for {fuel}", value=f"{price} €/MWh")

    where.metric(label="Wind efficiency", value=f"{config.wind_power * 100} %")
    where.metric(label="CO2 cost", value=f"{config.co2_price} €/ton")


def show_powerplants(powerplants, current_productions=None):
    N = len(powerplants)
    not_solved = current_productions is None
    if not_solved:
        current_productions = [float(p["pmin"]) for p in powerplants]
    txt_cost = [None] * N
    txt_real_load = [None] * N

    for p, col in zip(powerplants, st.columns(N)):
        col.image(f"{ASSETS_PATH}/{p['type']}.png", width=80, caption=p["type"])
    st.markdown("""---""")

    for i, (p, col) in enumerate(zip(powerplants, st.columns(N))):
        pmin, pmax = float(p["pmin"]), float(p["pmax"])
        col.slider(
            f"Power plant {i+1} Capacity",
            MIN_CAPACITY,
            pmax * 1.35,
            (pmin, pmax),
            disabled=True,
        )
        col.metric(
            label="Plant Efficiency",
            value=p["efficiency"],
            # delta=f'{(p["efficiency"]-0.5):.2f}'
        )

        current_productions[i] = col.slider(
            "Production",
            min_value=pmin,
            max_value=pmax,
            value=current_productions[i],
            disabled=not not_solved,
            key=f"production_{i}",
        )

        txt_real_load[i] = col.text("Real load: 0")
        txt_cost[i] = col.text("Cost: 0")

    st.markdown("""---""")

    return current_productions, txt_real_load, txt_cost


def show_value_in_txt_elems(values, elems, info=""):
    for v, e in zip(values, elems):
        e.text(f"{info}: {v:.1f}")


def show_summary(real_load, cost, config):
    c1, c2, c3 = st.columns(3)
    c1.metric("Total generated load", f"{sum(real_load):.1f} MWh")
    c2.metric("Total cost", f"€ {sum(cost):.1f}")
    c3.metric(
        f"Difference with the expected load",
        f"{(sum(real_load) - config.expected_load):.1f}",
    )


def reparse_data(config, powerplants):
    N = len(powerplants)
    expected_load = config.expected_load

    # capacity constraints
    bounds = [(p["pmin"], p["pmax"]) for p in powerplants]

    # create a vector of cost factor and the efficiency factor
    costs = [0] * N
    efficiencies = [0] * N

    for i, p in enumerate(powerplants):
        eff = p["efficiency"]
        ptype = p["type"]

        if ptype in ["gasfired", "turbojet"]:
            efficiencies[i] = eff
            costs[i] = config.fuel_prices.get(ptype, 0) / eff

        elif ptype == "windturbine":
            efficiencies[i] = config.wind_power
            costs[i] = 0

    return costs, efficiencies, bounds, expected_load


###############################################################################
def main_streamlit_app():
    st.set_page_config(page_title="Demo app - Powerplant Production", layout="wide")
    st.title("Powerplant Production Problem")

    # Add a selectbox to the sidebar:
    profile_id = st.sidebar.selectbox(
        "Select payload profile: ", EXAMPLE_PAYLOAD_PROFILE_IDS
    )

    if profile_id is not None:
        # when the profile_id is selected, load the corresponding payload profile
        # and show the config of this profile

        _, config, powerplants = load_profile(profile_id)
        show_config(config, where=st.sidebar)

        # re-prepare the input data and call the core algorithm
        costs, efficiencies, pminmax, expected_load = reparse_data(config, powerplants)

        st.table(powerplants)

        current_productions = None
        final_result = None

        # the current production solution is available when we call the solver
        # otherwise, just let users move the slider to update the estimate production
        if st.button("SOLVE"):
            final_result = solver.LP_solver(costs, efficiencies, pminmax, expected_load)
            current_productions = final_result.x.tolist()

        # otherwise, visualize the powerplant with the corresponding solved/estimated production
        current_productions, txt_real_load, txt_cost = show_powerplants(
            powerplants, current_productions
        )

        # calculate the real production and cost to update the gui
        real_load = [p * e for (p, e) in zip(current_productions, efficiencies)]
        total_costs = [
            p * e * c for (p, e, c) in zip(current_productions, efficiencies, costs)
        ]
        show_value_in_txt_elems(real_load, txt_real_load, "Real Load")
        show_value_in_txt_elems(total_costs, txt_cost, "Cost")

        # finally, show the updated metric and cost calculated above
        show_summary(real_load, total_costs, config)

        # show debug info
        with st.expander("Show Debug Info"):
            if final_result is None:
                st.write("Problem is not solved")
            else:
                st.write(final_result)

    # show explanation
    with st.expander("Show Explanation"):
        with open(f"{ASSETS_PATH}/powerplant_explanation.md", "r") as f:
            st.markdown(f.read())


if __name__ == "__main__":
    main_streamlit_app()
