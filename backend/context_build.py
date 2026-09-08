def build_context(graph_data: list, chunks: list) -> str:
    if not graph_data and not chunks:
        return "No relevant information found in the graph or documents."

    parts = []

    if graph_data:
        graph_section = "Knowledge Graph Information:\n"

        for item in graph_data:
            source = item["source"]
            relation = item.get("relation") or "RELATED_TO"
            target = item["target"]

            graph_section += f"- {source} {relation} {target}\n"

        parts.append(graph_section)

    if chunks:
        chunk_section = "Relevant Document Passages:\n"

        for c in chunks:
            chunk_section += f"- {c['text']}\n"

        parts.append(chunk_section)

    return "\n".join(parts)










 

 






















 