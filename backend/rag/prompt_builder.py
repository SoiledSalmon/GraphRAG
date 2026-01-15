"""
This module is responsible for constructing natural language prompts for the LLM
based on context retrieved from the knowledge graph and the user's current query.
It acts as a translation layer between structured retrieval data and the text generation model.
"""

from typing import Dict, Any

def build_prompt(context: Dict[str, Any], query: str) -> str:
    """
    Constructs a prompt for the LLM by combining the retrieved context and the user's query.

    Args:
        context (dict): A dictionary containing retrieval results, expected to match the format:
            {
                "past_events": [
                    {"type": "USER_QUERY", "timestamp": "...", "entity": "string"},
                    ...
                ],
                "entity_count": int,
                "topic_count": int
            }
        query (str): The raw input query from the user.

    Returns:
        str: A formatted natural language string suitable for direct input to an LLM.
    """
    sections = []

    # Process Memory Context
    memory_lines = []
    
    past_events = context.get("past_events", [])
    if past_events:
        for event in past_events:
            entity = event.get("entity")
            if entity:
                # Format: "Previously, the user mentioned the entity 'Neo4j' in a query."
                memory_lines.append(f"- Previously, the user mentioned the entity \"{entity}\" in a query.")

    entity_count = context.get("entity_count", 0)
    topic_count = context.get("topic_count", 0)
    
    if entity_count > 0 or topic_count > 0:
        count_summary = "- The conversation includes"
        parts = []
        if entity_count > 0:
            parts.append(f"{entity_count} distinct entities")
        if topic_count > 0:
            parts.append(f"{topic_count} topics")
        
        count_summary += " " + " and ".join(parts) + "."
        memory_lines.append(count_summary)

    if memory_lines:
        sections.append("Memory Context:")
        sections.extend(memory_lines)
        sections.append("") # Add spacing

    # Process User Query
    sections.append("User Query:")
    sections.append(query)

    return "\n".join(sections)
