# Python
from collections import OrderedDict
import json
# Packages
from rest_framework import renderers, serializers
from rest_framework import pagination, response, viewsets, filters
from rest_framework.reverse import reverse
from rest_framework.utils.urls import replace_query_param
from rest_framework_extensions.mixins import DetailSerializerMixin

DEFAULT_RENDERERS = (renderers.JSONRenderer, renderers.BrowsableAPIRenderer)
FORMATS = [dict(format=r.format, type=r.media_type) for r in DEFAULT_RENDERERS]


def get_links(view_name, kwargs=None, request=None):

    result = OrderedDict([
        ('self', dict(
            href=reverse(view_name, kwargs=kwargs, request=request)
        ))
    ])

    return result


class DataSetSerializerMixin(object):
    def to_representation(self, obj):
        result = super().to_representation(obj)
        result['dataset'] = self.dataset
        return result


class LinksField(serializers.HyperlinkedIdentityField):

    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def to_representation(self, value):
        request = self.context.get('request')

        result = OrderedDict(
            [
                ('self', {
                    'href': self.get_url(value, self.view_name, request, None)
                }),
            ]
        )

        return result

    def get_url(self, obj, view_name, request, _format):
        """
        Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        if hasattr(obj, 'landelijk_id'):
            self.lookup_field = 'landelijk_id'

        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_url_kwarg: lookup_value}
        return self.reverse(
            view_name, kwargs=kwargs, request=request, format=_format)


class HALSerializer(serializers.HyperlinkedModelSerializer):
    """
    Use landelijk ids if possible
    """
    url_field_name = '_links'
    serializer_url_field = LinksField

    def get_url(self, obj, view_name, request, _format):

        landelijk_id = getattr(obj, 'landelijk_id', None)
        obj_pk = obj.pk

        # prefer landeljk id usage
        if landelijk_id:
            obj_pk = landelijk_id

        url_kwargs = {
            'pk': obj_pk
        }

        return reverse(
            view_name, kwargs=url_kwargs, request=request, format=_format)


class HALPagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        self_link = self.request.build_absolute_uri()
        if self_link.endswith(".api"):
            self_link = self_link[:-4]

        if self.page.has_next():
            next_link = replace_query_param(
                self_link, self.page_query_param, self.page.next_page_number())
        else:
            next_link = None

        if self.page.has_previous():
            prev_link = replace_query_param(
                self_link, self.page_query_param,
                self.page.previous_page_number())
        else:
            prev_link = None

        return response.Response(OrderedDict([
            ('_links', OrderedDict([
                ('self', dict(href=self_link)),
                ('next', dict(href=next_link)),
                ('previous', dict(href=prev_link)),
            ])),
            ('count', self.page.paginator.count),
            ('results', data)
        ]))


class LimitedHALPagination(HALPagination):
    max_page_size = 5
    page_size = 5


class DatapuntViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):

    renderer_classes = DEFAULT_RENDERERS
    pagination_class = HALPagination
    filter_backends = (filters.DjangoFilterBackend,)

    # default ordering
    ordering = ('id',)


class RelatedSummaryField(serializers.Field):

    def to_representation(self, value):
        count = value.count()

        model_name = value.model.__name__
        mapping = model_name.lower() + "-list"
        url = reverse(mapping, request=self.context['request'])

        landelijk_id = getattr(value.instance, 'landelijk_id', None)
        parent_pk = value.instance.pk

        filter_name = list(value.core_filters.keys())[0]

        # prefer landeljk id usage
        if landelijk_id:
            # if not filter_name.endswith('__id'):
            parent_pk = landelijk_id

        return {
            'count': count,
            'href': "{}?{}={}".format(
                url, filter_name, parent_pk),
        }


class AdresFilterField(serializers.Field):
    """
    For obj get link to addresses
    """

    def get_attribute(self, obj):
        return obj

    def to_representation(self, obj):

        model_name = obj.__class__.__name__
        filterkey = model_name.lower()

        url = reverse(
            'nummeraanduiding-list', request=self.context['request'])

        if hasattr(obj, 'landelijk_id'):
            landelijk_id = obj.landelijk_id
        else:
            landelijk_id = obj.id

        return {
            'href': '{}?{}={}'.format(
                url, filterkey, landelijk_id)
        }


class DisplayField(serializers.Field):

    def __init__(self, *args, **kwargs):
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        return str(value)


class MultipleGeometryField(serializers.Field):

    read_only = True

    def get_attribute(self, obj):
        # Checking if point geometry exists. If not returning the
        # regular multipoly geometry
        return obj.point_geom or obj.poly_geom

    def to_representation(self, value):
        # Serilaize the GeoField. Value could be either None,
        # Point or MultiPoly
        res = ''
        if value:
            res = json.loads(value.geojson)
        return res


class DistanceGeometryField(serializers.Field):
    """
    A geometry field that represents distance. It expects the
    value to be of type Distance
    https://docs.djangoproject.com/en/1.10/ref/contrib/gis/measure/#django.contrib.gis.measure.Distance
    """
    read_only = True
    source = 'afstand'
    unit = 'm'

    def __init__(self, *args, **kwargs):
        """
        Allow overwriting of the unit
        """
        self.unit = kwargs.get('unit', self.unit)
        super(DistanceGeometryField, self).__init__(*args, **kwargs)

    def get_attribute(self, obj):
        # If there is no distance returning None
        return getattr(obj, self.source, None)

    def to_representation(self, value):
        try:
            return getattr(value, 'm')
        except AttributeError:
            return None
