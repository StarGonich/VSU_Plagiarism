import os
import functools

import networkx as nx
from itertools import combinations
from tqdm import tqdm

from LogParser import LogParser

SUBGRAPH_SIZE = 4
LOGPATH = r"C:\Users\Alexey\Documents\VKR\VSU_Plagiarism\log.txt"
ARCHIVEPATH = r"C:\Users\Alexey\Documents\VKR\VSU_Plagiarism\602776"
GRAPHSPATH = r"C:\Users\Alexey\Documents\VKR\VSU_Plagiarism\graphs"
cache = set()

def prepare_nodes(graph):
    nodes_to_check = list(graph.nodes())
    for node in nodes_to_check:
        name = graph.nodes[node].get('NAME', None)
        if name is None:
            graph.remove_node(node)


def print_labels(G):
    for node in G.nodes():
        print(G.nodes[node]['NAME'])


@functools.lru_cache(maxsize=None)
def get_all_weakly_connected_subgraphs(G_path):
    cache.add(G_path)
    graph = nx.drawing.nx_agraph.read_dot(f"{GRAPHSPATH}/{G_path}")
    prepare_nodes(graph)
    subgraphs = []
    for node_subset in tqdm(tuple(combinations(graph.nodes(), SUBGRAPH_SIZE)),
                            desc=f"Subgraph combinations of {G_path}", position=1, ascii=True):
        subgraph = graph.subgraph(node_subset)
        if nx.is_weakly_connected(subgraph):
            subgraphs.append(subgraph)
    return subgraphs


def plagiarism(G1_path, G1, G2):
    G1_all_subgraphs = get_all_weakly_connected_subgraphs(G1_path)
    G1_nodes_iso = {node: False for node in G1.nodes()}
    print(f"All weakly graphs: {len(G1_all_subgraphs)}")
    isomorphic_subgraphs = []
    for subgraph in tqdm(G1_all_subgraphs, desc=f"Isomorphism", leave=False, position=1, ascii=True):
        GM = nx.algorithms.isomorphism.DiGraphMatcher(G2, subgraph, node_match=lambda n1, n2: n1['NAME'] == n2['NAME'])
        if GM.subgraph_is_isomorphic():
            for node in subgraph.nodes():
                G1_nodes_iso[node] = True
            isomorphic_subgraphs.append(subgraph)
    print(f"All isomorphic graphs: {len(isomorphic_subgraphs)}")
    print(f"Result: {sum(G1_nodes_iso.values())}/{len(G1_nodes_iso)}")
    print("----------------------------------")
    return sum(G1_nodes_iso.values())/len(G1_nodes_iso)


files = [f for f in os.listdir(GRAPHSPATH) if os.path.isfile(os.path.join(GRAPHSPATH, f))]

logparser = LogParser(LOGPATH, ARCHIVEPATH)
logparser.parse()

files_iso = {file: False for file in files}
results = []
too_large_graphs = []
search = ['E']

for problem in logparser.problems:
    if problem.code not in search:
        continue
    print(problem.code, problem.name)
    submissions = [sub for sub in problem.submissions if sub.verdict == 'OK']
    for graph_subset in tqdm(tuple(combinations(submissions, 2)), desc="Combinations of programs", position=0, ascii=True):
        G1_sub, G2_sub = graph_subset
        G1_path = f"{os.path.splitext(G1_sub.filename)[0]}.dot"
        G2_path = f"{os.path.splitext(G2_sub.filename)[0]}.dot"
        G1 = nx.drawing.nx_agraph.read_dot(f"{GRAPHSPATH}/{G1_path}")
        G2 = nx.drawing.nx_agraph.read_dot(f"{GRAPHSPATH}/{G2_path}")
        prepare_nodes(G1)
        prepare_nodes(G2)
        print("Before swap:", G1_path, G2_path)
        if G1_path not in cache and G2_path in cache or G1_path not in cache and G2_path not in cache and G1.number_of_nodes() > G2.number_of_nodes():
            G1_path, G2_path = G2_path, G1_path
            G1, G2 = G2, G1
        print("After swap:", G1_path, G2_path)
        res = plagiarism(G1_path, G1, G2)
        if res > 0.6:
            files_iso[G1_path] = True
            files_iso[G2_path] = True
        results.append((G1_path, G2_path, res))


# Сортировка по убыванию
results.sort(key=lambda x: x[2], reverse=True)

# Запись в лог
with open("plagiarism_log.txt", "w", encoding="utf-8") as f:
    f.write("Результаты сравнения графов (отсортированы по убыванию res):\n")
    f.write("=" * 60 + "\n")
    for G1_name, G2_name, res in results:
        f.write(f"{G1_name} & {G2_name}: {res:.4f}\n")
    f.write("=" * 60 + "\n")
    f.write("Итого в плагиате подозреваются:\n")
    for file in files_iso:
        if files_iso[file]:
            f.write(f"{file}\n")

print("\nЛог сохранён в plagiarism_log.txt")