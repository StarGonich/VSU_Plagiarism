import argparse
import logging
import glob
from collections import defaultdict

import networkx as nx

import pruner
import pruner.langs
import pruner.predicates
import utils
import visualization

logger = logging.getLogger(__name__)


def read_dot_files(ast_files, cfg_files, pdg_files) -> dict[str, list[nx.Graph]]:
    """
    Read multiple .dot files and return a list of graphs.

    Args:
        ast_files (list): List of AST .dot file paths
        cfg_files (list): List of CFG .dot file paths
        pdg_files (list): List of PDG .dot file paths

    Returns:
        list: List of graphs read from the .dot files
    """
    input_graphs = defaultdict(list)
    for graph_type, files in zip(
        ["ast", "cfg", "pdg"], [ast_files, cfg_files, pdg_files]
    ):
        if files is not None:
            for file_path in files:
                graph = utils.read_dot_file(file_path)
                input_graphs[graph_type].append(graph)
    return input_graphs


def add_edge_label(input_graphs):
    # we add labels to the edges to make them identifiable
    for graph in input_graphs["ast"]:
        for u, v, k, data in graph.edges(keys=True, data=True):
            data["label"] = "AST"

    for graph in input_graphs["cfg"]:
        for u, v, k, data in graph.edges(keys=True, data=True):
            data["label"] = "CFG"

    # we ignore the edges in the pdg graphs, as they are already labeled

    return input_graphs


def merge_graphs(input_graphs):
    ast_graph = nx.DiGraph()
    for graph in input_graphs["ast"]:
        ast_graph.update(graph)
    cfg_graph = nx.DiGraph()
    for graph in input_graphs["cfg"]:
        cfg_graph.update(graph)
    pdg_graph = nx.MultiDiGraph()
    for graph in input_graphs["pdg"]:
        pdg_graph.update(graph)
    # Merge the graphs into a single graph
    merged_graph = nx.MultiDiGraph()
    merged_graph.update(ast_graph)
    merged_graph.update(cfg_graph)
    merged_graph.update(pdg_graph)
    return merged_graph


def add_call_edges(merged_graph, ref_graph):
    for u, v, k, data in ref_graph.edges(keys=True, data=True):
        if data["label"] == "CALL":
            # If method not explicitly implemented, the "artifact" node only presents in AST graph.
            # If we not import AST graph, the call edge should be ignored.
            if merged_graph.has_node(u) and merged_graph.has_node(v):
                merged_graph.add_edge(u, v, **data)

    return merged_graph


def copy_node_data(merged_graph, ref_graph):
    for node in merged_graph.nodes():
        if node in ref_graph.nodes.keys():
            ref_data = ref_graph.nodes[node]
            merged_graph.nodes[node].update(ref_data)
        else:
            logger.warning(f"Node {node} not found in reference graph")
    return merged_graph


def main():
    parser = argparse.ArgumentParser(
        description="Merge multiple Graphviz .dot files into a single graph."
    )
    parser.add_argument("--ast", nargs="+", help="Paths to the AST .dot files")
    parser.add_argument("--cfg", nargs="+", help="Paths to the CFG .dot files")
    parser.add_argument("--pdg", nargs="+", help="Paths to the PDG .dot files")
    parser.add_argument("--ref", help="Path to the reference .dot file")
    parser.add_argument(
        "--lang", choices=["py", "java", "cpp"], help="Language of the input files"
    )
    parser.add_argument(
        "--raw", action="store_true", help="disable pretty label and colorization"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="./out/merged.dot",
        help="Path to the output .dot file (default: merged.dot)",
    )

    args = parser.parse_args()
    utils.setup_logging(args.verbose)

    pdg_files = []
    for pattern in args.pdg:
        pdg_files.extend(glob.glob(pattern))
    input_graphs = read_dot_files(args.ast, args.cfg, pdg_files)
    refer_graph: nx.Graph = utils.read_dot_file(args.ref)

    # input_graphs = add_edge_label(input_graphs)

    merged_graph = merge_graphs(input_graphs)
    merged_graph = copy_node_data(merged_graph, refer_graph)
    merged_graph = add_call_edges(merged_graph, refer_graph)

    graph_pruner = pruner.GraphPruner(merged_graph)

    if args.lang == "py":
        if args.ast is None:
            graph_pruner.add_prune_function(
                pruner.langs.python.remove_artifact_nodes_without_ast
            )
        else:
            graph_pruner.add_prune_function(
                pruner.langs.python.remove_artifact_nodes_with_ast
            )
    elif args.lang == "cpp":
        graph_pruner.add_prune_function(pruner.langs.cpp.remove_global_import)

    graph_pruner.add_edge_predicate(pruner.predicates.edges.null_ddg)
    graph_pruner.add_edge_predicate(pruner.predicates.edges.cdg)

    # graph_pruner.add_node_predicate(pruner.predicates.nodes.ast_leaves)
    graph_pruner.add_node_predicate(
        pruner.predicates.nodes.is_method_implicitly_defined
    )
    graph_pruner.add_node_predicate(pruner.predicates.nodes.operator_fieldaccess)

    graph_pruner.prune()
    graph_pruner.remove_isolated_nodes()

    # if not args.ast:
    #     utils.add_virtual_root(merged_graph)

    merged_graph.name = f"Merged {args.lang} Graph"

    if not args.raw:
        visualization.pretty_graph(merged_graph)
    utils.write_dot_file(merged_graph, f"{args.output}")


if __name__ == "__main__":
    main()
