"""Write one assignment as a line an event log already understands.

The line is a clock, the event name `flag check`, the phase `event`, and
key=value attributes. A trace reads it as a point in time on the innermost
span that was open around it, so the variant sits on the same span as the
failure.
"""

from __future__ import annotations


def format_line(clock, decision):
    return "%s flag check event flag=%s variant=%s bucket=%d ramp=%d" % (
        clock,
        decision["flag"],
        decision["variant"],
        decision["bucket"],
        decision["ramp"],
    )
