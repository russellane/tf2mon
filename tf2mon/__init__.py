"""Team Fortress 2 Console Monitor."""

from argparse import Namespace

from loguru import logger  # noqa

from tf2mon.controls import Controls
from tf2mon.pkg import APPNAME, APPTAG  # noqa
from tf2mon.steamweb import SteamWebAPI

config: dict = {}
options: Namespace = None
steam_web_api: SteamWebAPI = None

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
from tf2mon.controls.misc import SingleStepControl as _SingleStepControl  # noqa
from tf2mon.controls.misc import TauntFlagControl as _TauntFlagControl  # noqa
from tf2mon.controls.misc import ThroeFlagControl as _ThroeFlagControl  # noqa
from tf2mon.controls.msgqueues import MsgQueuesControl as _MsgQueuesControl  # noqa
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
MsgQueuesControl = _MsgQueuesControl()
PushControl = _PushControl()
ResetPaddingControl = _ResetPaddingControl()
ShowDebugControl = _ShowDebugControl()
ShowKDControl = _ShowKDControl()
ShowKillsControl = _ShowKillsControl()
ShowPerksControl = _ShowPerksControl()
SingleStepControl = _SingleStepControl()
SortOrderControl = _SortOrderControl()
SpamsClearControl = _SpamsClearControl()
SpamsControl = _SpamsControl()
SpamsPopControl = _SpamsPopControl()
SpamsPopleftControl = _SpamsPopleftControl()
TauntFlagControl = _TauntFlagControl()
ThroeFlagControl = _ThroeFlagControl()
UserPanelControl = _UserPanelControl()

controls = Controls()
controls.bind(HelpControl, "F1")
controls.bind(MotdControl, "Ctrl+F1")
controls.bind(DebugFlagControl, "F2")
controls.bind(TauntFlagControl, "F3")
controls.bind(ThroeFlagControl, "Shift+F3")
controls.bind(ShowKDControl, "F4")
controls.bind(ShowKillsControl, "Shift+F4")
controls.bind(UserPanelControl, "F5")
controls.bind(ShowPerksControl, "Shift+F5")
controls.bind(JoinOtherTeamControl, "F6")
controls.bind(SortOrderControl, "F7")
controls.bind(LogLocationControl, "F8")
controls.bind(ResetPaddingControl, "Ctrl+F8")
controls.bind(LogLevelControl, "Shift+F8")
controls.bind(GridLayoutControl, "F9")
controls.bind(ClearChatsControl, "Shift+F9")
controls.bind(ShowDebugControl, "KP_INS")
controls.bind(SingleStepControl, "KP_DEL")
controls.bind(KickLastCheaterControl, "[", game_only=True)
controls.bind(KickLastRacistControl, "]", game_only=True)
controls.bind(KickLastSuspectControl, "\\", game_only=True)
controls.bind(KicksPopControl, "KP_HOME")
controls.bind(KicksClearControl, "KP_LEFTARROW")
controls.bind(KicksPopleftControl, "KP_END")
controls.bind(SpamsPopControl, "KP_PGUP")
controls.bind(SpamsClearControl, "KP_RIGHTARROW")
controls.bind(SpamsPopleftControl, "KP_PGDN")
controls.bind(ClearQueuesControl, "KP_5")
controls.bind(PushControl, "KP_DOWNARROW")
