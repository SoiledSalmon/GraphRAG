import spacy

# Load the spaCy model
# Note: Ensure 'en_core_web_sm' is installed in the environment
nlp = spacy.load("en_core_web_sm")

def extract_entities(text: str) -> dict:
    """
    Extracts named entities from text using spaCy and identifies topics based on predefined keyword rules.
    """
    doc = nlp(text)
    
    # Extract entity text strings and remove duplicates
    entities = list(set(ent.text for ent in doc.ents))
    
    # Lightweight topic mapping using simple keyword rules
    topics = []
    lower_text = text.lower()
    
    # Keywords for LLMs topic
    if any(kw in lower_text for kw in ["llm", "gpt", "transformer", "language model"]):
        topics.append("LLMs")
    
    # Keywords for RAG topic
    if any(kw in lower_text for kw in ["rag", "retrieval", "vector store"]):
        topics.append("RAG")
    
    # Keywords for Knowledge Graphs topic
    if any(kw in lower_text for kw in ["graph", "node", "edge", "triplet"]):
        topics.append("Knowledge Graphs")
    
    return {
        "entities": entities,
        "topics": topics
    }