import unittest

from ramp.assign import assign
from ramp.line import format_line
from ramp.log import LogError, parse_log


class LineTests(unittest.TestCase):
    def test_line_reads_back_as_a_flag_event(self):
        decision = assign("checkout-v2", "ada", 10)
        line = format_line("12:01:02.100", decision)
        event = parse_log(line)[0]
        self.assertEqual(event.name, "feature_flag")
        self.assertEqual(event.phase, "event")
        self.assertEqual(event.attributes["feature_flag.key"], "checkout-v2")
        self.assertEqual(event.attributes["feature_flag.result.variant"], "control")
        self.assertEqual(event.attributes["bucket"], "57")

    def test_a_comment_and_a_blank_line_are_skipped(self):
        events = parse_log("# note\n\n12:00:00.000 checkout start\n")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].phase, "start")

    def test_a_line_with_two_phases_is_refused(self):
        with self.assertRaises(LogError):
            parse_log("12:00:00.000 checkout start stop\n")

    def test_a_word_after_the_phase_must_be_an_attribute(self):
        with self.assertRaises(LogError):
            parse_log("12:00:00.000 checkout start customer\n")
