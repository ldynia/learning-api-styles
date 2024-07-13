from django.test import Client


def before_feature(context, feature):
    context.client = Client()
