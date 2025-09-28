from itertools import combinations

import networkx as nx
from networkx.classes import neighbors


def prepare_nodes(graph):
    nodes_to_check = list(graph.nodes())
    for node in nodes_to_check:
        name = graph.nodes[node].get('NAME', None)
        if name is None:
            graph.remove_node(node)

def esu_enumerate(G, k):
    results = []
    seen = set()

    for v in G.nodes():
        neighbors = set(G.predecessors(v)) | set(G.successors(v))
        V_extension = {u for u in neighbors if u > v}
        extend_subgraph(G, k, {v}, V_extension, v, results, seen)
    return results


def extend_subgraph(G, k, V_sub, V_ext, v, results, seen):
    if len(V_sub) == k:
        # results.append(V_sub.copy())
        # Создаем frozenset для проверки уникальности
        sub_frozen = frozenset(V_sub)
        if sub_frozen not in seen:
            seen.add(sub_frozen)
            results.append(V_sub.copy())
        return

    while V_ext:
        w = V_ext.pop()
        new_sub = V_sub | {w}
        neighbors = set(G.predecessors(w)) | set(G.successors(w))
        neighbors_w = {u for u in neighbors if u not in V_sub and u > v}
        new_ext = V_ext | neighbors_w
        extend_subgraph(G, k, new_sub, new_ext, v, results, seen)


def get_all_weakly_connected_subgraphs(G, SUBGRAPH_SIZE):
    subgraphs = []
    for node_combination in combinations(G.nodes(), SUBGRAPH_SIZE):
        subgraph = G.subgraph(node_combination)
        if nx.is_weakly_connected(subgraph):
            subgraphs.append(subgraph)
    return subgraphs


G = nx.drawing.nx_agraph.read_dot("C:\\Users\\Alexey\\Documents\\VKR\\VSU_Plagiarism\\graphs\\315116517.dot")
prepare_nodes(G)
# G = nx.circulant_graph(10, [1])
connected_subgraphs = esu_enumerate(G, 4)
print(f"Найдено {len(connected_subgraphs)} связных подграфов размера 4")
connected_subgraphs = get_all_weakly_connected_subgraphs(G, 4)
print(f"Найдено {len(connected_subgraphs)} связных подграфов размера 4")