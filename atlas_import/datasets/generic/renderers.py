from django.template import loader, RequestContext
from rest_framework import renderers

__author__ = 'yigalduppen'


class HTMLDetailRenderer(renderers.BaseRenderer):
    format = 'html'
    media_type = 'text/html+detail'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        view = renderer_context['view']
        request = renderer_context['request']

        obj = view.get_object()
        tmpl = loader.get_template(view.template_name)
        ctx = RequestContext(request, dict(data=data, object=obj))
        return tmpl.render(ctx)

DEFAULT_RENDERERS = (renderers.JSONRenderer, renderers.BrowsableAPIRenderer, HTMLDetailRenderer)


