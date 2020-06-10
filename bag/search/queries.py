import logging

from typing import List
from elasticsearch_dsl import Search

log = logging.getLogger(__name__)


def create_search_query(
        *,
        query: dict,
        indexes: List[str],
        sort_fields: List[str] = None,
        size: int = 15
) -> Search:
    """
    :param query: an elastic search query
    :param indexes: list of indexes to use
    :param sort_fields: an optional list of fields to use for server-side sorting
    :param size: an optional limit on size of the result set
    """
    assert indexes

    search = (
        Search()
        .index(*indexes)
        .query(query)
    )
    if sort_fields:
        search = search.sort(*sort_fields)

    return search[0:size]
