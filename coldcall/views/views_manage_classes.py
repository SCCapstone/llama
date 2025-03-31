from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from .view_helper import get_template_dir
from coldcall.models import Class

class ManageClassesView(LoginRequiredMixin, View):
    def get(self, request):
        self.template_name = get_template_dir("manage_classes", request.is_mobile)
        classes = Class.objects.filter(professor_key=request.user)

        class_filter = request.GET.get('class_filter', '')

        if classes and class_filter == 'archived':
            classes = Class.objects.filter(professor_key=request.user, is_archived=True)
        elif classes and class_filter == 'active':
            classes = Class.objects.filter(professor_key=request.user, is_archived=False)
        elif classes and class_filter == 'all':
            classes = Class.objects.filter(professor_key=request.user)
        else:
            classes = Class.objects.filter(professor_key=request.user, is_archived=False) # default to active

        context = {
            'classes': classes,
            'class_filter': class_filter,
        }

        return render(request, self.template_name, context)