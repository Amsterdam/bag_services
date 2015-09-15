from collections import OrderedDict
import logging

log = logging.getLogger(__name__)


class Cache(object):
    """
    In-memory cache for all bag-data.
    """

    def __init__(self):
        self.cache = OrderedDict()

    def clear(self):
        """
        Clears the cache.
        """
        self.cache.clear()

    def put(self, obj):
        """
        Adds an object to the cache.
        """
        model = type(obj)
        pk = obj.pk
        self.cache.setdefault(model, dict())[pk] = obj

    def models(self):
        """
        Returns all the models that have been added to the cache in the order in which they were first added.
        """
        return list(self.cache.keys())

    def objects(self, model):
        """
        Returns all objects stored for a specific model.
        """
        return list(self.cache[model].values())

    def get(self, model, pk):
        """
        Returns the object with the specified PK, or None
        """
        return self.cache.get(model, dict()).get(pk)

    def flush(self, chunk_size=500):
        """
        Flush all models in the cache to the database
        """
        stored_models = self.models()

        # drop all data
        for model in reversed(stored_models):
            log.info("Dropping data from %s", model)
            model.objects.all().delete()

        # batch-insert all data
        for model in stored_models:
            log.info("Creating data for %s", model)
            values = self.objects(model)

            for i in range(0, len(values), chunk_size):
                model.objects.bulk_create(values[i:i + chunk_size])

        # clear cache
        self.cache.clear()



class AbstractCacheBasedTask(object):
    def __init__(self, cache):
        self.cache = cache

    def execute(self):
        raise NotImplementedError()

    def create(self, obj):
        self.cache.put(obj)

    def foreign_key_id(self, model, model_id):
        obj = self.cache.get(model, model_id)
        if not obj:
            return None

        return obj.pk

    def get(self, model, pk):
        return self.cache.get(model, pk)

    def merge_existing(self, model, pk, values):
        obj = self.cache.get(model, pk)
        if not obj:
            return

        for key, value in values.items():
            setattr(obj, key, value)

        self.cache.put(obj)


class FlushCacheTask(object):
    """
     1. Remove all data from the database
     2. Use batch-insert to insert all data into the database
     3. Clear the cache
    """
    name = "Flush data to database"
    chunk_size = 500

    def __init__(self, cache):
        self.cache = cache

    def execute(self):
        self.cache.flush(chunk_size=self.chunk_size)
