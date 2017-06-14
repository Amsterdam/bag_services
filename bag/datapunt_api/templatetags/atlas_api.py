import urllib.parse
import math

from django.template import Library
from django.template.loader import get_template

register = Library()

PAGE_SIZE = 10


def get_current_page(request):
    return int(request.query_params.get('page', 1)) - 1


def should_paginate(queryset):
    return queryset.count() > PAGE_SIZE


@register.filter
def api_paginate(queryset, request):
    if not should_paginate(queryset):
        return queryset.all()

    page = get_current_page(request)
    index = page * PAGE_SIZE
    offset = index + PAGE_SIZE

    return queryset[index:offset]


@register.simple_tag(takes_context=True)
def api_pagination(context, queryset):
    if not should_paginate(queryset):
        return ""

    size = queryset.count()
    max_page = math.ceil(float(size) / PAGE_SIZE)

    page = get_current_page(context.request) + 1
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < max_page else None

    next_url = update_url(context.request, next_page)
    prev_url = update_url(context.request, prev_page)
    first_url = update_url(context.request, 1)
    last_url = update_url(context.request, max_page)

    new_ctx = context.new(dict(
        current_page=page,
        previous=prev_page,
        next=next_page,
        total=max_page,
        next_url=next_url,
        prev_url=prev_url,
        first_url=first_url,
        last_url=last_url,
    ))

    return get_template("datapunt_api/pagination.html").render(new_ctx)


def update_url(url, page):
    if page is None:
        return None

    url = url.build_absolute_uri(url.get_full_path())
    url_parts = urllib.parse.urlparse(url)
    params = dict(urllib.parse.parse_qsl(url_parts.query))

    if page == 1 and 'page' in params:
        del params['page']
    else:
        params['page'] = page

    return urllib.parse.urlunparse((url_parts.scheme, url_parts.netloc, url_parts.path, url_parts.params,
                                    urllib.parse.urlencode(params), url_parts.fragment))
