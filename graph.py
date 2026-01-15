from neo4j import GraphDatabase
from datetime import datetime

class GraphMemory:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(
            uri,
            auth = (username, password)
        )

    def close(self):
        self.driver.close()

    def get_or_create_user(self, user_id):
        query = """"
            MERGE (u:User {id: $user_id})
            RETURN u
        """
        with self.driver.session() as session:
            session.run(query, user_id=user_id)

    def create_event(self, event_type):
        query = """
        CREATE (e:Event {
            type: $event_type,
            timestamp: $timestamp
        })
        RETURN e
        """
        with self.driver.session() as session:
            result = session.run(
                query,
                event_type=event_type,
                timestamp=datetime.utcnow().isoformat()
            )
            return result.single()["e"]
        
    def get_or_create_entity(self, entity_name):
        query = """
        MERGE (e:Entity {name: $name})
        RETURN e
        """
        with self.driver.session() as session:
            session.run(query, name=entity_name)

    def get_or_create_topic(self, topic_name):
        query = """
        MERGE (t:Topic {name: $name})
        RETURN t
        """
        with self.driver.session() as session:
            session.run(query, name=topic_name)

    def link_event_entity(self, event_id, entity_name):
        query = """
        MATCH (e:Event) WHERE id(e) = $event_id
        MATCH (en:Entity {name: $entity_name})
        MERGE (e)-[:MENTIONS]->(en)
        """
        with self.driver.session() as session:
            session.run(
                query,
                event_id=event_id,
                entity_name=entity_name
            )

    def link_event_topic(self, event_id, topic_name):
        query = """
        MATCH (e:Event) WHERE id(e) = $event_id
        MATCH (t:Topic {name: $topic_name})
        MERGE (e)-[:ASKED_ABOUT]->(t)
        """
        with self.driver.session() as session:
            session.run(
                query,
                event_id=event_id,
                topic_name=topic_name
            )
    
    def link_previous_event(self, current_event_id, previous_event_id):
        if previous_event_id is None:
            return

        query = """
        MATCH (curr:Event) WHERE id(curr) = $curr_id
        MATCH (prev:Event) WHERE id(prev) = $prev_id
        MERGE (curr)-[:PREVIOUS_CONTEXT]->(prev)
        """
        with self.driver.session() as session:
            session.run(
                query,
                curr_id=current_event_id,
                prev_id=previous_event_id
            )

    def store_interaction(
        self,
        user_id,
        event_type,
        entities,
        topics,
        previous_event_id=None
    ):
        self.get_or_create_user(user_id)

        event = self.create_event(event_type)
        event_id = event.id

        self.link_user_event(user_id, event_id)

        for entity in entities:
            self.get_or_create_entity(entity)
            self.link_event_entity(event_id, entity)

        for topic in topics:
            self.get_or_create_topic(topic)
            self.link_event_topic(event_id, topic)

        self.link_previous_event(event_id, previous_event_id)

        return event_id