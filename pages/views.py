import logging
import os

from django.conf import settings
from django.core.mail import send_mail
from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View

from category.models import Category
from projects.models import Project

logger = logging.getLogger(__name__)

PRESENTATIONS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'static', 'presentations'
)


class Home(TemplateView):

    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.filter(active=True)
        context['categories'] = Category.objects.all()
        return context


class Presentations(TemplateView):

    template_name = "pages/presentations.html"


@xframe_options_sameorigin
def serve_presentation(request, filename):
    filepath = os.path.join(PRESENTATIONS_DIR, filename)
    if not os.path.isfile(filepath) or '..' in filename:
        raise Http404
    return FileResponse(open(filepath, 'rb'), content_type='application/pdf')


class SendMessage(View):
    def post(self, *args, **kwargs):
        try:
            name = self.request.POST.get('name', '')
            email = self.request.POST.get('email', '')
            message = self.request.POST.get('message', '')

            if not all([name, email, message]):
                return JsonResponse(
                    {'msg': 'Please fill in all fields.'},
                    status=400
                )

            subject = f"Msg from {name}, form in ariedi.com"
            full_message = f"From: {name} <{email}>\n\n{message}"

            # Check if email is configured
            if settings.EMAIL_HOST:
                send_mail(
                    subject,
                    full_message,
                    settings.EMAIL_HOST_USER or 'noreply@ariedi.com',
                    ['joaoariedi@gmail.com'],
                    fail_silently=False
                )
                return JsonResponse({'msg': 'Thanks! Your message was sent successfully.'})
            else:
                # Log the message if email is not configured
                logger.info(f"Contact form submission: {subject}\n{full_message}")
                return JsonResponse({'msg': 'Thanks! Your message was received.'})

        except Exception as e:
            logger.error(f"Error sending contact form: {e}")
            return JsonResponse(
                {'msg': 'Sorry, there was an error. Please try again or email me directly.'},
                status=500
            )




