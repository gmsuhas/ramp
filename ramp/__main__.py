"""ramp on the command line.

    python3 -m ramp assign checkout-v2 42 ada
    python3 -m ramp line 12:01:02.100 checkout-v2 42 ada
    python3 -m ramp report checkout-v2 examples/rollout.log
"""

from __future__ import annotations

import sys

from ramp.assign import AssignError, assign
from ramp.line import format_line
from ramp.log import LogError, parse_log
from ramp.report import render, summarize


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        if not args or args[0] in ("-h", "--help"):
            _usage()
            return 0
        command, rest = args[0], args[1:]
        if command == "assign":
            sys.stdout.write(_render_decision(_assignment(rest)) + "\n")
        elif command == "line":
            if len(rest) != 4:
                raise AssignError("expected a clock, a flag, a ramp, and an identity")
            decision = assign(rest[1], rest[3], _percent(rest[2]))
            sys.stdout.write(format_line(rest[0], decision) + "\n")
        elif command == "report":
            if len(rest) != 2:
                raise AssignError("expected a flag name and a log file")
            sys.stdout.write(render(summarize(_read(rest[1]), rest[0])))
        else:
            raise AssignError("unknown command %r" % command)
    except (AssignError, LogError, OSError) as error:
        sys.stderr.write("ramp: %s\n" % error)
        return 1
    return 0


def _assignment(args):
    if len(args) != 3:
        raise AssignError("expected a flag, a ramp, and an identity")
    return assign(args[0], args[2], _percent(args[1]))


def _percent(text):
    if not isinstance(text, str) or len(text) > 1 and text.startswith("0"):
        raise AssignError("ramp must be a whole number from 0 to 100, got %r" % text)
    if not text.isascii() or not text.isdigit():
        raise AssignError("ramp must be a whole number from 0 to 100, got %r" % text)
    return int(text)


def _render_decision(decision):
    return "%s  variant=%s  bucket=%d  ramp=%d" % (
        decision["flag"],
        decision["variant"],
        decision["bucket"],
        decision["ramp"],
    )


def _read(path):
    with open(path, encoding="utf-8") as handle:
        return parse_log(handle.read())


def _usage():
    sys.stderr.write(
        "usage: ramp assign FLAG PERCENT IDENTITY\n"
        "       ramp line   CLOCK FLAG PERCENT IDENTITY\n"
        "       ramp report FLAG FILE\n"
    )


if __name__ == "__main__":
    sys.exit(main())
