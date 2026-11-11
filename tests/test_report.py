import pathlib
import unittest

from ramp.log import parse_log
from ramp.report import render, summarize

ROLLOUT = (
    pathlib.Path(__file__).parents[1] / "examples" / "rollout.log"
).read_text(encoding="utf-8")
FLAG = "checkout-v2"


class ReportTests(unittest.TestCase):
    def test_failure_lands_on_the_flagged_variant(self):
        rows = summarize(parse_log(ROLLOUT), FLAG)
        self.assertEqual(rows["treatment"], {"requests": 2, "failed": 1})
        self.assertEqual(rows["control"], {"requests": 2, "failed": 0})

    def test_an_unflagged_request_counts_for_neither(self):
        rows = summarize(parse_log(ROLLOUT), FLAG)
        self.assertEqual(
            rows["treatment"]["requests"] + rows["control"]["requests"], 4
        )

    def test_render_states_the_rate(self):
        text = render(summarize(parse_log(ROLLOUT), FLAG))
        self.assertIn("treatment", text)
        self.assertIn("50.0%", text)
        self.assertIn("control", text)
        self.assertIn("0.0%", text)

    def test_a_flag_outside_a_request_counts_nothing(self):
        rows = summarize(
            parse_log("12:00:00.000 flag check event flag=checkout-v2 variant=treatment\n"),
            FLAG,
        )
        self.assertEqual(rows, {})

    def test_a_child_flag_does_not_blame_the_parent(self):
        log = (
            "12:00:00.000 checkout start\n"
            "12:00:00.010 pay start\n"
            "12:00:00.020 flag check event flag=checkout-v2 variant=treatment\n"
            "12:00:00.030 pay stop\n"
            "12:00:00.040 checkout fail error=timeout\n"
        )
        rows = summarize(parse_log(log), FLAG)
        self.assertEqual(rows["treatment"], {"requests": 1, "failed": 0})
        self.assertNotIn("control", rows)

    def test_interleaved_requests_keep_their_own_variant(self):
        log = (
            "12:00:00.000 checkout start customer=a\n"
            "12:00:00.100 checkout start customer=b\n"
            "12:00:00.110 flag check event flag=checkout-v2 variant=treatment\n"
            "12:00:00.120 checkout fail error=timeout customer=b\n"
            "12:00:00.200 flag check event flag=checkout-v2 variant=control\n"
            "12:00:00.210 checkout stop customer=a\n"
        )
        rows = summarize(parse_log(log), FLAG)
        self.assertEqual(rows["treatment"], {"requests": 1, "failed": 1})
        self.assertEqual(rows["control"], {"requests": 1, "failed": 0})

    def test_an_unclosed_span_is_not_counted(self):
        log = (
            "12:00:00.000 checkout start\n"
            "12:00:00.010 flag check event flag=checkout-v2 variant=treatment\n"
        )
        self.assertEqual(summarize(parse_log(log), FLAG), {})

    def test_a_second_flag_is_left_out(self):
        log = (
            "12:00:00.000 checkout start\n"
            "12:00:00.010 flag check event flag=pricing-v1 variant=treatment\n"
            "12:00:00.020 checkout fail error=timeout\n"
        )
        self.assertEqual(summarize(parse_log(log), FLAG), {})

    def test_an_unknown_variant_is_skipped(self):
        log = (
            "12:00:00.000 checkout start\n"
            "12:00:00.010 flag check event flag=checkout-v2 variant=holdout\n"
            "12:00:00.020 checkout fail error=timeout\n"
        )
        self.assertEqual(summarize(parse_log(log), FLAG), {})

    def test_same_name_pairs_with_the_latest_open_span(self):
        log = (
            "12:00:00.000 checkout start\n"
            "12:00:00.010 checkout start\n"
            "12:00:00.020 flag check event flag=checkout-v2 variant=treatment\n"
            "12:00:00.030 checkout stop\n"
            "12:00:00.040 checkout fail error=timeout\n"
        )
        rows = summarize(parse_log(log), FLAG)
        self.assertEqual(rows["treatment"], {"requests": 1, "failed": 0})
