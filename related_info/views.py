# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import Context
from django.shortcuts import render_to_response, redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from tardis.tardis_portal.auth import decorators as authz
from tardis.tardis_portal.creativecommonshandler import CreativeCommonsHandler
from tardis.tardis_portal.models import Experiment, ExperimentParameter
from tardis.tardis_portal.shortcuts import render_response_index


from . import forms
from .related_info import RelatedInfoHandler

import logging
logger = logging.getLogger(__name__)

auxiliary_schema_namespace = 'http://www.tardis.edu.au/schemas/experiment/annotation/2011/07/07'

def _redirect(experiment_id):
    return redirect(reverse('tardis.tardis_portal.views.view_experiment', args=[experiment_id]))


@never_cache
@authz.experiment_access_required
def index(request, experiment_id):
    url = 'related_info/index.html'
    c = Context()
    if request.user.is_authenticated():
        c['has_write_permissions'] = authz.has_write_permissions(request, experiment_id)

    rih = RelatedInfoHandler(experiment_id)
    c['related_uris'] = rih.uris()
    c['related_publications'] = rih.publications()
    c['experiment_id'] = int(experiment_id)

    c['other_info'] = ExperimentParameter.objects.filter(name__schema__namespace=auxiliary_schema_namespace, parameterset__experiment=experiment_id)

    uris = RelatedInfoHandler(experiment_id)

    return HttpResponse(render_response_index(request, url, c))

@authz.write_permissions_required
def add_uri(request, experiment_id):
    url = 'related_info/add_uri.html'
    c = Context()
    if request.POST:
        form = forms.RelatedUriForm(request.POST)
        if form.is_valid():
            RelatedInfoHandler(experiment_id).add_uri(form.cleaned_data)
            return _redirect(experiment_id)
    else:
        form = forms.RelatedUriForm()
    c['url'] = reverse('tardis.apps.related_info.views.add_uri', args=[experiment_id])
    c['form'] = form
    return HttpResponse(render_response_index(request, url, c))
    

@authz.write_permissions_required
def add_publication(request, experiment_id):
    url = 'related_info/add_publication.html'
    c = Context()
    if request.POST:
        form = forms.RelatedPublicationForm(request.POST)
        if form.is_valid():
            RelatedInfoHandler(experiment_id).add_publication(form.cleaned_data)
            return _redirect(experiment_id)
    else:
        form = forms.RelatedPublicationForm()
    c['url'] = reverse('tardis.apps.related_info.views.add_publication', args=[experiment_id])
    c['form'] = form
    return HttpResponse(render_response_index(request, url, c))

@authz.write_permissions_required
def edit_uri(request, experiment_id, parameterset_id):
    c = Context()
    rih = RelatedInfoHandler(experiment_id)
    if request.POST:
        form = forms.RelatedUriForm(request.POST)
        if form.is_valid():
            rih.edit_uri(form.cleaned_data, parameterset_id)
            return _redirect(experiment_id)
    else:
        form = forms.RelatedUriForm(initial=rih.uri_form_data(parameterset_id))
    c['form'] = form
    c['url'] = reverse('tardis.apps.related_info.views.edit_uri', args=[experiment_id, parameterset_id])
    url = 'related_info/add_uri.html'
    return HttpResponse(render_response_index(request, url, c))

@authz.write_permissions_required
def edit_publication(request, experiment_id, parameterset_id):
    c = Context()
    rih = RelatedInfoHandler(experiment_id)
    if request.POST:
        form = forms.RelatedPublicationForm(request.POST)
        if form.is_valid():
            rih.edit_publication(form.cleaned_data, parameterset_id)
            return _redirect(experiment_id)
    else:
        form = forms.RelatedPublicationForm(initial=rih.publication_form_data(parameterset_id))
    c['form'] = form
    c['url'] = reverse('tardis.apps.related_info.views.edit_publication', args=[experiment_id, parameterset_id])
    url = 'related_info/add_publication.html'
    return HttpResponse(render_response_index(request, url, c))

@require_POST
@authz.write_permissions_required
def delete_uri(request, experiment_id, parameterset_id):
    rih = RelatedInfoHandler(experiment_id)
    rih.delete_uri(parameterset_id)
    return HttpResponse('{"success": true}', mimetype='application/json');

@require_POST
@authz.write_permissions_required
def delete_publication(request, experiment_id, parameterset_id):
    rih = RelatedInfoHandler(experiment_id)
    rih.delete_publication(parameterset_id)
    return HttpResponse('{"success": true}', mimetype='application/json');
