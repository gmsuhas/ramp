import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from ramp.__main__ import main


class CliTests(unittest.TestCase):
    def test_assign_prints_variant_bucket_and_ramp(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["assign", "checkout-v2", "10", "ada"])
        self.assertEqual(code, 0)
        self.assertEqual(
            out.getvalue().strip(),
            "checkout-v2  variant=control  bucket=57  ramp=10",
        )

    def test_help_exits_clean(self):
        self.assertEqual(main(["-h"]), 0)
        self.assertEqual(main([]), 0)

    def test_a_leading_zero_ramp_is_refused(self):
        self.assertEqual(main(["assign", "checkout-v2", "010", "ada"]), 1)

    def test_a_blank_identity_is_refused(self):
        self.assertEqual(main(["assign", "checkout-v2", "10", "   "]), 1)

    def test_report_needs_a_flag_and_a_file(self):
        self.assertEqual(main(["report", "examples/rollout.log"]), 1)
