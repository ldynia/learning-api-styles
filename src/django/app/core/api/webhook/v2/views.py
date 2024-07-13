import base64
import hmac
import json
import random
import time

from datetime import datetime
from datetime import timezone

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.status import HTTP_413_REQUEST_ENTITY_TOO_LARGE
from standardwebhooks import Webhook

from config.constants import WEBHOOK_SECRET
from config.constants import WEBHOOK_SECRET_B64
from config.constants import WEBHOOK_EXPIRATION_SECONDS
from config.constants import WEBHOOK_PAYLOAD_MAX_SIZE_BYTES


@method_decorator(csrf_exempt, name="dispatch")
class WebhookCustomView(View):
    wh = Webhook(WEBHOOK_SECRET_B64)

    def post(self, request):
        """
        Method echoes the request body
        """
        if len(request.body) > WEBHOOK_PAYLOAD_MAX_SIZE_BYTES:
            err = "Payload is too big."
            return JsonResponse({"errors": [err]}, status=HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        wh_id = request.headers.get("Webhook-Id")
        if not wh_id:
            err = "Missing Webhook-Id header."
            return JsonResponse({"errors": [err]}, status=HTTP_400_BAD_REQUEST)

        wh_received_signature = request.headers.get("Webhook-Signature")
        if not wh_received_signature:
            err = "Missing Webhook-Signature header."
            return JsonResponse({"errors": [err]}, status=HTTP_400_BAD_REQUEST)

        wh_timestamp = request.headers.get("Webhook-Timestamp")
        if not wh_timestamp:
            err = "Missing Webhook-Timestamp header."
            return JsonResponse({"errors": [err]}, status=HTTP_400_BAD_REQUEST)

        timestamp = datetime.fromtimestamp(int(wh_timestamp), tz=timezone.utc)
        offset = (datetime.now(timezone.utc) - timestamp).total_seconds()
        wh_expired = (int(offset) >= WEBHOOK_EXPIRATION_SECONDS)
        if wh_expired:
            err = "Request is too old."
            return JsonResponse({"errors": [err]}, status=HTTP_400_BAD_REQUEST)

        # Generate a random number to choose between two signature generation methods
        if random.randint(0, 1) == 0:
            print("Generating standard-webhooks signature")
            wh_expected_signature = self.wh.sign(wh_id, timestamp, request.body.decode('utf-8'))
        else:
            # This code exist to support book to create standard-webhooks signature manually
            print("Generating standard-webhooks signature manually")
            payload = request.body.decode("utf-8")
            secret = WEBHOOK_SECRET.encode("utf-8")
            sig_scheme = f"{wh_id}.{int(wh_timestamp)}.{payload}".encode("utf-8") # <5>
            signature = hmac.new(secret, msg=sig_scheme, digestmod="SHA256").digest() # <6>
            signature_b64 = base64.b64encode(signature).decode("utf-8")
            wh_expected_signature = f"v1,{signature_b64}"

        # Compare signatures
        if wh_received_signature != wh_expected_signature:
            err = "HMAC mismatch"
            return JsonResponse({"errors": [err]}, status=HTTP_401_UNAUTHORIZED)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return request.body

        return JsonResponse(data)
