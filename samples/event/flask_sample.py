import threading
import queue
from flask import Flask

import lark_oapi as lark
from lark_oapi.adapter.flask import *
from lark_oapi.api.im.v1 import *

app = Flask(__name__)


def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    print(lark.JSON.marshal(data))


def do_customized_event(data: lark.CustomizedEvent) -> None:
    print(lark.JSON.marshal(data))


handler = lark.EventDispatcherHandler.builder(lark.ENCRYPT_KEY, lark.VERIFICATION_TOKEN, lark.LogLevel.DEBUG) \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p1_customized_event("message", do_customized_event) \
    .build()


q = queue.Queue()

def worker():
    while True:
        request = q.get()
        print(f'handler on {request}')
        resp = handler.do(request)
        print(f'Finished {resp}')
        q.task_done()


@app.route("/event", methods=["POST"])
def event():
    # put event message to queue, do not block current request
    # return empty
    q.put_nowait(parse_req())
    return


if __name__ == "__main__":
    # Turn-on the worker thread.
    threading.Thread(target=worker, daemon=True).start()
    # start flask server
    app.run(port=7777)
