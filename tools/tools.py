from langchain_core.tools import tool
from rag_retailbanking_team8.core.db import get_retailbankingvector_store
import requests
import psycopg
from psycopg.rows import dict_row
import os
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s -  %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


_raw_conn = os.getenv("PG_CONNECTION_STRING_FTS")


@tool
def search_vector(query: str, k: int, collection_name: str):
    """perform search using vector embeddings"""

    if not query:
        logger.warning("Empty query provided.")
        return []

    if not collection_name:
        logger.warning("Empty collection_name provided.")
        return []

    if not isinstance(k, int) or k <= 0:
        logger.error("Invalid parameter k, must be a positive integer")
        return []

    try:
        logger.info("Running vector search...")

        vector_store = get_retailbankingvector_store(collection_name)

        docs = vector_store.similarity_search(query, k)

        output = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
            for doc in docs
        ]

        return output
    except Exception as e:
        logger.error(f"Error occured during vector search: {e}")
        return []


@tool
def search_fts(query: str, k: int, collection_name: str):
    """Keyword search against the stored chunks using Postgres' tsvector/tsquery/ts_rank"""
    if not query:
        logger.warning("Empty query provided.")
        return []

    if not collection_name:
        logger.warning("Empty collection_name provided.")
        return []

    if not isinstance(k, int) or k <= 0:
        logger.error("Invalid parameter k, must be a positive integer")
        return []

    logger.info("Running FTS Search...")

    try:
        sql = """
        SELECT
            e.document                                               AS content,
            e.cmetadata                                              AS metadata,
            ts_rank(
                to_tsvector('english', e.document),
                plainto_tsquery('english', %(query)s)
            )                                                        AS fts_rank
        FROM  langchain_pg_embedding  e
        JOIN  langchain_pg_collection c ON c.uuid = e.collection_id
        WHERE c.name = %(collection)s
            AND to_tsvector('english', e.document)
                @@ plainto_tsquery('english', %(query)s)
        ORDER BY fts_rank DESC
        LIMIT %(k)s;
    """

        try:
            with psycopg.connect(_raw_conn, row_factory=dict_row) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        sql, {"query": query, "collection": collection_name, "k": k}
                    )
                    rows = cur.fetchall()

            output = [
                {
                    "content": row["content"],
                    "metadata": row["metadata"],
                    "fts_rank": round(float(row["fts_rank"]), 4),
                }
                for row in rows
            ]
        except Exception as e:
            logger.error("Database extraction failure during FTS search.")
            output = []

        return output

    except Exception as e:
        logger.error(f"Error occured during FTS search: {e}")
        return []


@tool
def search_hybrid(query: str, k: int, collection_name: str):
    """Merge vector and fts results using RRF (Reciprocal Rank Fusion)
    Chunks appearing in both search results will rank higher than those in only one
    The constant 60 prevents top-ranked outputs from dominating
    How RRF scores for a chunk = sum of 1/(rank + 60)
    """
    if not query:
        logger.warning("Empty query provided.")
        return []

    if not collection_name:
        logger.warning("Empty collection_name provided.")
        return []

    if not isinstance(k, int) or k <= 0:
        logger.error("Invalid parameter k, must be a positive integer")
        return []

    logger.info("Running Hybrid Search...")

    try:
        try:
            vector_search_results = search_vector.func(
                query=query, k=5, collection_name=collection_name
            )
        except Exception as e:
            logger.error("In hybrid search tool - vector search failed {e} ")

        try:
            fts_results = search_fts.func(
                query=query, k=5, collection_name=collection_name
            )
        except Exception as e:
            logger.error("In hybrid search tool - fts search failed {e} ")

        rrf_scores: dict[str, float] = {}
        chunk_map: dict[str, dict] = {}

        # Walk the vector results in ranked order (best match first).
        # enumerate gives rank 0, 1, 2... so we add +1 below to make ranks start at 1.
        for rank, doc in enumerate(vector_search_results):
            # Use the first 120 chars of the chunk text as an identity key.
            # Same chunk retrieved by both searches -> same key -> its scores add up.
            key = doc["content"][:120]
            # RRF formula: score += 1 / (k_constant + rank). Better rank (smaller number)
            # gives a bigger score. .get(key, 0) lets us accumulate across both loops.
            rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (60 + rank + 1)
            # Remember the full chunk so we can rebuild the final list from the winning keys.
            chunk_map[key] = {"content": doc["content"], "metadata": doc["metadata"]}

        # Same pass over the FTS results. A chunk found by BOTH searches gets scored
        # twice here, which is exactly how RRF rewards agreement between the two methods.
        for rank, item in enumerate(fts_results):
            key = item["content"][:120]
            rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (60 + rank + 1)
            chunk_map[key] = {"content": item["content"], "metadata": item["metadata"]}

        # this line sorts the results of our RRF calculation so that
        # the higher scoring doc/chunk appear at the very top of the final list
        ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        # print(ranked)
        return [chunk_map[key] for key, _ in ranked[:k]]
    except Exception as e:
        logger.error(f"Error occured during hybrid search: {e}")
        return []
