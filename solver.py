"""Solution to the powerplant production problem.
    `greedy_solver`: straightforward solution with greedy algorithm
"""
import utils


def greedy_solver(costs, efficiencies, pminmax, total_load):
    """Greedy algorithm to dispatch the powerplant in merit order,
    for which the powerplant with lower cost will be dispatched first.
    This order makes sure the total cost is minimized.
    """

    # merit/economic dispatching order: sort the costs assceding - low cost first
    # if two powerplants have the same cost, dispatch the one with higher efficiency
    dispatching_order = sorted(
        range(len(costs)), key=lambda i: (costs[i], -efficiencies[i])
    )

    pmins, pmaxs = zip(*pminmax)
    prods = [0] * len(costs)
    current_load = 0

    # start generating power by the merit order to match the expected load
    for i in dispatching_order:
        eff = efficiencies[i]
        if eff <= utils.EPSILON:
            continue

        # generate power from the ith plant according to the efficiency of this plant
        prod_i = (total_load - current_load) / eff

        # cap the generated product by the ith plant capacity
        prod_i = min(prod_i, pmaxs[i])
        if prod_i < pmins[i]:
            continue

        # add the contribution of the current plant to the current_load
        prods[i] += prod_i
        current_load += prod_i * eff

        if current_load == total_load:
            break

    return prods, dispatching_order
