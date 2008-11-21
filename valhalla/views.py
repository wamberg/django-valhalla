from django import http
from django.core import paginator
from django.core import serializers

from valhalla import models as valhalla_models


def deed_list(request):
    """
    Return a json list of deeds.
    """
    # parse the amount of deeds requested per page
    per_page_request = request.GET.get('per', '20')
    try:
        per_page = int(per_page_request)
    except ValueError:
        raise http.Http404

    # create a deed paginator
    deeds = valhalla_models.Deed.objects.all()
    deed_paginator = paginator.Paginator(deeds,
            per_page, allow_empty_first_page=True)

    # parse the requested page number
    page = request.GET.get('p', '1')
    try:
        page_number = int(page)
    except ValueError:
        if page == 'last':
            page_number = deed_paginator.num_pages
        else:
            raise http.Http404

    # get the page of Deed objects if it exists
    try:
        deed_page = deed_paginator.page(page_number)
    except paginator.InvalidPage:
        raise http.Http404

    # return the requested Deed objects as a json list
    json_deed_list = serializers.serialize('json', deed_page.object_list)
    return http.HttpResponse(json_deed_list, mimetype='application/json')


def deed_detail(request):
    pass
