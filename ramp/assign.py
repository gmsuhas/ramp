"""Pick a variant for one request, the same way every time.

The stick is a number from 0 to 99 taken from the flag, the salt, and the
identity, so the same customer lands on the same number for as long as the
flag keeps its salt. The ramp is a percentage. A request whose number falls
under it gets the treatment. Everyone else gets the control.

There is no third answer. An identity that is missing, or a ramp that is
not a whole number from 0 to 100, is a reason to refuse rather than a
reason to guess.
"""

from __future__ import annotations

import hashlib


class AssignError(ValueError):
    """The flag, the ramp, or the identity could not be used."""


def stick(flag, identity, salt=""):
    """Return the stable 0-99 bucket for this identity on this flag."""
    if not isinstance(flag, str) or not flag.strip():
        raise AssignError("a flag needs a name")
    if not isinstance(identity, str) or not identity.strip():
        raise AssignError("an identity is required, not assumed")
    text = "%s\0%s\0%s" % (flag, salt, identity)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100


def assign(flag, identity, ramp, salt=""):
    """Return the flag, the variant, the bucket, and the ramp.

    `ramp` is the percentage of identities that receive the treatment.
    0 sends everyone to the control and 100 sends everyone to the treatment.
    A bucket under the ramp is treatment. The bucket itself is not.
    """
    if isinstance(ramp, bool) or not isinstance(ramp, int):
        raise AssignError("ramp must be a whole number from 0 to 100, got %r" % ramp)
    if not 0 <= ramp <= 100:
        raise AssignError("ramp must be from 0 to 100, got %r" % ramp)
    bucket = stick(flag, identity, salt)
    variant = "treatment" if bucket < ramp else "control"
    return {"flag": flag, "variant": variant, "bucket": bucket, "ramp": ramp}
