from typing import Match

from loguru import logger

import tf2mon
from tf2mon.chat import Chat
from tf2mon.gameevent import GameEvent
from tf2mon.player import Player
from tf2mon.racist import is_racist_text
from tf2mon.user import UserKey


class GameChatEvent(GameEvent):

    # 'Bob :  hello'
    # '*DEAD* Bob :  hello'
    # '*DEAD*(TEAM) Bob :  hello'

    pattern = (
        r"(?:(?P<dead>\*DEAD\*)?(?P<teamflag>\(TEAM\))? )?(?P<username>.*) :  ?(?P<msg>.*)$"
    )

    def handler(self, match: Match[str]) -> None:

        _dead, teamflag, username, msg = match.groups()

        user = tf2mon.users[UserKey(username)]
        chat = Chat(user, bool(teamflag), msg)

        user.chats.append(chat)
        tf2mon.ChatsControl.append(chat)

        level = "TEAMCHAT" if chat.teamflag else "CHAT"
        if user.team:
            level += user.team.name
        logger.log(level, f"{user} {msg}")

        # if this is a team chat, then we know we're on the same team, and
        # if one of us knows which team we're on and the other doesn't, we
        # can assign.

        if chat.teamflag and user != tf2mon.users.me:
            # we're on the same team
            if not user.team:
                if tf2mon.users.my.team:
                    user.team = tf2mon.users.my.team
            elif not tf2mon.users.my.team:
                tf2mon.users.my.team = user.team

        # inspect msg
        if is_racist_text(chat.msg):
            user.kick(Player.RACIST)

        elif user.is_cheater_chat(chat):
            user.kick(Player.CHEATER)
