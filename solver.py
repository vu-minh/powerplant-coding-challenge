"""Solution to the powerplant production problem.
    `greedy_solver`: straightforward solution with greedy algorithm
"""
from utils import dot


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

    # the initial state is the minumum capacity of each power plant
    pmins, pmaxs = zip(*pminmax)
    prods = list(pmins)
    current_load = dot(prods, efficiencies)

    # start generating power by the merit order to match the expected load
    for i in dispatching_order:
        eff = efficiencies[i]

        # generate power from the ith plant according to the efficiency of this plant
        prod_i = (total_load - current_load) / eff
        print("prod_i", prod_i, current_load, eff, pmaxs[i], pmins[i])

        # cap the generated product by the ith plant capacity
        # note that the gas powerplants (all plants) are at their minimum capacity
        prod_i = min(prod_i, pmaxs[i] - pmins[i])

        # add the contribution of the current plant to the current_load
        prods[i] += prod_i
        current_load += prod_i * eff
        print(i, prods[i], prod_i * eff)

        solved = current_load == total_load
        if solved:
            break

    # return the production of each powerplant and the total cost
    return prods, dispatching_order, solved, dot(prods, costs)


# if __name__ == "__main__":
#     data_path = "data/payload1.json"

#     prods, status, cost = greedy_solver(*extract_constraints(data_path))
#     print(prods, status, cost)
