from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


@method_decorator(csrf_exempt, name="dispatch")
class WebhookEchoView(View):
    def post(self, request):
        return HttpResponse(request.body)
