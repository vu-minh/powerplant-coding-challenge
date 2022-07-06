## Powerplant Efficiency

```
Load = total demand of power. The powerplants must generate power (production) that are equal to the demanded load.

                    +---------------+
                    | POWERPLANT    |
MWh of fuel ------> | efficiency eff| -------> MWh of electricity
                    | (eff = 0.5)   |
                    +---------------+

2 MWh of fuel ------> (eff = 0.5) -----------> 1 MWh of electricy

fuel price:10 €/MWh
-> real cost to generate 1 MWh electricy with this fuel is price/eff = 20 €/MWh
```

## Linear Programming (LP) Model Explanation

LP is to minimize a linear objective function $c^T x$ subject to linear equality/inequality constraints, and has the form:

$$
\begin{equation}
\begin{aligned}
& \min_{x}      & c^T x     &               & \\
& \text{s.t. }  & A_{ub} x  & \leq b_{ub},  & \\
&               & A_{eq} x  & = b_{eq},     & \\
&               & l \leq    &  x \leq u
\end{aligned}
\end{equation}
$$

In this problem, the vector $x$ is the production of the powerplants we need to find.
$x$ is bounded by the capacity of the powerplants, that means $pmin \leq  x \leq pmax$.

We need to generate the expected load $b_{eq}$ by combining the production generated by each powerplant $x_1, x_2, ..., x_n$, controled by the plants' efficiency $e_1, e_2, ..., e_n$:

$$
\text{expected load} = b_{eq} = \sum_{i=1}^{n} e_i  x_i
$$

The final goal is to minimize the total cost
$$
\sum_{i=1}^{n} cost_i x_i,
$$
where `cost_i` $ = \dfrac{\text{fuel\_price}[i]}{\text{efficiencies}[i]}$ is the real cost when taking into account the powerplant efficiency (CO2 price is added to the fuel price for gas powerplant if considered) and the cost of wind turbine is always 0.

In pseudo code, the problem can be translated as:

```python
minimize:    objective = fuel_price @ x
subject to:  efficiencies @ x == expected_load
             pmin <= x <= pmax
```