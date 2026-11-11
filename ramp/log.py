"""The small part of an event log this tool needs to read back.

A line is a clock, a name, a phase, and key=value attributes, which is the
shape otl writes and reads. ramp only asks three things of it: which span
opened, which flag event landed on it, and whether it failed.
"""

from __future__ import annotations


class LogError(ValueError):
    """A line could not be read as an event."""


class Event:
    def __init__(self, name, phase, attributes):
        self.name = name
        self.phase = phase
        self.attributes = attributes


PHASES = ("start", "stop", "event", "fail")


def parse_log(text):
    events = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        event = _parse_line(line, line_no)
        if event is not None:
            events.append(event)
    return events


def _parse_line(line, line_no):
    text = line.strip()
    if not text or text.startswith("#"):
        return None
    words = text.split()
    if len(words) < 2:
        raise LogError("line %d needs a clock and a name" % line_no)
    body = words[1:]
    phase_at = [
        index for index, word in enumerate(body) if word in PHASES and "=" not in word
    ]
    if len(phase_at) != 1:
        raise LogError("line %d needs exactly one phase" % line_no)
    phase = body[phase_at[0]]
    name = " ".join(body[: phase_at[0]])
    if not name:
        raise LogError("line %d has no event name" % line_no)
    attributes = {}
    for word in body[phase_at[0] + 1 :]:
        key, equals, value = word.partition("=")
        if not equals or not key:
            raise LogError("line %d: expected key=value, got %r" % (line_no, word))
        attributes[key] = value
    return Event(name, phase, attributes)
