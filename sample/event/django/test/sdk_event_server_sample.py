"""test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from typing import Dict

import attr
from django.http import HttpRequest, HttpResponse
from django.urls import path
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from larksuiteoapi.model import OapiHeader, OapiRequest
from larksuiteoapi import Config, Context, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG
from larksuiteoapi.event import BaseEvent, set_event_callback, handle_event
from larksuiteoapi.service.contact.v3 import UserUpdatedEventHandler, UserUpdatedEvent

# for Cutome APP（企业自建应用）
app_settings = Config.new_internal_app_settings_from_env()

# for memory store and logger(level=debug)
conf = Config(DOMAIN_FEISHU, app_settings, log_level=LEVEL_DEBUG)


def user_update_handle(ctx, conf, event):
    # type: (Context, Config, UserUpdatedEvent) ->None
    print(ctx.get_request_id())
    print(event.header)
    print(event.event)
    pass


# set event type 'contact.user.updated_v3' handle
UserUpdatedEventHandler.set_callback(conf, user_update_handle)


@method_decorator(csrf_exempt, name='dispatch')
class SampleWebhookEventHandler(View):
    def post(self, request):  # type: (HttpRequest) -> HttpResponse
        oapi_request = OapiRequest(uri=request.path, body=request.body, header=OapiHeader(request.headers))
        oapi_resp = handle_event(conf, oapi_request)
        resp = HttpResponse(oapi_resp.body, status=oapi_resp.status_code, content_type=oapi_resp.content_type)
        return resp


urlpatterns = [
    path('webhook/event', SampleWebhookEventHandler.as_view()),
]
