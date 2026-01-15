from neo4j import GraphDatabase

class GraphRetriever:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(username, password)
        )

    def close(self):
        self.driver.close()
    
    def retrieve_context(
        self,
        user_id,
        entities,
        topics,
        max_events=5
    ):
        entity_context = self._retrieve_by_entities(
            user_id, entities, max_events
        )
        topic_context = self._retrieve_by_topics(
            user_id, topics, max_events
        )

        return self._merge_contexts(entity_context, topic_context)
    
    def _retrieve_by_entities(self, user_id, entities, max_events):
        if not entities:
            return []

        query = """
        MATCH (u:User {id: $user_id})-[:ASKED_ABOUT]->(e:Event)
              -[:MENTIONS]->(en:Entity)
        WHERE en.name IN $entities
        RETURN e.type AS type, e.timestamp AS timestamp, en.name AS entity
        ORDER BY e.timestamp DESC
        LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(
                query,
                user_id=user_id,
                entities=entities,
                limit=max_events
            )
            return [record.data() for record in result]
        
    def _retrieve_by_topics(self, user_id, topics, max_events):
        if not topics:
            return []

        query = """
        MATCH (u:User {id: $user_id})-[:ASKED_ABOUT]->(e:Event)
              -[:ASKED_ABOUT]->(t:Topic)
        WHERE t.name IN $topics
        RETURN e.type AS type, e.timestamp AS timestamp, t.name AS topic
        ORDER BY e.timestamp DESC
        LIMIT $limit
        """

        with self.driver.session() as session:
            result = session.run(
                query,
                user_id=user_id,
                topics=topics,
                limit=max_events
            )
            return [record.data() for record in result]
        
    def _merge_contexts(self, entity_ctx, topic_ctx):
        seen = set()
        merged = []

        for item in entity_ctx + topic_ctx:
            key = (item["type"], item["timestamp"])
            if key not in seen:
                seen.add(key)
                merged.append(item)

        return {
            "past_events": merged,
            "entity_count": len(entity_ctx),
            "topic_count": len(topic_ctx)
        }
