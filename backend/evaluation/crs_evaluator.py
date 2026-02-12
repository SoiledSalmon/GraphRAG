from typing import List, Dict, Callable, Any
from pydantic import BaseModel

class CRSScores(BaseModel):
    context_recall: float
    context_precision: float
    temporal_stability: float
    dependency_resolution: float
    context_decay_resistance: float
    composite_score: float
    # Debug Info
    query_entities: List[str]
    response_entities: List[str]
    context_entities: List[str]
    query_topics: List[str]
    response_topics: List[str]
    context_topics: List[str]

class CRSEvaluator:
    """
    Evaluates Context Retention Score (CRS) based on deterministic interactions
    between user query, system response, and retrieved context.
    
    Metrics:
    1. Context Recall: Proportion of context entities referenced in response.
    2. Context Precision: Proportion of response entities that come from context.
    3. Temporal Stability: Topic consistency between query+context and response.
    4. Dependency Resolution: Proportion of query entities addressed in response.
    5. Context Decay Resistance: Heuristic for maintenance of long-term context (default 1.0 for single-turn).
    """

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            "context_recall": 0.3,
            "context_precision": 0.2,
            "temporal_stability": 0.2,
            "dependency_resolution": 0.2,
            "context_decay_resistance": 0.1
        }

    def evaluate(
        self,
        query_text: str,
        response_text: str,
        context_text: str,
        extract_func: Callable[[str], Dict[str, List[str]]]
    ) -> CRSScores:
        """
        Calculates CRS sub-metrics and composite score using the provided extraction function.
        """
        # 1. Extract entities/topics
        q_ext = extract_func(query_text)
        r_ext = extract_func(response_text)
        c_ext = extract_func(context_text)

        q_ents = set(q_ext.get("entities", []))
        r_ents = set(r_ext.get("entities", []))
        c_ents = set(c_ext.get("entities", []))
        
        q_topics = set(q_ext.get("topics", []))
        r_topics = set(r_ext.get("topics", []))
        c_topics = set(c_ext.get("topics", []))

        # 2. Calculate Metrics

        # Context Recall: Entities in Response / Entities in Context
        # (Handling div-by-zero: if no context entities, recall is 1.0 if response also has none, else 0?)
        # Logic: If context has no entities, recall is N/A or perfect. Let's say 1.0 if context empty.
        if not c_ents:
            recall = 1.0
        else:
            recall = len(r_ents.intersection(c_ents)) / len(c_ents)

        # Context Precision: Entities in Response matching Context / All Entities in Response
        if not r_ents:
            precision = 1.0 # No hallucinations if no entities
        else:
            precision = len(r_ents.intersection(c_ents)) / len(r_ents)

        # Dependency Resolution: Entities in Response matching Query / All Entities in Query
        if not q_ents:
            dep_res = 1.0
        else:
            # We check if response entities cover query entities (direct addressing)
            dep_res = len(r_ents.intersection(q_ents)) / len(q_ents)

        # Temporal Stability: Topic Consistency
        # Jaccard similarity between (Query Topics + Context Topics) and Response Topics
        target_topics = q_topics.union(c_topics)
        if not target_topics and not r_topics:
            stability = 1.0
        elif not target_topics or not r_topics:
            stability = 0.0
        else:
            stability = len(r_topics.intersection(target_topics)) / len(r_topics.union(target_topics))

        # Context Decay Resistance
        # Placeholder for now as we treat this as a snapshot. 
        # Using 1.0 to indicate no detected decay in this immediate window.
        decay = 1.0 

        # 3. Composite Score
        composite = (
            recall * self.weights["context_recall"] +
            precision * self.weights["context_precision"] +
            stability * self.weights["temporal_stability"] +
            dep_res * self.weights["dependency_resolution"] +
            decay * self.weights["context_decay_resistance"]
        )

        return CRSScores(
            context_recall=round(recall, 3),
            context_precision=round(precision, 3),
            temporal_stability=round(stability, 3),
            dependency_resolution=round(dep_res, 3),
            context_decay_resistance=round(decay, 3),
            composite_score=round(composite, 3),
            query_entities=list(q_ents),
            response_entities=list(r_ents),
            context_entities=list(c_ents),
            query_topics=list(q_topics),
            response_topics=list(r_topics),
            context_topics=list(c_topics)
        )
