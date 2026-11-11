"""Read the lines back and say whether the treatment is the one failing.

A `feature_flag` event marks the span that is open around it, which
is the innermost open span, the same span a trace would attach the event
to. The mark belongs to one flag. A later `fail` of that span counts
against the variant. A request with no flag line is left out: an unknown
variant is not the control.
"""

from __future__ import annotations


class Tally:
    def __init__(self):
        self.rows = {}

    def add(self, variant, failed):
        row = self.rows.setdefault(variant, {"requests": 0, "failed": 0})
        row["requests"] += 1
        if failed:
            row["failed"] += 1


def summarize(events, flag):
    """Pair one flag's events with the spans they landed on.

    The mark goes on the innermost open span. A flag event with no span
    open around it is ignored, and so is a flag other than the one named.
    Two rollouts in one log are never pooled into one table.
    """
    tally = Tally()
    open_spans = []
    for event in events:
        if event.phase == "start":
            open_spans.append(_Span(event.name))
            continue
        if event.phase in ("stop", "fail"):
            span = _take(open_spans, event.name)
            if span is not None and span.variant is not None:
                tally.add(span.variant, failed=(event.phase == "fail"))
            continue
        if event.name != "feature_flag" or not open_spans:
            continue
        if event.attributes.get("feature_flag.key") != flag:
            continue
        variant = event.attributes.get("feature_flag.result.variant")
        if variant not in ("control", "treatment"):
            continue
        open_spans[-1].variant = variant
    return tally.rows


def render(rows):
    lines = []
    for variant in ("control", "treatment"):
        row = rows.get(variant)
        if row is None:
            continue
        requests = row["requests"]
        failed = row["failed"]
        rate = (100.0 * failed / requests) if requests else 0.0
        lines.append(
            "%-10s %4d requests  %4d failed  %5.1f%%"
            % (variant, requests, failed, rate)
        )
    if not lines:
        return "no flagged requests\n"
    return "\n".join(lines) + "\n"


class _Span:
    def __init__(self, name):
        self.name = name
        self.variant = None


def _take(open_spans, name):
    for index in range(len(open_spans) - 1, -1, -1):
        if open_spans[index].name == name:
            return open_spans.pop(index)
    return None
