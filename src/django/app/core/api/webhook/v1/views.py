from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import HTTP_400_BAD_REQUEST
from standardwebhooks import Webhook

from config.constants import WEBHOOK_SECRET_B64


@method_decorator(csrf_exempt, name="dispatch")
class WebhookStandardView(View):
    wh = Webhook(WEBHOOK_SECRET_B64)

    def post(self, request):
        try:
            payload = self.wh.verify(request.body, request.headers)
        except Exception as e:
            return JsonResponse({"errors": [str(e)]}, status=HTTP_400_BAD_REQUEST)

        return JsonResponse(payload)
