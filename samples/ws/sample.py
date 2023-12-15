import lark_oapi as lark


def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    print(f'[do_p2_im_message_receive_v1 access], data: {lark.JSON.marshal(data, indent=4)}')


def do_customized_event(data: lark.CustomizedEvent) -> None:
    print(f'[do_customized_event access], data: {lark.JSON.marshal(data, indent=4)}')


event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p1_customized_event("message", do_customized_event) \
    .build()


def main():
    cli = lark.ws.Client("cli_a4dc980719f8501b", "xMipnnMfihhJh18U6LP3OhofU0tMyDxW",
                         event_handler=event_handler, log_level=lark.LogLevel.DEBUG)
    cli.start()


if __name__ == "__main__":
    main()
