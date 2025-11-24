def convert_knowledge_graph_to_dict_format(kg_result) -> dict:
    """Convert knowledge graph from list format to dict format with node/edge IDs
    
    Converts:
        nodes: [{'name': '...'}, {'name': '...'}]
        edges: [{'source': '...', 'target': '...', 'label': '...'}]
    
    To:
        nodes: {
            'node1': {'name': '...'},
            'node2': {'name': '...'}
        }
        edges: {
            'edge1': {'source': 'node1', 'target': 'node2', 'label': '...'}
        }
    """
    # Create name to node_id mapping from nodes
    name_to_node_id = {}
    nodes_dict = {}
    
    for idx, node in enumerate(kg_result.nodes, 1):
        node_id = f"node{idx}"
        node_name = node.name
        nodes_dict[node_id] = {"name": node_name}
        name_to_node_id[node_name] = node_id
    
    # Convert edges using the name to node_id mapping
    edges_dict = {}
    for idx, edge in enumerate(kg_result.edges, 1):
        edge_id = f"edge{idx}"
        source_id = name_to_node_id.get(edge.source, edge.source)
        target_id = name_to_node_id.get(edge.target, edge.target)
        edges_dict[edge_id] = {
            "source": source_id,
            "target": target_id,
            "label": edge.label
        }
    
    return {
        "nodes": nodes_dict,
        "edges": edges_dict
    }
