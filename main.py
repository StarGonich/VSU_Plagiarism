import os
import functools

import networkx as nx
from itertools import combinations
from tqdm import tqdm

from LogParser import LogParser

LOGPATH = r"C:\Users\Alexey\Documents\VKR\VSU_Plagiarism\log.txt"
ARCHIVEPATH = r"C:\Users\Alexey\Documents\VKR\VSU_Plagiarism\602776"
GRAPHSPATH = r"C:\Users\Alexey\Documents\VKR\VSU_Plagiarism\graphs"

SUBGRAPH_SIZE = 5
SEARCH = 'K'
PLAGIARISM_METRIC = 0.6

cache = set()


def extend_subgraph(G, k, V_sub, V_ext, v, results, seen):
    if len(V_sub) == k:
        # results.append(V_sub.copy())
        # Создаем frozenset для проверки уникальности
        sub_frozen = frozenset(V_sub)
        if sub_frozen not in seen:
            seen.add(sub_frozen)
            results.append(G.subgraph(V_sub))
        return
    while V_ext:
        w = V_ext.pop()
        new_sub = V_sub | {w}
        neighbors = set(G.predecessors(w)) | set(G.successors(w))
        neighbors_w = {u for u in neighbors if u not in V_sub and u > v}
        new_ext = V_ext | neighbors_w
        extend_subgraph(G, k, new_sub, new_ext, v, results, seen)


def prepare_nodes(graph):
    nodes_to_remove = []
    for node in graph.nodes():
        name = graph.nodes[node].get('NAME', None)
        if name is None:
            nodes_to_remove.append(node)
    graph.remove_nodes_from(nodes_to_remove)
    components_to_remove = []
    weak_components = tuple(nx.weakly_connected_components(graph))
    for component in weak_components:
        if len(component) < SUBGRAPH_SIZE:
            components_to_remove.extend(component)
    graph.remove_nodes_from(components_to_remove)


def print_labels(G):
    for node in G.nodes():
        print(G.nodes[node]['NAME'])


@functools.lru_cache(maxsize=None)
def get_all_weakly_connected_subgraphs(G_path):
    cache.add(G_path)
    G = nx.drawing.nx_agraph.read_dot(f"{GRAPHSPATH}/{G_path}")
    prepare_nodes(G)
    subgraphs = []

    seen = set()
    for v in tqdm(G.nodes(),
                  desc=f"Getting subgraphs of {G_path}", position=2, leave=False, ascii=True, colour='yellow'):
        neighbors = set(G.predecessors(v)) | set(G.successors(v))
        V_extension = {u for u in neighbors if u > v}
        extend_subgraph(G, SUBGRAPH_SIZE, {v}, V_extension, v, subgraphs, seen)

    # weak_components = tuple(nx.weakly_connected_components(G))
    # for component in tqdm(tuple(weak_components),
    #                       desc=f"Getting subgraphs of {G_path}", position=1, ascii=True, colour='blue'):
    #     if len(component) >= SUBGRAPH_SIZE:
    #         for node_combination in tqdm(tuple(combinations(component, SUBGRAPH_SIZE)),
    #                                      position=2, leave=False, ascii=True, colour='yellow'):
    #             subgraph = G.subgraph(node_combination)  # создание графа из вершин
    #             if nx.is_weakly_connected(subgraph):  # if (граф слабосвязный)
    #                 subgraphs.append(subgraph)
    # for sub in subgraphs:
    #     print(sub.nodes())
    return subgraphs


def plagiarism(G1_path, G1, G2):
    G1_nodes_iso = {node: False for node in G1.nodes()}
    G1_all_subgraphs = get_all_weakly_connected_subgraphs(G1_path)
    print(f"\nAll weakly graphs: {len(G1_all_subgraphs)}")
    isomorphic_subgraphs = []

    for subgraph in tqdm(G1_all_subgraphs,
                         desc=f"Isomorphism", leave=False, position=3, ascii=True):
        if all(G1_nodes_iso[node] for node in subgraph.nodes()):
            continue  # Пропускаем проверку изоморфизма
        GM = nx.algorithms.isomorphism.DiGraphMatcher(G2, subgraph, node_match=lambda n1, n2: n1['NAME'] == n2['NAME'])
        if GM.subgraph_is_isomorphic():
            for node in subgraph.nodes():
                G1_nodes_iso[node] = True
            isomorphic_subgraphs.append(subgraph)
    print(f"\nAll isomorphic graphs: {len(isomorphic_subgraphs)}")
    print(f"Result: {sum(G1_nodes_iso.values())}/{len(G1_nodes_iso)}")
    print("----------------------------------")
    return sum(G1_nodes_iso.values())/len(G1_nodes_iso)


def printlog(problem, results):
    with open(f"{problem.code}{SUBGRAPH_SIZE}_log.txt", "w", encoding="utf-8") as f:
        f.write("Результаты сравнения графов (отсортированы по убыванию res):\n")
        f.write("=" * 60 + "\n")
        for G1_name, G2_name, res in results:
            f.write(f"{G1_name} & {G2_name}: {res:.4f}\n")
        f.write("=" * 60 + "\n")
        f.write("Итого в плагиате подозреваются:\n")
        for file in files_iso:
            if files_iso[file]:
                f.write(f"{file}\n")
    print(f"\nЛог сохранён в {problem.code}_log.txt")


# files = [f for f in os.listdir(GRAPHSPATH) if os.path.isfile(os.path.join(GRAPHSPATH, f))]

logparser = LogParser(LOGPATH, ARCHIVEPATH)
logparser.parse()

results = []
check_errors = []

for problem in logparser.problems:
    if problem.code not in SEARCH:
        continue
    files_iso = {sub.filename: False for sub in problem.submissions}
    print(problem.code, problem.name)
    submissions = [sub for sub in problem.submissions if sub.verdict == 'OK']
    for graph_subset in tqdm(tuple(combinations(submissions, 2)),
                             desc="Combinations of programs", position=0, ascii=True, colour='green'):
        G1_sub, G2_sub = graph_subset
        G1_path = f"{os.path.splitext(G1_sub.filename)[0]}.dot"
        G2_path = f"{os.path.splitext(G2_sub.filename)[0]}.dot"
        G1 = nx.drawing.nx_agraph.read_dot(f"{GRAPHSPATH}/{G1_path}")
        G2 = nx.drawing.nx_agraph.read_dot(f"{GRAPHSPATH}/{G2_path}")
        prepare_nodes(G1)
        prepare_nodes(G2)
        print("\nBefore swap:", G1_path, G2_path)
        if G1_path not in cache and (G2_path in cache or G1.number_of_nodes() > G2.number_of_nodes()):
            G1_path, G2_path = G2_path, G1_path
            G1, G2 = G2, G1
        print("After swap:", G1_path, G2_path)
        if G1.number_of_nodes() != 0:
            res = plagiarism(G1_path, G1, G2)
            if res > PLAGIARISM_METRIC:
                files_iso[G1_path] = True
                files_iso[G2_path] = True
            results.append((G1_path, G2_path, res))
        else:
            check_errors.append(G1_path)
    results.sort(key=lambda x: x[2], reverse=True)
    printlog(problem, results)
    results.clear()
    get_all_weakly_connected_subgraphs.cache_clear()