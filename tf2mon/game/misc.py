from typing import Match

from loguru import logger

import tf2mon
from tf2mon.gameevent import GameEvent
from tf2mon.user import Team


class GameServerEvent(GameEvent):

    # must be before `chat`
    # account : not logged in  (No account specified)
    # version : 6173888/24 6173888 secure
    # map     : pl_barnblitz at: 0 x, 0 y, 0 z
    # udp/ip  : 208.78.164.167:27067  (public ip: 208.78.164.167)
    # tags    : hidden,increased_maxplayers,payload,valve
    # steamid : [A:1:3814649857:15826] (90139968514486273)
    # players : 20 humans, 0 bots (32 max)
    # edicts  : 1378 used of 2048 max

    pattern = r"(account|version|map|udp\/ip|tags|steamid|players|edicts)\s+: (.*)"

    def handler(self, _match: Match[str] | None) -> None:
        pass  # logger.log("server", m.group(0)),


class GamePingEvent(GameEvent):

    # "06/05/2022 - 13:54:19:   67 ms : luft"
    # "06/05/2022 - 13:54:19:xy 87 ms : BananaHatTaco"
    pattern = r"\s*\d+ ms .*"

    def handler(self, _match: Match[str] | None) -> None:
        pass  # logger.log("server", m.group(0)),


class GameLobbyFailedEvent(GameEvent):

    pattern = "Failed to find lobby shared object"

    def handler(self, match: Match[str]) -> None:
        logger.trace("tf_lobby_debug failed: " + match.group(0))


class GameTeamsSwitchedEvent(GameEvent):

    pattern = "^Teams have been switched"

    def handler(self, _match: Match[str] | None) -> None:
        pass  # tf2mon.users.switch_teams()


class GameUserSwitchedEvent(GameEvent):

    pattern = r"You have switched to team (?P<teamname>\w+) and will"

    def handler(self, match: Match[str]) -> None:
        tf2mon.users.my.team = Team(match.group("teamname"))


class GameHostnameEvent(GameEvent):

    # hostname: Valve Matchmaking Server (Virginia iad-1/srcds148 #53)

    pattern = "^hostname: (.*)"

    def handler(self, _match: Match[str] | None) -> None:
        tf2mon.users.check_status()
