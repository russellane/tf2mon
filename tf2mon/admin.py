"""Admin Console."""

import re
import threading

from loguru import logger

import tf2mon
from tf2mon.hacker import HackerAttr
from tf2mon.regex import Regex


class Admin:
    """Admin Console."""

    def __init__(self, monitor):
        """Initialize Admin Console."""

        self.monitor = monitor
        self._single_step_event = threading.Event()
        self.is_single_stepping = self.monitor.options.single_step
        self._single_step_re = None

        if pattern := self.monitor.options.search:
            if pattern.startswith("/"):
                pattern = pattern[1:]
            self.set_single_step_pattern(pattern)

        if self.is_single_stepping:
            self.start_single_stepping()
        else:
            self._stop_single_stepping()
        self._single_step_at_eof = False

        # See fkeys.py for:
        #    tf2mon.fkeys.FKey(
        #        cmd='SINGLE-STEP',
        #        game_key='KP_DEL',
        #        curses_key=curses.KEY_DC,
        #        handler=lambda m: self.start_single_stepping(),
        #    ),

        # Commands operator may type into monitor admin console:
        self.regex_list = [
            # stop single-stepping
            Regex("^(c|cont|continue)$", lambda m: self._stop_single_stepping()),
            # stop single-stepping until eof, then single-step again
            Regex("^(r|run|g|go)$", lambda m: self.set_single_step_lineno(0)),
            # dump internals
            Regex("^dump$", lambda m: self.monitor.dump()),
            # pause when logfile reaches `lineno`.
            Regex(
                R"^(b|break|breakpoint)[= ](?P<lineno>\d+)$",
                lambda m: self.set_single_step_lineno(int(m.group("lineno"))),
            ),
            # pause when logfile reaches next line that matches `pattern`.
            Regex(
                "^/(?P<pattern>.*)$", lambda m: self.set_single_step_pattern(m.group("pattern"))
            ),
            # kick cheater
            Regex(
                R"^kick[= ](?P<userid>\d+)$",
                lambda m: self.monitor.users.kick_userid(
                    int(m.group("userid")), HackerAttr.CHEATER
                ),
            ),
            # kick racist
            Regex(
                R"^kkk[= ](?P<userid>\d+)$",
                lambda m: self.monitor.users.kick_userid(
                    int(m.group("userid")), HackerAttr.RACIST
                ),
            ),
            # mark suspect
            Regex(
                R"^suspect[= ](?P<userid>\d+)$",
                lambda m: self.monitor.users.kick_userid(
                    int(m.group("userid")), HackerAttr.SUSPECT
                ),
            ),
            # drop to python debugger
            Regex("^PDB$", lambda m: self.monitor.breakpoint()),
            # deprecated, legacy, support old conlogs.
            Regex(
                "^(TOGGLE-SCOREBOARD|TOGGLE-QUEUES|CHATS-POP|CHATS-POPLEFT|CHATS-CLEAR)$",
                lambda m: logger.debug("ignore"),
            ),
            # The following aren't commands, but other items that may be in
            # the conlog. They don't belong in `gameplay` because they're
            # not generated by tf2.
            # qvalve
            Regex("^(QVALVE) (.*)", lambda m: logger.log(m.group(1), m.group(2))),
        ]

    def start_single_stepping(self):
        """Begin prompting operator before processing each line from con_logfile."""

        self.is_single_stepping = True
        self._single_step_event.clear()

    def _stop_single_stepping(self):
        """End prompting operator before processing each line from con_logfile."""

        self.is_single_stepping = False
        self._single_step_event.set()

    def set_single_step_lineno(self, lineno=0):
        """Begin single-stepping at `lineno` if given else at eof."""

        if lineno:
            self.monitor.conlog.inject_cmd(lineno, "SINGLE-STEP")
        else:
            # stop single-stepping until eof, then single-step again
            self._stop_single_stepping()
            self._single_step_at_eof = True

    def set_single_step_pattern(self, pattern=None):
        """Begin single-stepping at next line that matches `pattern`.

        Pass `None` to clear the pattern.
        """

        if not pattern:
            self._single_step_re = None
            logger.log("ADMIN", "clear _single_step_re")
        else:
            flags = 0
            if pattern.endswith("/i"):
                pattern = pattern[:-2]
                flags = re.IGNORECASE
            elif pattern.endswith("/"):
                pattern = pattern[:-1]
            self._single_step_re = re.compile(pattern, flags)
            logger.log("ADMIN", f"set search={self._single_step_re}")

    def step(self, line):
        """Involve operator if `line` requires single-step attention.

        Called by the game thread (not the admin thread) for each line read
        from conlog, to wait for the operator (when necessary) before
        processing the line.

        If there's an active single-step pattern and last `line` read from
        con_logfile matches pattern, or if we are single-stepping, then
        wait for admin thread to release the lock.

        Args:
            line: last string read from con_logfile.

        Returns:
            immediately if gate is clear, else waits for it.
        """

        # start single stepping if pattern match
        if (
            self._single_step_re
            and not self.is_single_stepping
            and self._single_step_re.search(line)
        ):
            flags = "i" if (self._single_step_re.flags & re.IGNORECASE) else ""
            logger.log("ADMIN", f"break search /{self._single_step_re.pattern}/{flags}")
            self.start_single_stepping()

        level = "nextline" if self.is_single_stepping else "logline"
        logger.log(level, "-" * 80)
        logger.log(level, self.monitor.conlog.last_line)

        # check gate
        self._single_step_event.wait()
        if self.is_single_stepping:
            self._single_step_event.clear()

    def repl(self):
        """Admin console read-evaluate-process-loop."""

        while not self.monitor.conlog.is_eof or self.monitor.options.follow:

            self.monitor.ui.update_display()

            prompt = tf2mon.APPNAME
            if self.is_single_stepping:
                prompt += " (single-stepping)"
            prompt += ": "

            if (line := self.monitor.ui.getline(prompt)) is None:
                logger.log("console", "quit eof")
                return

            if line == "":  # enter
                if self.monitor.conlog.is_eof:
                    logger.log("console", f"lineno={self.monitor.conlog.lineno} <EOF>")
                else:
                    logger.trace("step...")
                self._single_step_event.set()
                continue

            logger.log("console", f"line={line!r}")

            cmd = line  # .upper()
            if "quit".find(cmd) == 0:
                logger.log("console", "quit")
                return

            if regex := Regex.search_list(cmd, self.regex_list):
                regex.handler(regex.re_match_obj)
            else:
                logger.error(f"bad admin command {cmd!r}")
