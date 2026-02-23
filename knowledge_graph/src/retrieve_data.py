import time
import sys
from pathlib import Path

# Add parent directory to path so we can import common
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.models import get_embeddings
from common.logger import get_logger
from classifier.src.classifier import classify_hotpot_vocab
from agents.prompts.hotpot_examples import react_examples
from knowledge_graph.cyphers.crud_cyphers import retrieve_cypher

logger = get_logger(__name__)


def retrieve_memories(query, session):
    """
    Retrieve relevant memories/experiences from the knowledge graph based on a query.
    
    Args:
        query: The input question/query string
        id: Session or context ID
        session: Neo4j session object for executing Cypher queries
    
    Returns:
        str: Formatted string of example traces (separated by "---")
    """
    embeddings = get_embeddings()
    
    # Classify the query to extract intent, attributes, and entities
    vocab = classify_hotpot_vocab(query)
    logger.debug(f"Query vocab: {vocab}")
    
    # Embed the query
    query_embed = embeddings.embed_query(query)
    
    # Prepare parameters for Cypher query
    params = {
        "query_embedding": query_embed,
        "intent": vocab.get("intent"),
        "attributes": vocab.get("attributes", []),
        "entities": vocab.get("entities", [])
    }
    
    # Execute the retrieval query
    start = time.perf_counter()
    result = session.run(retrieve_cypher, **params)
    end = time.perf_counter()
    logger.info(f"Cypher retrieval took: {end - start:.4f}s")
    
    # Extract traces from results
    experiences = [record["node"].get("trace") for record in result]
    logger.info(f"Retrieved {len(experiences)} experiences from knowledge graph")
    
    # Pad with react examples if we have fewer than 3 experiences
    if len(experiences) < 3:
        padding_count = 3 - len(experiences)
        experiences.extend(react_examples[:padding_count])
        logger.info(f"Padded with {padding_count} examples from react_examples")
    return experiences
