"""Player 'chat' messages."""

import time

from loguru import logger


class Chat:
    """Player 'chat' messages."""

    def __init__(self, user, teamflag, msg):
        """Create `Chat` object.

        Args:
            user:       User(object).
            teamflag:   True=team-chat, False=all-chat.
            msg:        The msg chatted by the user.
        """

        self.seqno = time.strftime("%T", time.localtime(int(time.time())))
        self.user = user
        self.teamflag = teamflag
        self.msg = msg

        level = "TEAMCHAT" if teamflag else "CHAT"
        if self.user.team:
            level += self.user.team.name

        logger.opt(depth=1).log(level, f"{user} {msg}")

    def __repr__(self):
        return (
            self.__class__.__name__
            + "("
            + ", ".join(
                [
                    f"seqno={self.seqno}",
                    f"user={self.user}",
                    f"teamflag={self.teamflag}",
                    f"msg={self.msg!r}",
                ]
            )
            + ")"
        )
