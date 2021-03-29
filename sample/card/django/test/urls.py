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
from typing import Union, Dict

from django.http import HttpRequest, HttpResponse
from django.urls import path
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from larksuiteoapi.model.oapi_header import OapiHeader
from larksuiteoapi.model.oapi_request import OapiRequest

from larksuiteoapi import Config, Context, DefaultLogger, LEVEL_DEBUG, DOMAIN_FEISHU, DOMAIN_LARK_SUITE

from larksuiteoapi.card import Card, set_card_callback, handle_card

# for Cutome APP（企业自建应用）
app_settings = Config.new_internal_app_settings_from_env()

# for memory store and logger(level=debug)
conf = Config.new_config_with_memory_store(DOMAIN_FEISHU, app_settings, DefaultLogger(), LEVEL_DEBUG)


def example_handler(ctx, conf, card):
    # type: (Context, Config, Card) -> Union[None, Dict]
    print('card = %s' % card)
    print('request id = %s' % ctx.get_request_id())
    return {
        "config": {
            "wide_screen_mode": True
        },
        "card_link": {
            "url": "https://www.baidu.com",
            "android_url": "https://developer.android.com/",
            "ios_url": "https://developer.apple.com/",
            "pc_url": "https://www.windows.com"
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "this is header"
            }
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": "This is a very very very very very very very long text;"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "Read"
                        },
                        "type": "default"
                    }
                ]
            }
        ]
    }


set_card_callback(conf, example_handler)


@method_decorator(csrf_exempt, name='dispatch')
class SampleWebhookCardHandler(View):
    def post(self, request):  # type: (HttpRequest) -> HttpResponse
        oapi_request = OapiRequest(uri=request.path, body=request.body,
                                   header=OapiHeader(request.headers))

        oapi_resp = handle_card(conf, oapi_request)
        resp = HttpResponse(oapi_resp.body, status=oapi_resp.status_code, content_type=oapi_resp.content_type)
        return resp


urlpatterns = [
    path('webhook/card', SampleWebhookCardHandler.as_view()),
]
