from collections import OrderedDict

from django.template import RequestContext, loader
from rest_framework import renderers, serializers, pagination, response, viewsets
from rest_framework.reverse import reverse
from rest_framework.utils.urls import replace_query_param
from rest_framework_extensions.mixins import DetailSerializerMixin


class HTMLDetailRenderer(renderers.BaseRenderer):
    format = 'html'
    media_type = 'text/html'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        view = renderer_context['view']
        request = renderer_context['request']

        obj = view.get_object()
        tmpl = loader.get_template(view.template_name)
        ctx = RequestContext(request, dict(data=data, object=obj))
        return tmpl.render(ctx)


DEFAULT_RENDERERS = (renderers.JSONRenderer, renderers.BrowsableAPIRenderer, HTMLDetailRenderer)
FORMATS = [dict(format=r.format, type=r.media_type) for r in DEFAULT_RENDERERS]


def get_links(view_name, kwargs=None, request=None):
    result = OrderedDict([
        ('self', dict(
            href=reverse(view_name, kwargs=kwargs, request=request)
        ))
    ])
    for f in FORMATS:
        result[f['type']] = dict(
            href=reverse(view_name, kwargs=kwargs, request=request, format=f['format'])
        )

    return result


class DataSetSerializerMixin(object):
    def to_representation(self, obj):
        result = super().to_representation(obj)
        result['dataset'] = self.dataset
        return result


class LinksField(serializers.HyperlinkedIdentityField):
    def to_representation(self, value):
        request = self.context.get('request')

        result = OrderedDict([
            ('self', dict(
                href=self.get_url(value, self.view_name, request, None))
             ),
        ])

        for f in FORMATS:
            result[f['type']] = dict(
                href=self.get_url(value, self.view_name, request, f['format'])
            )

        return result


class HALSerializer(serializers.HyperlinkedModelSerializer):
    url_field_name = '_links'
    serializer_url_field = LinksField


class HALPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        self_link = self.request.build_absolute_uri()
        if self_link.endswith(".api"):
            self_link = self_link[:-4]

        if self.page.has_next():
            next_link = replace_query_param(self_link, self.page_query_param, self.page.next_page_number())
        else:
            next_link = None

        if self.page.has_previous():
            prev_link = replace_query_param(self_link, self.page_query_param, self.page.previous_page_number())
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


class AtlasViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    renderer_classes = DEFAULT_RENDERERS
    pagination_class = HALPagination
