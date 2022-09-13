"""Team Fortress 2 Gameplay."""

from loguru import logger

from tf2mon.game.capture import GameCaptureEvent
from tf2mon.game.chat import GameChatEvent
from tf2mon.game.connected import GameConnectedEvent
from tf2mon.game.kill import GameKillEvent
from tf2mon.game.lobby import GameLobbyEvent
from tf2mon.game.perk import (
    GamePerkChangeEvent,
    GamePerkOff1Event,
    GamePerkOff2Event,
    GamePerkOnEvent,
)
from tf2mon.game.status import GameStatusEvent
from tf2mon.regex import Regex
from tf2mon.users import Users


class Gameplay:
    """Team Fortress 2 Gameplay."""

    regex_list = [
        # new server
        # Regex(
        #     "(Client reached server_spawn.$|Connected to [0-9]|Differing lobby received.)",
        #     lambda m: tf2mon.reset_game(),
        # ),
        # capture/defend
        GameCaptureEvent().regex,
        # must be before `chat`
        # account : not logged in  (No account specified)
        # version : 6173888/24 6173888 secure
        # map     : pl_barnblitz at: 0 x, 0 y, 0 z
        # udp/ip  : 208.78.164.167:27067  (public ip: 208.78.164.167)
        # tags    : hidden,increased_maxplayers,payload,valve
        # steamid : [A:1:3814649857:15826] (90139968514486273)
        # players : 20 humans, 0 bots (32 max)
        # edicts  : 1378 used of 2048 max
        Regex(
            r"(account|version|map|udp\/ip|tags|steamid|players|edicts)\s+: (.*)",
            lambda m: ...,  # logger.log("server", m.group(0)),
        ),
        # "06/05/2022 - 13:54:19: Client ping times:"
        Regex(
            r"Client ping times:",
            lambda m: ...,  # logger.log("server", m.group(0)),
        ),
        # "06/05/2022 - 13:54:19:   67 ms : luft"
        # "06/05/2022 - 13:54:19:xy 87 ms : BananaHatTaco"
        Regex(
            r"\s*\d+ ms .*",
            lambda m: ...,  # logger.log("server", m.group(0)),
        ),
        GameChatEvent().regex,
        GameKillEvent().regex,
        GameConnectedEvent().regex,
        GameStatusEvent().regex,
        GameLobbyEvent().regex,
        GamePerkOnEvent().regex,
        GamePerkOff1Event().regex,
        GamePerkOff2Event().regex,
        GamePerkChangeEvent().regex,
        #
        Regex(
            "Failed to find lobby shared object",
            lambda m: logger.trace("tf_lobby_debug failed: " + m.group(0)),
        ),
        # Regex(
        #    '^Teams have been switched',
        #    lambda m: tf2mon.users.switch_teams()),
        #
        Regex(
            r"You have switched to team (?P<teamname>\w+) and will",
            lambda m: Users.me.assign_team(m.group("teamname")),
        ),
        # hostname: Valve Matchmaking Server (Virginia iad-1/srcds148 #53)
        Regex(
            "^hostname: (.*)",
            lambda m: Users.check_status(),
        ),
    ]
