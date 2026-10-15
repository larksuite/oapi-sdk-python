"""mentioned_all for rich-text post @all messages (issue #138).

A post that @-mentions everyone carries an ``at`` AST node with
``user_id == "all"`` and Feishu does NOT populate ``mentions[]`` for @all —
so the only signal is the rendered text. The flatten renderer must emit the
``@_all`` placeholder so the pipeline's probes (``text_has_mention_all`` /
``resolve_mentions``) fire.
"""

import json

import pytest

from lark_oapi.channel.normalize.pipeline import InboundPipeline, PipelineConfig, PipelineDeps


def _msg(msg_type="post", content=None):
    return {
        "message_id": "om_1",
        "create_time": 1000,
        "chat_id": "oc_1",
        "chat_type": "group",
        "message_type": msg_type,
        "content": json.dumps(content or {"text": "hi"}, ensure_ascii=False),
        "mentions": [],
    }


def _sender(open_id="ou_sender"):
    return {"sender_id": {"open_id": open_id, "user_id": "u1"}, "sender_type": "user"}


@pytest.mark.asyncio
async def test_post_mention_all_sets_mentioned_all():
    # Covers both wire shapes: the classic single-locale ``{"content": ...}``
    # post and locale-keyed posts (``{"zh_cn": {...}}``).
    for post_content in (
        {
            "content": [
                [
                    {"tag": "at", "user_id": "all", "user_name": "Everyone"},
                    {"tag": "text", "text": " heads up everyone"},
                ]
            ]
        },
        {
            "zh_cn": {
                "content": [
                    [
                        {"tag": "at", "user_id": "all", "user_name": "所有人"},
                        {"tag": "text", "text": " 全体注意"},
                    ]
                ]
            }
        },
    ):
        p = InboundPipeline(PipelineConfig(), PipelineDeps())
        inbound = await p.process(
            event_id="e", message_event=_msg(content=post_content), sender=_sender()
        )
        assert inbound is not None
        assert inbound.mentioned_all is True
        # the @_all placeholder resolves to the human-visible form
        assert "@all" in inbound.content.text


@pytest.mark.asyncio
async def test_post_regular_at_does_not_set_mentioned_all():
    post_content = {
        "content": [
            [
                {"tag": "at", "user_id": "ou_user", "user_name": "Alice"},
                {"tag": "text", "text": " hi"},
            ]
        ]
    }
    p = InboundPipeline(PipelineConfig(), PipelineDeps())
    inbound = await p.process(
        event_id="e", message_event=_msg(content=post_content), sender=_sender()
    )
    assert inbound is not None
    assert inbound.mentioned_all is False
    assert "@Alice" in inbound.content.text
