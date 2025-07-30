import os
import networkx as nx
from itertools import combinations
from tqdm import tqdm

SUBGRAPH_SIZE = 4

def prepare_nodes(graph):
    nodes_to_check = list(graph.nodes())
    for node in nodes_to_check:
        name = graph.nodes[node].get('NAME', None)
        if name is None:
            graph.remove_node(node)


def print_labels(G):
    for node in G.nodes():
        print(G.nodes[node]['NAME'])


# Функция для генерации всех индуцированных подграфов
def get_all_weakly_connected_subgraphs(graph):
    subgraphs = []
    # Перебор всех комбинаций вершин
    for node_subset in tqdm(tuple(combinations(graph.nodes(), SUBGRAPH_SIZE))):
        subgraph = graph.subgraph(node_subset)
        if nx.is_weakly_connected(subgraph):
            subgraphs.append(subgraph)
    return subgraphs


def plagiarism(G1, G2):
    G1_nodes_iso = {node: False for node in G1.nodes()}
    G1_all_subgraphs = get_all_weakly_connected_subgraphs(G1)
    print(f"Всего слабосвязных подграфов: {len(G1_all_subgraphs)}")
    isomorphic_subgraphs = []
    for subgraph in tqdm(G1_all_subgraphs):
        GM = nx.algorithms.isomorphism.DiGraphMatcher(G2, subgraph, node_match=lambda n1, n2: n1['NAME'] == n2['NAME'])
        if GM.subgraph_is_isomorphic():
            for node in subgraph.nodes():
                G1_nodes_iso[node] = True
            isomorphic_subgraphs.append(subgraph)
    print(f"Всего изоморфных подграфов: {len(isomorphic_subgraphs)}")
    print(f"Результат: {sum(G1_nodes_iso.values())}/{len(G1_nodes_iso)}")
    print("----------------------------------")
    return sum(G1_nodes_iso.values())/len(G1_nodes_iso)


folder_path = 'archive_cpp/graphs'  # Укажите путь к вашей папке
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
files_iso = {file: False for file in files}
results = []
for graph_subset in combinations(files, 2):
    G1_path, G2_path = graph_subset
    G1 = nx.drawing.nx_agraph.read_dot(f"archive_cpp/graphs/{G1_path}")
    G2 = nx.drawing.nx_agraph.read_dot(f"archive_cpp/graphs/{G2_path}")
    prepare_nodes(G1)
    prepare_nodes(G2)
    if G1.number_of_nodes() < G2.number_of_nodes():
        print(G1_path, G2_path)
        res = plagiarism(G1, G2)
        if res > 0.5:
            files_iso[G1_path] = True
            files_iso[G2_path] = True
        results.append((G1_path, G2_path, res))
    else:
        print(G2_path, G1_path)
        res = plagiarism(G2, G1)
        if res > 0.5:
            files_iso[G1_path] = True
            files_iso[G2_path] = True
        results.append((G2_path, G1_path, res))


# Сортировка по убыванию res
results.sort(key=lambda x: x[2], reverse=True)

# Запись в лог
with open("plagiarism_log.txt", "w", encoding="utf-8") as f:
    f.write("Результаты сравнения графов (отсортированы по убыванию res):\n")
    f.write("=" * 60 + "\n")
    for G1_name, G2_name, res in results:
        f.write(f"{G1_name} vs {G2_name}: {res:.4f}\n")
    f.write("=" * 60 + "\n")
    f.write("Итого в плагиате подозреваются:\n")
    for file in files_iso:
        if files_iso[file]:
            f.write(f"{file}\n")

print("\nЛог сохранён в plagiarism_log.txt")