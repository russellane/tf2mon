import re

import tf2mon.monitor as Monitor
from tf2mon.chat import Chat
from tf2mon.game import GameEvent
from tf2mon.player import Player
from tf2mon.racist import is_racist_text


class GameChatEvent(GameEvent):

    # 'Bob :  hello'
    # '*DEAD* Bob :  hello'
    # '*DEAD*(TEAM) Bob :  hello'

    pattern = (
        r"(?:(?P<dead>\*DEAD\*)?(?P<teamflag>\(TEAM\))? )?(?P<username>.*) :  ?(?P<msg>.*)$"
    )

    def handler(self, match: re.Match) -> None:

        _leader, _dead, teamflag, username, msg = match.groups()

        user = Monitor.users[username]
        chat = Chat(user, teamflag, msg)

        user.chats.append(chat)
        Monitor.chats.append(chat)
        Monitor.ui.show_chat(chat)

        # if this is a team chat, then we know we're on the same team, and
        # if one of us knows which team we're on and the other doesn't, we
        # can assign.

        if chat.teamflag and user != Monitor.users.me:
            # we're on the same team
            if not user.team:
                if Monitor.users.my.team:
                    user.assign_team(Monitor.users.my.team)
            elif not Monitor.users.my.team:
                Monitor.users.me.assign_team(user.team)

        # inspect msg
        if is_racist_text(chat.msg):
            user.kick(Player.RACIST)

        elif user.is_cheater_chat(chat):
            user.kick(Player.CHEATER)
