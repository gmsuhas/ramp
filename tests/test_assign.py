import unittest

from ramp.assign import AssignError, assign, stick


class StickTests(unittest.TestCase):
    def test_same_identity_keeps_its_bucket(self):
        self.assertEqual(stick("checkout-v2", "ada"), stick("checkout-v2", "ada"))

    def test_ada_lands_on_the_documented_bucket(self):
        self.assertEqual(stick("checkout-v2", "ada"), 57)

    def test_salt_moves_the_bucket(self):
        self.assertNotEqual(
            stick("checkout-v2", "ada"), stick("checkout-v2", "ada", salt="v2")
        )

    def test_missing_identity_is_refused(self):
        with self.assertRaises(AssignError):
            stick("checkout-v2", "")

    def test_blank_identity_is_refused(self):
        with self.assertRaises(AssignError):
            stick("checkout-v2", "   ")

    def test_blank_flag_is_refused(self):
        with self.assertRaises(AssignError):
            stick("  ", "ada")


class AssignTests(unittest.TestCase):
    def test_zero_ramp_is_all_control(self):
        for identity in ("ada", "bea", "cal", "dee"):
            decision = assign("checkout-v2", identity, 0)
            self.assertEqual(decision["variant"], "control")

    def test_full_ramp_is_all_treatment(self):
        decision = assign("checkout-v2", "ada", 100)
        self.assertEqual(decision["variant"], "treatment")

    def test_bucket_decides_the_boundary(self):
        bucket = stick("checkout-v2", "ada")
        below = assign("checkout-v2", "ada", bucket)
        above = assign("checkout-v2", "ada", bucket + 1)
        self.assertEqual(below["variant"], "control")
        self.assertEqual(above["variant"], "treatment")

    def test_ramp_must_be_a_whole_percentage(self):
        with self.assertRaises(AssignError):
            assign("checkout-v2", "ada", 10.5)
        with self.assertRaises(AssignError):
            assign("checkout-v2", "ada", 101)
        with self.assertRaises(AssignError):
            assign("checkout-v2", "ada", True)
        with self.assertRaises(AssignError):
            assign("checkout-v2", "ada", False)
