"""
==================================================
 Individual search queries for external systems
--------------------------------------------------
 Each of these functions builds a query and,
 if needed an aggregation as well.
 They all return a dict with the Q and A keyes
==================================================
"""
# Python
# Packages
# from elasticsearch_dsl import Search, Q, A

import logging

import typing as typing
from elasticsearch_dsl import Search

log = logging.getLogger(__name__)


class ElasticQueryWrapper(object):
    """
    Wrapper object for dynamically constructing elastic search queries.
    """

    def __init__(self,
                 query: typing.Optional[dict],
                 sort_fields: [str] = None,
                 indexes: [str] = None,
                 size: int = None,
                 custom_sort_function: typing.Callable = None
                 ):
        """
        :param query: an elastic search query
        :param sort_fields: an optional list of fields to use for server-side sorting
        :param indexes: an optional list of indexes to use

        :param size: an optional limit on size of the result set
        :param custom_sort_function: an optional function to use for client-side sorting
        """
        self.query = query
        self.sort_fields = sort_fields
        self.indexes = indexes
        self.size = size
        self.custom_sort_function = custom_sort_function

    def to_elasticsearch_object(self, client) -> Search:
        assert self.indexes

        search = (
            Search()
                .using(client)
                .index(*self.indexes)
                .query(self.query)
        )
        if self.sort_fields:
            search = search.sort(*self.sort_fields)

        size = 15  # default size
        if self.size:
            size = self.size

        search = search[0:size]

        return search
