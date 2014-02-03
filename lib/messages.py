"""Definitions of messages sent/received by clients and servers."""


def ctrl_success(msg="", result=None):
    """"""
    return {"type": "ctrl_success", "msg": msg, "result": result}


def ctrl_error(msg=""):
    """Construct message for CtrlServer-related errors.

    :param msg: Optional error message.
    :type msg: string
    :returns: Constructed ctrl_error dict, ready to be sent over the wire.

    """
    return {"type": "ctrl_error", "msg": msg}

def ctrl_cmd(cmd, opts=None):
    """Construct message used for sending a command to the CtrlServer.

    :param cmd: Primary-key description of the type of message this is.
    :type cmd: string
    :param opts: Any data that needs to be passed with this message.
    :type opts: dict
    :returns: Constructed cmd_msg dict, ready to be sent over the wire.

    """
    return {"type": "cmd_msg", "cmd": cmd, "opts": opts}
