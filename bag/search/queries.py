import logging

from typing import List
from elasticsearch_dsl import Search

log = logging.getLogger(__name__)


def create_search_query(
        *,
        query: dict,
        indexes: List[str],
        sort_fields: List[str] = None,
        size: int = 15,
        search_type = None,
) -> Search:
    """
    :param query: an elastic search query
    :param indexes: list of indexes to use
    :param sort_fields: an optional list of fields to use for server-side sorting
    :param size: an optional limit on size of the result set
    :param search_type: search_type to be passed. For example dfs_query_then_fetch. See :
      https://www.elastic.co/guide/en/elasticsearch/reference/master/search-request-body.html#dfs-query-then-fetch
    """
    assert indexes

    search = (
        Search()
        .index(*indexes)
        .query(query)
    )
    if search_type:
        search = search.params(search_type=search_type)
    if sort_fields:
        search = search.sort(*sort_fields)

    return search[0:size]
