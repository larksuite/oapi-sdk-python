import asyncio
import os

from lark_oapi.channel import FeishuChannel


def _require_env(name):
    value = os.environ.get(name)
    if not value:
        raise SystemExit(
            f"Missing {name}. Set it before running, for example: "
            f"export {name}=your_value"
        )
    return value


async def main():
    channel = FeishuChannel(
        app_id=_require_env("LARK_APP_ID"),
        app_secret=_require_env("LARK_APP_SECRET"),
    )

    async def on_message(msg):
        await channel.send(
            msg.conversation.chat_id,
            {"text": f"echo: {msg.content_text}"},
        )

    channel.on("message", on_message)

    await channel.connect()


if __name__ == "__main__":
    asyncio.run(main())
