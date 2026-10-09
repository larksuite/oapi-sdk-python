"""Synchronous Agent calls and incremental SSE consumption."""

import sys

from common import (
    arguments,
    checked,
    configuration,
    create_session_request,
    handle_event,
    interrupt_requests,
    message_request,
    query_id,
    reply_status,
    required,
    stream_options,
    stream_request,
    upload_source,
    uploaded,
)


def read(api, option, sid, query, cursor="", close_early=False):
    request = stream_request(sid, query)
    bounds = stream_options(cursor)
    stream = api.session_event.stream(request, option, bounds)
    # The context manager closes the HTTP body on break, error or cancellation.
    with stream:
        print("stream content type=" + stream.headers.get("content-type", ""))
        for event in stream:
            handle_event(event)
            if close_early:
                print("closing receiver after one event; Agent may continue generating")
                break


def chat(api, option):
    request = create_session_request()
    response = api.session.create(request, option)
    session = checked(response, "create session")
    if not session.id:
        raise RuntimeError("create session: missing id")

    request = message_request(session.id)
    response = api.session_event.create(request, option)
    submitted = checked(response, "send message")
    query = query_id(submitted)
    print("AGENT_SESSION_ID=" + session.id)
    print("AGENT_QUERY_MESSAGE_ID=" + query)
    read(api, option, session.id, query)


def run(mode):
    api, option = configuration()
    if mode == "chat":
        chat(api, option)
    elif mode == "upload":
        with upload_source() as request:
            response = api.file.create(request, option)
            data = checked(response, "upload")
            uploaded(data)
    elif mode in ("resume", "close"):
        cursor = required("AGENT_LAST_EVENT_ID") if mode == "resume" else ""
        sid = required("AGENT_SESSION_ID")
        query = required("AGENT_QUERY_MESSAGE_ID")
        close_early = mode == "close"
        read(api, option, sid, query, cursor, close_early)
    else:
        request, get = interrupt_requests()
        response = api.session_event.create(request, option)
        checked(response, "interrupt reply")
        response = api.session_message.get(get, option)
        data = checked(response, "query reply")
        reply_status(data)


if __name__ == "__main__":
    try:
        run(arguments().mode)
    except KeyboardInterrupt:
        print(
            "receiver cancelled; this does not interrupt Agent generation",
            file=sys.stderr,
        )
    except Exception as error:
        message = str(error) if isinstance(error, RuntimeError) else type(error).__name__
        print(message, file=sys.stderr)
        sys.exit(1)
