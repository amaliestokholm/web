# encoding: utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from tutor.models import *
from django.contrib.auth.views import password_change
from django.views.generic import ListView, UpdateView
from tutor.viewimpl.loginout import logout_view, login_view
from tutor.viewimpl.profile import profile_view
from django import forms
from mftutor import siteconfig

class GroupsView(ListView):
    context_object_name = 'groups'
    template_name = 'groups.html'
    def get_queryset(self):
        return Tutor.objects.select_related().get(profile=self.request.user.get_profile(), year=2012).groups.select_related().all()

def tutor_password_change_view(request):
    if 'back' in request.GET:
        back = request.GET['back']
    else:
        back = reverse('news')
    return password_change(request, 'registration/password_change_form.html', back)

class UploadPictureForm(forms.ModelForm):
    class Meta:
        model = TutorProfile
        fields = ('picture',)

class UploadPictureView(UpdateView):
    model = TutorProfile
    template_name = 'uploadpicture.html'
    form_class = UploadPictureForm
    def get_object(self):
        return self.request.user.get_profile()
    def get_success_url(self):
        return reverse('upload_picture_view')

def tutors_view(request, group=None):
    lookup_group = group or 'alle'

    tutorgroup = get_object_or_404(TutorGroup, handle=lookup_group)

    leader = tutor_group_leader(lookup_group, siteconfig.year)

    tutors = Tutor.objects.filter(year=siteconfig.year, early_termination__isnull=True, groups__handle=lookup_group) \
            .order_by('profile__user__first_name').select_related()

    groups = TutorGroup.objects.filter(visible=True, tutor__year__in=[siteconfig.year]).distinct()

    if leader:
        tutors = tutors.exclude(pk=leader.pk)
        tutors = [leader] + list(tutors.all())

    return render_to_response('tutors.html',
            {
                'group': group,
                'leader': leader,
                'tutor_list': tutors,
                'groups': groups,
                },
            RequestContext(request))
