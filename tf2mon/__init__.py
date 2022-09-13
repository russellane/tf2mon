"""Team Fortress 2 Console Monitor."""

import curses
from argparse import Namespace
from pprint import pformat

from loguru import logger

from tf2mon.conlog import Conlog
from tf2mon.controller import Controller
from tf2mon.steamweb import SteamWebAPI
from tf2mon.ui import UI
from tf2mon.user import Team
from tf2mon.users import Users

config: dict = {}
conlog: Conlog = None
options: Namespace = None
steam_web_api: SteamWebAPI = None
ui: UI = None

from tf2mon.controls.chats import ChatsControl as _ChatsControl  # noqa
from tf2mon.controls.chats import ClearChatsControl as _ClearChatsControl  # noqa
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
from tf2mon.controls.msgqueues import MsgQueuesControl as _MsgQueuesControl  # noqa
from tf2mon.controls.singlestep import SingleStepControl as _SingleStepControl  # noqa
from tf2mon.controls.singlestep import SingleStepStartControl as _SingleStepStartControl  # noqa
from tf2mon.controls.sortorder import SortOrderControl as _SortOrderControl  # noqa
from tf2mon.controls.spams import SpamsClearControl as _SpamsClearControl  # noqa
from tf2mon.controls.spams import SpamsControl as _SpamsControl  # noqa
from tf2mon.controls.spams import SpamsPopControl as _SpamsPopControl  # noqa
from tf2mon.controls.spams import SpamsPopleftControl as _SpamsPopleftControl  # noqa
from tf2mon.controls.userpanel import UserPanelControl as _UserPanelControl  # noqa

ClearChatsControl = _ClearChatsControl()
ClearQueuesControl = _ClearQueuesControl()
DebugFlagControl = _DebugFlagControl()
GridLayoutControl = _GridLayoutControl()
HelpControl = _HelpControl()
JoinOtherTeamControl = _JoinOtherTeamControl()
KickLastCheaterControl = _KickLastCheaterControl()
KickLastRacistControl = _KickLastRacistControl()
KickLastSuspectControl = _KickLastSuspectControl()
KicksClearControl = _KicksClearControl()
KicksControl = _KicksControl()
KicksPopControl = _KicksPopControl()
KicksPopleftControl = _KicksPopleftControl()
LogLevelControl = _LogLevelControl()
LogLocationControl = _LogLocationControl()
MotdControl = _MotdControl()
ChatsControl = _ChatsControl()
MsgQueuesControl = _MsgQueuesControl()
PushControl = _PushControl()
ResetPaddingControl = _ResetPaddingControl()
ShowDebugControl = _ShowDebugControl()
ShowKDControl = _ShowKDControl()
ShowKillsControl = _ShowKillsControl()
ShowPerksControl = _ShowPerksControl()
SingleStepControl = _SingleStepControl()
SingleStepStartControl = _SingleStepStartControl()
SortOrderControl = _SortOrderControl()
SpamsClearControl = _SpamsClearControl()
SpamsControl = _SpamsControl()
SpamsPopControl = _SpamsPopControl()
SpamsPopleftControl = _SpamsPopleftControl()
TauntFlagControl = _TauntFlagControl()
ThroeFlagControl = _ThroeFlagControl()
UserPanelControl = _UserPanelControl()

#
controller = Controller()

# controls with key bindings
controller.add(HelpControl, "F1")
controller.add(MotdControl, "Ctrl+F1")
controller.add(DebugFlagControl, "F2")
controller.add(TauntFlagControl, "F3")
controller.add(ThroeFlagControl, "Shift+F3")
controller.add(ShowKDControl, "F4")
controller.add(ShowKillsControl, "Shift+F4")
controller.add(UserPanelControl, "F5")
controller.add(ShowPerksControl, "Shift+F5")
controller.add(JoinOtherTeamControl, "F6")
controller.add(SortOrderControl, "F7")
controller.add(LogLocationControl, "F8")
controller.add(ResetPaddingControl, "Ctrl+F8")
controller.add(LogLevelControl, "Shift+F8")
controller.add(GridLayoutControl, "F9")
controller.add(ClearChatsControl, "Shift+F9")
controller.add(ShowDebugControl, "KP_INS")
controller.add(SingleStepStartControl, "KP_DEL")
controller.add(KickLastCheaterControl, "[", game_only=True)
controller.add(KickLastRacistControl, "]", game_only=True)
controller.add(KickLastSuspectControl, "\\", game_only=True)
controller.add(KicksPopControl, "KP_HOME")
controller.add(KicksClearControl, "KP_LEFTARROW")
controller.add(KicksPopleftControl, "KP_END")
controller.add(SpamsPopControl, "KP_PGUP")
controller.add(SpamsClearControl, "KP_RIGHTARROW")
controller.add(SpamsPopleftControl, "KP_PGDN")
controller.add(ClearQueuesControl, "KP_5")
controller.add(PushControl, "KP_DOWNARROW")

# controls without key bindings
controller.add(ChatsControl)
controller.add(KicksControl)
controller.add(SpamsControl)
controller.add(MsgQueuesControl)
controller.add(SingleStepControl)


def reset_game() -> None:
    """Start new game."""

    logger.success("RESET GAME")

    Users.me.assign_team(Team.BLU)
    Users.my.display_level = "user"
    ChatsControl.clear()
    ui.refresh_chats()
    MsgQueuesControl.clear()


def debugger() -> None:
    """Drop into python debugger."""

    if conlog.is_eof or SingleStepControl.is_stepping:
        curses.reset_shell_mode()
        breakpoint()  # pylint: disable=forgotten-debug-statement
        curses.reset_prog_mode()


def dump() -> None:
    """Dump stuff."""

    logger.success(pformat(Users.__dict__))
    for user in Users.users_by_username.values():
        logger.success(pformat(user.__dict__))
