import re

import tf2mon
from tf2mon.chat import Chat
from tf2mon.game import GameEvent
from tf2mon.player import Player


class GameChatEvent(GameEvent):

    # 'Bob :  hello'
    # '*DEAD* Bob :  hello'
    # '*DEAD*(TEAM) Bob :  hello'

    pattern = (
        r"(?:(?P<dead>\*DEAD\*)?(?P<teamflag>\(TEAM\))? )?(?P<username>.*) :  ?(?P<msg>.*)$"
    )

    def handler(self, match: re.Match) -> None:

        _leader, _dead, teamflag, username, msg = match.groups()

        user = tf2mon.monitor.users[username]
        chat = Chat(user, teamflag, msg)

        user.chats.append(chat)
        tf2mon.monitor.chats.append(chat)
        tf2mon.ui.show_chat(chat)

        # if this is a team chat, then we know we're on the same team, and
        # if one of us knows which team we're on and the other doesn't, we
        # can assign.

        me = my = tf2mon.monitor.me
        if chat.teamflag and user != me:
            # we're on the same team
            if not user.team:
                if my.team:
                    user.assign_team(my.team)
            elif not my.team:
                me.assign_team(user.team)

        # inspect msg
        if tf2mon.monitor.is_racist_text(chat.msg):
            user.kick(Player.RACIST)

        elif user.is_cheater_chat(chat):
            user.kick(Player.CHEATER)
