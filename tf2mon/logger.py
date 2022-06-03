"""Logger config."""

from loguru import logger


def configure_logger() -> None:
    """Logger config."""

    # pylint: disable=too-many-statements

    # remove bold from loguru default colors
    # for lvl in logger._core.levels.values():
    #    logger.level(lvl.name, color=lvl.color.replace('<bold>', ''))

    # set severity of custom levels relative to the builtins
    _always = _warn = logger.level("WARNING").no
    _info = logger.level("INFO").no
    _debug = logger.level("DEBUG").no
    _trace = logger.level("TRACE").no

    # black blue cyan green magenta red white yellow
    # bold dim normal hide italic blink strike underline reverse
    # logger.level('DEBUG', no=_debug, color='<cyan>')
    # logger.level('TRACE', color='<white>')

    # admin
    logger.level("ADMIN", no=_always, color="<magenta><bold><italic>")
    logger.level("KICK", no=_always, color="<red><italic><reverse>")

    # users
    logger.level("ADDUSER", no=_always, color="<yellow><italic>")
    logger.level("Inactive", no=_always, color="<yellow>")

    # lobby
    logger.level("ADDLOBBY", no=_trace, color="<yellow><italic><bold>")

    # queues
    logger.level("CLEAR", no=_info, color="<magenta>")
    logger.level("EMPTY", no=_info, color="<magenta><reverse>")
    logger.level("PUSH", no=_info, color="<magenta><italic>")
    logger.level("PUSHLEFT", no=_info, color="<magenta><italic><bold>")
    logger.level("POP", no=_info, color="<magenta><italic>")
    logger.level("POPLEFT", no=_info, color="<magenta><italic><bold>")

    logger.level("SPAMS", no=_always, color="<white>")
    logger.level("KICKS", no=_always, color="<white><italic>")

    # gameplay
    logger.level("CAPBLU", no=_always, color="<cyan>")
    logger.level("CAPRED", no=_always, color="<red>")
    logger.level("CHAT", no=_always, color="<green>")
    logger.level("CHATBLU", no=_always, color="<cyan>")
    logger.level("CHATRED", no=_always, color="<red>")
    logger.level("CONNECT", no=_always, color="<magenta>")
    logger.level("DEFBLU", no=_always, color="<cyan>")
    logger.level("DEFRED", no=_always, color="<red>")
    logger.level("KILL", no=_always, color="<green>")
    logger.level("KILLBLU", no=_always, color="<cyan>")
    logger.level("KILLRED", no=_always, color="<red>")
    logger.level("STATUS", no=_trace, color="<magenta>")
    logger.level("TEAMCHAT", no=_always, color="<green><italic>")
    logger.level("TEAMCHATBLU", no=_always, color="<cyan><italic>")
    logger.level("TEAMCHATRED", no=_always, color="<red><italic>")
    logger.level("PERK-ON", no=_always, color="<green><italic>")
    logger.level("PERK-OFF", no=_always, color="<green>")

    # logger.level('action', no=_debug,  color='<blue><bold>')
    # logger.level('assign', no=_debug,  color='<green>')
    logger.level("div", no=_debug, color="<cyan>")
    logger.level("duel", no=_info, color="<magenta>")
    logger.level("exclude", no=_trace, color="<white>")
    logger.level("help", no=_always, color="<magenta>")
    logger.level("ignore", no=_debug, color="<white>")
    logger.level("injected", no=_always, color="<yellow><reverse><italic>")
    logger.level("logline", no=_debug, color="<yellow>")
    logger.level("nextline", no=_warn, color="<yellow>")
    logger.level("console", no=_always, color="<green><bold>")
    logger.level("hacker", no=_always, color="<yellow><reverse>")
    logger.level("regex", no=_trace, color="<magenta>")
    logger.level("report", no=_always, color="<cyan>")
    logger.level("server", no=_trace, color="<cyan>")
    logger.level("QVALVE", no=_always, color="<cyan><italic>")
    logger.level("toggle", no=_debug, color="<green><bold><italic>")
    logger.level("user", no=_debug, color="<green>")
    logger.level("RED", no=_debug, color="<red>")
    logger.level("BLU", no=_debug, color="<cyan>")

    logger.level("MILENKO", no=_always, color="<yellow><bold><italic><reverse>")
    logger.level("CHEATER", no=_always, color="<yellow><bold><italic>")
    logger.level("SUSPECT", no=_always, color="<magenta><bold><italic>")
    logger.level("RACIST", no=_always, color="<red><bold><italic><reverse>")
    logger.level("FUZZ", no=_always, color="<yellow><reverse>")
    logger.level("ALIAS", no=_always, color="<cyan><reverse>")
    logger.level("NOTIFY", no=_always, color="<yellow><reverse>")
