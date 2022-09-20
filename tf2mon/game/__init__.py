"""Team Fortress 2 Gameplay."""

from .capture import GameCaptureEvent
from .chat import GameChatEvent
from .connected import GameConnectedEvent
from .kill import GameKillEvent
from .lobby import GameLobbyEvent
from .misc import (
    GameHostnameEvent,
    GameLobbyFailedEvent,
    GamePingEvent,
    GameServerEvent,
    GameTeamsSwitchedEvent,
    GameUserSwitchedEvent,
)
from .perk import GamePerkChangeEvent, GamePerkOff1Event, GamePerkOff2Event, GamePerkOnEvent
from .status import GameStatusEvent
from .suicide import GameSuicideEvent

events = [
    GameCaptureEvent(),
    GameServerEvent(),
    GamePingEvent(),
    GameChatEvent(),
    GameKillEvent(),
    GameConnectedEvent(),
    GameSuicideEvent(),
    GameStatusEvent(),
    GameLobbyEvent(),
    GamePerkOnEvent(),
    GamePerkOff1Event(),
    GamePerkOff2Event(),
    GamePerkChangeEvent(),
    GameLobbyFailedEvent(),
    GameTeamsSwitchedEvent(),
    GameUserSwitchedEvent(),
    GameHostnameEvent(),
]
