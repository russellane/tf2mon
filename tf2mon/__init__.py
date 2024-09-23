"""Team Fortress 2 Console Monitor."""

import curses
from argparse import Namespace
from pprint import pformat
from typing import Any

from loguru import logger

from tf2mon.conlog import Conlog
from tf2mon.controller import Controller
from tf2mon.steamweb import SteamWebAPI
from tf2mon.ui import UI
from tf2mon.user import Team, UserKey
from tf2mon.users import Users

config: dict[str, Any] = {}
conlog: Conlog | None = None
options: Namespace
steam_web_api: SteamWebAPI
ui: UI
users: Users

from tf2mon.controls.chats import ChatsControl as _ChatsControl  # noqa
from tf2mon.controls.chats import ClearChatsControl as _ClearChatsControl  # noqa
from tf2mon.controls.chats import RefreshChatsControl as _RefreshChatsControl  # noqa
from tf2mon.controls.gridlayout import GridLayoutControl as _GridLayoutControl  # noqa
from tf2mon.controls.help import HelpControl as _HelpControl  # noqa
from tf2mon.controls.help import MotdControl as _MotdControl  # noqa
from tf2mon.controls.kicklast import KickLastCheaterControl as _KickLastCheaterControl  # noqa
from tf2mon.controls.kicklast import KickLastRacistControl as _KickLastRacistControl  # noqa
from tf2mon.controls.kicklast import KickLastSuspectControl as _KickLastSuspectControl  # noqa
from tf2mon.controls.kicks import KicksClearControl as _KicksClearControl  # noqa
from tf2mon.controls.kicks import KicksControl as _KicksControl  # noqa
from tf2mon.controls.kicks import KicksPopControl as _KicksPopControl  # noqa
from tf2mon.controls.kicks import KicksPopleftControl as _KicksPopleftControl  # noqa
from tf2mon.controls.logger import LogLevelControl as _LogLevelControl  # noqa
from tf2mon.controls.logger import LogLocationControl as _LogLocationControl  # noqa
from tf2mon.controls.logger import ResetPaddingControl as _ResetPaddingControl  # noqa
from tf2mon.controls.misc import ClearQueuesControl as _ClearQueuesControl  # noqa
from tf2mon.controls.misc import DebugFlagControl as _DebugFlagControl  # noqa
from tf2mon.controls.misc import JoinOtherTeamControl as _JoinOtherTeamControl  # noqa
from tf2mon.controls.misc import PushControl as _PushControl  # noqa
from tf2mon.controls.misc import ShowDebugControl as _ShowDebugControl  # noqa
from tf2mon.controls.misc import ShowKDControl as _ShowKDControl  # noqa
from tf2mon.controls.misc import ShowKillsControl as _ShowKillsControl  # noqa
from tf2mon.controls.misc import ShowPerksControl as _ShowPerksControl  # noqa
from tf2mon.controls.misc import TauntFlagControl as _TauntFlagControl  # noqa
from tf2mon.controls.misc import ThroeFlagControl as _ThroeFlagControl  # noqa
from tf2mon.controls.msgqueues import DisplayFileControl as _DisplayFileControl  # noqa
from tf2mon.controls.msgqueues import MsgQueuesControl as _MsgQueuesControl  # noqa
from tf2mon.controls.singlestep import SingleStepControl as _SingleStepControl  # noqa
from tf2mon.controls.singlestep import SingleStepStartControl as _SingleStepStartControl  # noqa
from tf2mon.controls.sortorder import SortOrderControl as _SortOrderControl  # noqa
from tf2mon.controls.spams import SpamsClearControl as _SpamsClearControl  # noqa
from tf2mon.controls.spams import SpamsControl as _SpamsControl  # noqa
from tf2mon.controls.spams import SpamsPopControl as _SpamsPopControl  # noqa
from tf2mon.controls.spams import SpamsPopleftControl as _SpamsPopleftControl  # noqa
from tf2mon.controls.userpanel import UserPanelControl as _UserPanelControl  # noqa

controller = Controller(
    [
        ChatsControl := _ChatsControl(),
        ClearChatsControl := _ClearChatsControl(),
        ClearQueuesControl := _ClearQueuesControl(),
        DebugFlagControl := _DebugFlagControl(),
        DisplayFileControl := _DisplayFileControl(),
        GridLayoutControl := _GridLayoutControl(),
        HelpControl := _HelpControl(),
        JoinOtherTeamControl := _JoinOtherTeamControl(),
        KickLastCheaterControl := _KickLastCheaterControl(),
        KickLastRacistControl := _KickLastRacistControl(),
        KickLastSuspectControl := _KickLastSuspectControl(),
        KicksClearControl := _KicksClearControl(),
        KicksControl := _KicksControl(),
        KicksPopControl := _KicksPopControl(),
        KicksPopleftControl := _KicksPopleftControl(),
        LogLevelControl := _LogLevelControl(),
        LogLocationControl := _LogLocationControl(),
        MotdControl := _MotdControl(),
        MsgQueuesControl := _MsgQueuesControl(),
        PushControl := _PushControl(),
        RefreshChatsControl := _RefreshChatsControl(),
        ResetPaddingControl := _ResetPaddingControl(),
        ShowDebugControl := _ShowDebugControl(),
        ShowKDControl := _ShowKDControl(),
        ShowKillsControl := _ShowKillsControl(),
        ShowPerksControl := _ShowPerksControl(),
        SingleStepControl := _SingleStepControl(),
        SingleStepStartControl := _SingleStepStartControl(),
        SortOrderControl := _SortOrderControl(),
        SpamsClearControl := _SpamsClearControl(),
        SpamsControl := _SpamsControl(),
        SpamsPopControl := _SpamsPopControl(),
        SpamsPopleftControl := _SpamsPopleftControl(),
        TauntFlagControl := _TauntFlagControl(),
        ThroeFlagControl := _ThroeFlagControl(),
        UserPanelControl := _UserPanelControl(),
    ]
)

# ordered for rendering `--help`
controller.bind(HelpControl, "F1")
controller.bind(MotdControl, "Ctrl+F1")
controller.bind(DisplayFileControl, "Shift+F1")
controller.bind(DebugFlagControl, "F2")
controller.bind(TauntFlagControl, "F3")
controller.bind(ThroeFlagControl, "Shift+F3")
controller.bind(ShowKDControl, "F4")
controller.bind(ShowKillsControl, "Shift+F4")
controller.bind(UserPanelControl, "F5")
controller.bind(ShowPerksControl, "Shift+F5")
controller.bind(JoinOtherTeamControl, "F6")
controller.bind(SortOrderControl, "F7")
controller.bind(LogLocationControl, "F8")
controller.bind(ResetPaddingControl, "Ctrl+F8")
controller.bind(LogLevelControl, "Shift+F8")
controller.bind(GridLayoutControl, "F9")
controller.bind(RefreshChatsControl, "Ctrl+F9")
controller.bind(ClearChatsControl, "Shift+F9")
controller.bind(ShowDebugControl, "KP_INS")
controller.bind(SingleStepStartControl, "KP_DEL")
controller.bind(KickLastCheaterControl, "[")
controller.bind(KickLastRacistControl, "]")
controller.bind(KickLastSuspectControl, "\\")
controller.bind(KicksPopControl, "KP_HOME")
controller.bind(KicksClearControl, "KP_LEFTARROW")
controller.bind(KicksPopleftControl, "KP_END")
controller.bind(SpamsPopControl, "KP_PGUP")
controller.bind(SpamsClearControl, "KP_RIGHTARROW")
controller.bind(SpamsPopleftControl, "KP_PGDN")
controller.bind(ClearQueuesControl, "KP_5")
controller.bind(PushControl, "KP_DOWNARROW")


def reset_game() -> None:
    """Start new game."""

    logger.success("RESET GAME")

    global users  # noqa
    users = Users()
    users.me = users.my = users[UserKey(str(config.get("player_name")))]
    users.my.team = Team.BLU
    users.my.display_level = "user"
    ChatsControl.clear()
    MsgQueuesControl.clear()


def debugger() -> None:
    """Drop into python debugger."""

    global conlog  # noqa
    assert conlog

    if conlog.is_eof or SingleStepControl.is_stepping:
        curses.reset_shell_mode()
        breakpoint()  # pylint: disable=forgotten-debug-statement
        curses.reset_prog_mode()


def dump() -> None:
    """Dump stuff."""

    global users  # noqa

    logger.success(pformat(users.__dict__))
    for user in users.users_by_username.values():
        logger.success(pformat(user.__dict__))
