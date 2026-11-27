from collections import defaultdict
from math_engine.linear_algebra import gaussian_elimination, matrix_rank, null_space

def parse_netlist(text):
    components, names = [], set()
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 4:
            raise ValueError(f"Line {line_no}: expected 4 comma-separated fields.")
        name, p, n, value = parts
        if not name or name in names:
            raise ValueError(f"Line {line_no}: component names must be non-empty and unique.")
        names.add(name)
        kind = name[0].upper()
        if kind not in ("R", "V"):
            raise ValueError(f"Line {line_no}: component '{name}' must start with R (resistor) or V (voltage source).")
        if p == n:
            raise ValueError(f"Line {line_no}: a component cannot connect a node to itself.")
        try:
            value = float(value)
        except ValueError:
            raise ValueError(f"Line {line_no}: component value must be numeric.")
        if kind == "R" and value <= 0:
            raise ValueError(f"Line {line_no}: resistance must be greater than zero.")
        components.append({"name": name, "kind": kind, "p": p, "n": n, "value": value})
    if not components:
        raise ValueError("Enter at least one resistor or voltage source.")
    if not any(c["kind"] == "R" for c in components):
        raise ValueError("At least one resistor is required.")
    return components

def solve_circuit(text):
    comps = parse_netlist(text)
    nodes = sorted({x for c in comps for x in (c["p"], c["n"]) if x != "0"})
    node_map = {"0": 0}
    for i, node in enumerate(nodes, 1):
        node_map[node] = i
    v_unknowns = [f"V({n})" for n in nodes]
    sources = [c for c in comps if c["kind"] == "V"]
    unknowns = v_unknowns + [f"I({c['name']})" for c in sources]
    idx = {n: i for i, n in enumerate(nodes)}
    n_v, size = len(nodes), len(unknowns)
    if size == 0:
        raise ValueError("Circuit has no non-ground node voltage to solve.")
    A = [[0.0]*size for _ in range(size)]
    b = [0.0]*size
    equations = []
    # KCL at each non-ground node; resistor conductance and source branch currents.
    for c in comps:
        p, n = c["p"], c["n"]
        if c["kind"] == "R":
            g = 1.0/c["value"]
            if p != "0":
                A[idx[p]][idx[p]] += g
                if n != "0": A[idx[p]][idx[n]] -= g
            if n != "0":
                A[idx[n]][idx[n]] += g
                if p != "0": A[idx[n]][idx[p]] -= g
        else:
            j = n_v + sources.index(c)
            if p != "0": A[idx[p]][j] += 1.0
            if n != "0": A[idx[n]][j] -= 1.0
    for i, node in enumerate(nodes):
        terms = []
        for c in comps:
            if c["kind"] == "R" and node in (c["p"], c["n"]):
                other = c["n"] if node == c["p"] else c["p"]
                terms.append(f"(V({node})-V({other}))/({c['value']:g})")
            elif c["kind"] == "V" and node in (c["p"], c["n"]):
                sign = "+" if node == c["p"] else "-"
                terms.append(f"{sign} I({c['name']})")
        equations.append(f"ΣI at node {node} = 0: " + " + ".join(terms) + " = 0")
    for k, c in enumerate(sources):
        row = n_v+k
        if c["p"] != "0": A[row][idx[c["p"]]] += 1.0
        if c["n"] != "0": A[row][idx[c["n"]]] -= 1.0
        b[row] = c["value"]
        equations.append(f"Voltage constraint {c['name']}: V({c['p']}) - V({c['n']}) = {c['value']:g} V")
    reduced, pivots, pivot_rows, det, steps = gaussian_elimination(A, b)
    rank_a = matrix_rank(A)
    aug = [list(map(float, A[i])) + [float(b[i])] for i in range(size)]
    rank_aug = matrix_rank(aug)
    status = "none" if rank_a != rank_aug else ("unique" if rank_a == size else "infinite")
    basis = null_space(A)
    voltages, currents = {}, {}
    if status == "unique":
        solution = [0.0]*size
        for i, col in enumerate(pivots):
            solution[col] = reduced[i][-1]
        voltages = {"0": 0.0}
        for node in nodes: voltages[node] = solution[idx[node]]
        for c in comps:
            if c["kind"] == "R":
                vp = voltages.get(c["p"], 0.0); vn = voltages.get(c["n"], 0.0)
                currents[c["name"]] = (vp-vn)/c["value"]
            else:
                currents[c["name"]] = solution[n_v + sources.index(c)]
    adjacency = defaultdict(set)
    for c in comps:
        adjacency[c["p"]].add(c["n"]); adjacency[c["n"]].add(c["p"])
    adjacency = {node: sorted(adjacency.get(node, set())) for node in sorted({"0"} | set(nodes))}
    return {"components": comps, "node_map": node_map, "adjacency": adjacency,
            "unknowns": unknowns, "equations": equations, "A": A, "b": b,
            "rank_A": rank_a, "rank_aug": rank_aug, "status": status,
            "steps": steps, "determinant_text": f"{det:.8g}" if size == len(A) else "not square",
            "nullspace": basis, "voltages": voltages, "currents": currents}
