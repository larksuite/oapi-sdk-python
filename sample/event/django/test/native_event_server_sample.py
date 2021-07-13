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
conf = Config.new_config_with_memory_store(DOMAIN_FEISHU, app_settings, DefaultLogger(), LEVEL_DEBUG)


@attr.s
class ApplicationAppStatusChangeEventData(object):
    app_id = attr.ib(type=str, default='')
    tenant_key = attr.ib(type=str, default='')
    type = attr.ib(type=str, default='')
    status = attr.ib(type=str, default='')


@attr.s
class ApplicationAppStatusChangeEvent(BaseEvent):
    event = attr.ib(type=ApplicationAppStatusChangeEventData, default=None)


def app_status_change_event_handler(ctx, conf, event):
    # type: (Context, Config, ApplicationAppStatusChangeEvent) -> None
    print(ctx.get_request_id())
    print(conf.app_settings)
    print(event.event.type)


def user_change(ctx, conf, event):
    # type: (Context, Config, Dict) -> None
    print(ctx.get_request_id())
    print(conf.app_settings)
    print(event)


set_event_callback(conf, 'app_status_change', app_status_change_event_handler, ApplicationAppStatusChangeEvent)

set_event_callback(conf, 'user_update', user_change)


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
