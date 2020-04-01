import json

from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View

from category.models import Category
from projects.models import Project


class Home(TemplateView):

    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.filter(active=True)
        context['categories'] = Category.objects.all()
        return context


class SendMessage(View):
    def post(self, *args, **kwargs):
        name = self.request.POST['name']
        email = self.request.POST['email']
        message = self.request.POST['message']
        subject = f"Msg from {name}, form in ariedi.com.br"

        send_mail(subject,
                  message,
                  email,
                  ['joaoariedi@gmail.com'],
                  fail_silently=False)

        response = {'msg': 'Thanks, your message was sent successfully.'}

        return JsonResponse(response)




