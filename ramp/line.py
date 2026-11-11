"""Write one assignment as a line an event log already understands.

The line is a clock, the event name `feature_flag`, the phase `event`, and
key=value attributes. The name, `feature_flag.key`, and
`feature_flag.result.variant` are the ones the OpenTelemetry feature-flag
convention records on a span. A trace reads the line as a point in time on
the innermost span that was open around it, so the variant sits on the same
span as the failure.
"""

from __future__ import annotations


def format_line(clock, decision):
    return (
        "%s feature_flag event feature_flag.key=%s"
        " feature_flag.result.variant=%s feature_flag.result.reason=split"
        " bucket=%d ramp=%d"
        % (
            clock,
            decision["flag"],
            decision["variant"],
            decision["bucket"],
            decision["ramp"],
        )
    )
