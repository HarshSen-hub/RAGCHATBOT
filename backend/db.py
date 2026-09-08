from neo4j import GraphDatabase
from .config import NEO4J_URI, NEO4J_ID, NEO4J_PASSWORD

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_ID, NEO4J_PASSWORD))


def close_driver():
    driver.close()


def clear_database():
    """Wipes all nodes/relationships. Useful for testing/reingesting."""
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
