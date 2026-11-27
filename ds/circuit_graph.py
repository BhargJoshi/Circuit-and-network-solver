def build_adjacency_list(components):
    graph = {}
    for component in components:
        graph.setdefault(component["p"], []).append(component["n"])
        graph.setdefault(component["n"], []).append(component["p"])
    return graph
