import os
import functools
from io import StringIO

import networkx as nx
# import vf3py
from itertools import combinations
from tqdm import tqdm

from PlagiarismDB import PlagiarismDB, Submission

LOGPATH = "log.txt"
ARCHIVEPATH = "602776"
GRAPHSDIR= "graphs"
LOGSDIR = "logs"

SUBGRAPH_SIZE = 4
SEARCH = 'C'
# PLAGIARISM_METRIC = 0.6

cache = set()


def extend_subgraph(G, k, V_sub, V_ext, v, results, seen):
    if len(V_sub) == k:
        # results.append(V_sub.copy())
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
    G = nx.drawing.nx_agraph.read_dot(f"{GRAPHSDIR}/{G_path}")
    prepare_nodes(G)
    subgraphs = []
    seen = set()
    for v in tqdm(G.nodes(),
                  desc=f"Getting subgraphs of {G_path}", position=1, leave=False, ascii=True, colour='yellow'):
        neighbors = set(G.predecessors(v)) | set(G.successors(v))
        V_extension = {u for u in neighbors if u > v}
        extend_subgraph(G, SUBGRAPH_SIZE, {v}, V_extension, v, subgraphs, seen)
    return subgraphs


def plagiarism(G1_path, G1, G2):
    G1_nodes_iso = {node: False for node in G1.nodes()}
    G1_all_subgraphs = get_all_weakly_connected_subgraphs(G1_path)

    for subgraph in tqdm(G1_all_subgraphs,
                         desc=f"Isomorphism", leave=False, position=1, ascii=True):
        if all(G1_nodes_iso[node] for node in subgraph.nodes()):
            continue  # Пропускаем проверку изоморфизма
        is_isomorhic = nx.algorithms.isomorphism.DiGraphMatcher(
            G2, subgraph, node_match=lambda n1, n2: n1['NAME'] == n2['NAME']).subgraph_is_isomorphic()
        # iso = vf3py.has_subgraph(subgraph, G2, node_match=lambda n1, n2: n1['NAME'] == n2['NAME'], variant='P', num_threads=8)
        # iso = grandiso.find_motifs(subgraph, G2, is_node_attr_match=lambda p_id, t_id, p_g, t_g: (p_g.nodes[p_id].get('NAME') == t_g.nodes[t_id].get('NAME')))
        if is_isomorhic:
            for node in subgraph.nodes():
                G1_nodes_iso[node] = True
    return sum(G1_nodes_iso.values())/len(G1_nodes_iso)


def printlog(problem, results):
    if not os.path.exists(LOGSDIR):
        os.makedirs(LOGSDIR)
    log_file_path = os.path.join(LOGSDIR, f"{problem.code}_log.txt")
    with open(f"{log_file_path}", "w", encoding="utf-8") as f:
        f.write("Результаты сравнения графов (отсортированы по убыванию итогового результата):\n")
        f.write("=" * 60 + "\n")
        for G1, G2, res1, res2, res in results:
            f.write(f"{G1.submission_id}{G1.language} -> {G2.submission_id}{G2.language}: {res1:.4f}\n")
            f.write(f"{G2.submission_id}{G2.language} -> {G1.submission_id}{G1.language}: {res2:.4f}\n")
            f.write(f"Итоговый результат: {res}\n")
            f.write("-"*40+"\n")
        # f.write("=" * 60 + "\n")
        # f.write("Итого в плагиате подозреваются:\n")
        # for file in files_iso:
        #     if files_iso[file]:
        #         f.write(f"{file}\n")
        if errors:
            f.write("Графы, после обработки становящиемся пустыми:\n")
            for error in errors:
                f.write(f"{error}\n")

    print(f"\nЛог сохранён в {log_file_path}")


def get_graph_code(submission: Submission):
    cursor = db.conn.cursor()
    cursor.execute("""
            SELECT graph FROM submissions WHERE submission_id = ?
            """, (submission.submission_id,))
    result = cursor.fetchone()
    if result is None or result[0] is None:
        with open(f"./{GRAPHSDIR}/{submission.submission_id}.dot", 'r', encoding='utf-8') as f:
            code = f.read()
        cursor.execute("""
                    UPDATE submissions 
                    SET graph = ? 
                    WHERE submission_id = ?
                """, (code, submission.submission_id))
        db.conn.commit()
        return code
    return result[0]


# files = [f for f in os.listdir(GRAPHSDIR) if os.path.isfile(os.path.join(GRAPHSDIR, f))]

db = PlagiarismDB('plagiarism.db')
db.parse(LOGPATH, ARCHIVEPATH)
problems = db.get_problems_by_contest(int(ARCHIVEPATH))

results = []
errors = set()

for problem in problems:
    if problem.code not in SEARCH:
        continue
    # files_iso = {sub.filename: False for sub in problem.submissions}
    submissions = [sub for sub in db.get_submissions_by_problem(problem.id) if sub.verdict == 'OK']
    for graph_subset in tqdm(tuple(combinations(submissions, 2)),
                             desc=f"{problem.code}-{problem.name}: combinations of programs", position=0, ascii=True, colour='green'):
        G1_sub, G2_sub = graph_subset

        G1_dotpath = f"{G1_sub.submission_id}.dot"
        G2_dotpath = f"{G2_sub.submission_id}.dot"
        get_graph_code(G1_sub)
        get_graph_code(G2_sub)
        # G1 = nx.nx_agraph.read_dot(StringIO(get_graph_code(G1_sub)))
        # G2 = nx.nx_agraph.read_dot(StringIO(get_graph_code(G2_sub)))
        G1 = nx.drawing.nx_agraph.read_dot(f"./{GRAPHSDIR}/{G1_dotpath}")
        G2 = nx.drawing.nx_agraph.read_dot(f"./{GRAPHSDIR}/{G2_dotpath}")
        prepare_nodes(G1)
        if G1.number_of_nodes() == 0:
            errors.add(G1_dotpath)
            continue
        prepare_nodes(G2)
        if G2.number_of_nodes() == 0:
            errors.add(G2_dotpath)
            continue
        # if G1_dotpath not in cache and (G2_dotpath in cache or G1.number_of_nodes() > G2.number_of_nodes()):
        #     G1_sub, G2_sub = G2_sub, G1_sub
        #     G1_dotpath, G2_dotpath = G2_dotpath, G1_dotpath
        #     G1, G2 = G2, G1
        res1 = plagiarism(G1_dotpath, G1, G2)
        res2 = plagiarism(G2_dotpath, G2, G1)
        db.save_result(G1_sub.submission_id, G2_sub.submission_id, SUBGRAPH_SIZE, res1)
        db.save_result(G2_sub.submission_id, G1_sub.submission_id, SUBGRAPH_SIZE, res2)
        mn = min(res1, res2)
        # if min(res1, res2) > PLAGIARISM_METRIC:
        #     files_iso[G1_dotpath] = True
        #     files_iso[G2_dotpath] = True
        results.append((G1_sub, G2_sub, res1, res2, mn))
    results.sort(key=lambda x: x[4], reverse=True)
    printlog(problem, results)
    results.clear()
    errors.clear()
    get_all_weakly_connected_subgraphs.cache_clear()
