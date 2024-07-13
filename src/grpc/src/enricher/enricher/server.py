# tag::import_modules[]
import calendar
import concurrent
import logging

import grpc
from google.protobuf import any_pb2
from google.rpc import code_pb2, status_pb2, error_details_pb2
from grpc_reflection.v1alpha import reflection
from grpc_status import rpc_status
from pythonjsonlogger import jsonlogger
from transformers import AutoModelForCausalLM, AutoTokenizer

import enricher.proto.enricher.v1.enricher_pb2 as pb2
import enricher.proto.enricher.v1.enricher_pb2_grpc as pb2_grpc
# end::import_modules[]


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(funcName)s %(message)s"
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)


def get_lm_response(system_prompt, user_prompt):
    """Get response from language model"""
    # To improve response quality, use a larger model, such as "Qwen/Qwen2.5-0.5B-Instruct"
    model_name = "HuggingFaceTB/SmolLM2-135M-Instruct"

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype="auto", device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    ids = model.generate(**model_inputs, max_new_tokens=512, temperature=0.1)
    ids = [
        output_ids[len(input_ids) :]
        for input_ids, output_ids in zip(model_inputs.input_ids, ids)
    ]

    response = tokenizer.batch_decode(ids, skip_special_tokens=True)[0]
    return response


def get_month_period(timestamp):
    """Get month period: beginning, mid, end"""
    month_name = timestamp.strftime("%B")
    days_in_month = calendar.monthrange(timestamp.year, timestamp.month)[1]
    threshold = days_in_month // 3
    day = timestamp.day
    if day <= threshold:
        return f"beginning of {month_name}"
    elif day <= 2 * threshold:
        return f"mid of {month_name}"
    else:
        return f"end of {month_name}"


def get_weather_forecast(request):
    """Get text of the weather forecast contructed from indicators"""
    weather_forecast = request.weather_forecast
    location = (
        f"{weather_forecast.city.name} in {weather_forecast.city.country}"
    )
    month_period = get_month_period(weather_forecast.timestamp.ToDatetime())
    rain = (
        f"{int(weather_forecast.rain_sum_mm)} mm rain."
        if weather_forecast.rain_sum_mm > 0
        else f"No rain."
    )
    showers = (
        f"{int(weather_forecast.showers_sum_mm)} mm showers."
        if weather_forecast.showers_sum_mm > 0
        else f"No showers."
    )
    snowfall = (
        f"{int(weather_forecast.snowfall_sum_cm)} cm snowfall."
        if weather_forecast.snowfall_sum_cm > 0
        else f"No snowfall."
    )
    temperature_max_celsius = int(weather_forecast.temperature_max_celsius)
    temperature_min_celsius = int(weather_forecast.temperature_min_celsius)
    weather_forecast = (
        f"This is today's weather forecast for {location} in the {month_period}:\n"
        f"<br>\n"
        f"{rain}\n"
        f"<br>\n"
        f"{showers}\n"
        f"<br>\n"
        f"{snowfall}\n"
        f"<br>\n"
        f"Maximum temperature {temperature_max_celsius} degrees Celsius.\n"
        f"<br>\n"
        f"Minimum temperature {temperature_min_celsius} degrees Celsius.\n"
    )
    return weather_forecast


# tag::define_lm_weather_summarizeer[]
def summarize_weather_forecast(weather_forecast):
    """Prompt language model to get weather forecast explanation"""
    system_prompt = (
        "You are a regional climate expert and a tourist guide. "
        "Respond using a single paragraph and a maximum one sentence."
    )
    user_prompt = weather_forecast + (
        f"Is this weather typical for this location and period of the year?\n"
        "Recommended a tourist attraction for this period and specific weather."
    )
    logger.info("Getting lm_response", extra={"user_prompt": user_prompt})
    lm_response = get_lm_response(system_prompt, user_prompt)
    logger.info("Got lm_response", extra={"lm_response": lm_response})
    return lm_response
# end::define_lm_weather_summarizeer[]


# tag::define_rich_status[]
def create_field_validation_error_status(*, field, description):
    """Get rich status for a field validation error"""
    detail = any_pb2.Any()
    detail.Pack(
        error_details_pb2.BadRequest(
            field_violations=[
                error_details_pb2.BadRequest.FieldViolation(
                    field=field,
                    description=description,
                )
            ]
        )
    )
    return status_pb2.Status(
        code=code_pb2.INVALID_ARGUMENT,
        message="Field validation error",
        details=[detail],
    )
# end::define_rich_status[]


# tag::define_servicer_class[]
class EnricherServiceServicer(pb2_grpc.EnricherServiceServicer):
    def Enrich(self, request, context):
        if not (-90 <= request.weather_forecast.temperature_max_celsius <= 60):
            context.abort(  # <1>
                grpc.StatusCode.INVALID_ARGUMENT,
                "Allowed temperature_max_celsius range is [-90, 60].")

        if not (-90 <= request.weather_forecast.temperature_min_celsius <= 60):
            rich_status = create_field_validation_error_status(
                field="temperature_min_celsius",
                description="Allowed range is [-90, 60].")
            context.abort_with_status(rpc_status.to_status(rich_status))  # <2>

        deadline = context.time_remaining()  # <3>
        logger.info("Remaining deadline", extra={"deadline": deadline})

        weather_forecast = get_weather_forecast(request)  # <4>
        summary = summarize_weather_forecast(weather_forecast)  # <5>
        enriched_content = weather_forecast + (
            f"<br>\n"
            f"<br>\n"
            f"\nLanguage Model says:\n"
            f"<br>\n"
            f"{summary}")
        return pb2.EnrichResponse(content=enriched_content)  # <6>
# end::define_servicer_class[]


# tag::define_caching_interceptor[]
class CachingInterceptor(grpc.ServerInterceptor):
    def __init__(self):
        self.cache = {}  # <1>

    def intercept_service(self, continuation, handler_call_details):  # <2>
        rpc_method = handler_call_details.method
        logger.info("Intercepting", extra={"rpc_method": rpc_method})

        if rpc_method.startswith("/grpc.reflection.v1"):  # <3>
            logger.info("Bypassing interceptor")
            return continuation(handler_call_details)

        next_handler = continuation(handler_call_details)  # <4>

        def return_cached_response(request, context):
            cache_key = request.SerializeToString()  # <5>
            if cache_key not in self.cache:  # <6>
                response = next_handler.unary_unary(request, context)
                self.cache[cache_key] = response
            return self.cache[cache_key]  # <7>

        return grpc.unary_unary_rpc_method_handler(  # <8>
            return_cached_response,
            request_deserializer=next_handler.request_deserializer,
            response_serializer=next_handler.response_serializer)
# end::define_caching_interceptor[]

# tag::run_server[]
server = grpc.server(
    concurrent.futures.ThreadPoolExecutor(),
    interceptors=(CachingInterceptor(),),)
pb2_grpc.add_EnricherServiceServicer_to_server(
    EnricherServiceServicer(), server)

SERVICE_NAMES = (reflection.SERVICE_NAME,
    pb2.DESCRIPTOR.services_by_name["EnricherService"].full_name)
reflection.enable_server_reflection(SERVICE_NAMES, server)

server.add_insecure_port("0.0.0.0:50051")
server.start()
logger.info("gRPC server is ready to serve requests")
server.wait_for_termination()
# end::run_server[]
