"""Application controls."""

from tf2mon.controls.debugflag import DebugFlagControl
from tf2mon.controls.gridlayout import GridLayoutControl
from tf2mon.controls.help import HelpControl
from tf2mon.controls.joinotherteam import JoinOtherTeamControl
from tf2mon.controls.loglevel import LogLevelControl
from tf2mon.controls.loglocation import LogLocationControl
from tf2mon.controls.motd import MotdControl
from tf2mon.controls.resetpadding import ResetPaddingControl
from tf2mon.controls.showdebug import ShowDebugControl
from tf2mon.controls.showkd import ShowKDControl
from tf2mon.controls.singlestep import SingleStepControl
from tf2mon.controls.sortorder import SortOrderControl
from tf2mon.controls.tauntflag import TauntFlagControl
from tf2mon.controls.throeflag import ThroeFlagControl
from tf2mon.controls.userpanel import UserPanelControl

# ordered by fkey bindings
CLASS_LIST = [
    HelpControl,
    MotdControl,
    DebugFlagControl,
    TauntFlagControl,
    ThroeFlagControl,
    ShowKDControl,
    UserPanelControl,
    JoinOtherTeamControl,
    SortOrderControl,
    LogLocationControl,
    LogLevelControl,
    ResetPaddingControl,
    GridLayoutControl,
    ShowDebugControl,
    SingleStepControl,
]
