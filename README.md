# ramp

Know the same day whether the new version is the one failing.

**TLDR.** A rollout reaches some customers and not others. When something
breaks, the flag lives in one system and the errors live in another, so the
safe move is to undo the whole launch. ramp writes the version onto the
request and counts the failures. Nothing to install beyond Python 3.9.

Read this if you ship to a fraction of customers and find out too late
which version broke. It will not choose the percentage, and it will not
tell you the new version won. A handful of failures is a reason to look,
not a verdict.

## Try it

```sh
python3 -m ramp assign checkout-v2 10 ada
python3 -m ramp line 12:01:02.100 checkout-v2 10 ada
python3 -m ramp report checkout-v2 examples/rollout.log
```

`assign` prints the flag, the variant, the bucket, and the ramp:

```text
checkout-v2  variant=control  bucket=57  ramp=10
```

`line` prints the same decision as one event:

```text
12:01:02.100 feature_flag event feature_flag.key=checkout-v2 feature_flag.result.variant=control feature_flag.result.reason=split bucket=57 ramp=10
```

That is a clock, a name, a phase, and `key=value` attributes. The event
name `feature_flag`, and the attributes `feature_flag.key` and
`feature_flag.result.variant`, are the ones the
[OpenTelemetry feature-flag registry](https://opentelemetry.io/docs/specs/semconv/registry/attributes/feature-flag/)
records on a span. `feature_flag.result.reason=split` is the registry's
word for a value chosen by pseudorandom assignment, which is what the
bucket is. `bucket` and `ramp` are extra, so the line still says which
number the identity landed on and which percentage was in force.

[otl](https://github.com/gmsuhas/otl) reads the same line as a point in time
on the innermost span that was open around it. Drop it into a request log
and the variant sits on the same span as whatever the request did next.

## The rule

The stick is a number from 0 to 99, taken from the flag name and the
identity. The same customer gets the same number for as long as the flag
keeps its name. The ramp is a percentage: a number under it gets the
treatment, and the rest get the control. 0 is everyone on the control. 100
is everyone on the treatment.

There is no third answer. These are refused rather than guessed:

- an identity that is missing or blank, because an unknown customer is not the control
- a ramp that is not a whole number from 0 to 100, because "about 10" is not a ramp
- a request with no flag line, which the report leaves out instead of filing under a default

A salt on the flag moves every number, which is how a ramp starts over
without renaming the flag. The salt is an argument to `assign` and `stick`.
The command line does not take one: a new salt is a new call from the code
that owns the flag.

## The report

`examples/rollout.log` is a checkout flag at 10%. The buckets in it are the
ones `assign` returns, not a sketch. Two requests took the treatment and
one of them failed. Two took the control and both completed. One request
was never flagged, and it failed: it counts for neither.

```text
control       2 requests     0 failed    0.0%
treatment     2 requests     1 failed   50.0%
```

The report pairs a `feature_flag` event with the innermost span that was
open around it, the same span a trace would attach the event to, and a
`fail` of that span counts against the variant. A second flag in the same
log is ignored.
The report does not fetch a metric and it does not decide the ramp for you.
It says which variant failed, so the next move, roll forward or roll back,
is made on the same day as the deploy.

## Where it sits

[OpenFeature](https://openfeature.dev) is the standard for recording a flag
evaluation, and the vendors behind it already serve the flags. ramp does
not replace either one. It writes the evaluation as the span event the
OpenTelemetry registry already names, and it reads that line back.

[otl](https://github.com/gmsuhas/otl) turns the log into one trace. ramp
does not: it writes a line otl already understands, and a report a person
can read without a collector.

## Tests

```sh
python3 -m unittest discover -s tests
```

## What it deliberately does not do

No flag service, no network, no persistence, and no statistics beyond a
count. It will not choose the ramp, and it will not say the treatment won.
A difference on a handful of requests is a reason to go look, not a result.
