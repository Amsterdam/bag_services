import logging

log = logging.getLogger(__name__)


class AbstractOrmTask(object):
    """
    Basic batch task for working with Django ORM.
    """

    def __init__(self):
        self.cache = dict()
        self.to_create = []

    def execute(self):
        raise NotImplementedError()

    def create(self, obj):
        self.to_create.append(obj)

    def flush(self, batch_size=300):
        if not self.to_create:
            return

        model = self.to_create[0].__class__

        def chunks():
            for i in range(0, len(self.to_create), batch_size):
                yield self.to_create[i:i + batch_size]

        for chunk in chunks():
            model.objects.bulk_create(chunk)

        self.to_create.clear()

    def tear_down(self):
        self.flush()
        self.cache.clear()

    def merge(self, model, pk, values):
        model.objects.update_or_create(pk=pk, defaults=values)

    def merge_existing(self, model, pk, values):
        model.objects.filter(pk=pk).update(**values)

    def foreign_key_id(self, model, model_id):
        """
        Returns `model_id` if `model_id` identifies a valid instance of `model`; returns None otherwise.
        """
        if not model_id:
            return None

        key = str(model)
        id_set = self.cache.get(key, None)

        if id_set is None:
            id_set = set(model.objects.values_list('pk', flat=True))
            self.cache[key] = id_set

        if model_id not in id_set:
            log.warning("Reference to non-existing object of type %s with key %s", model, model_id)
            return None

        return model_id


