from typing import List
from django.test import TestCase
from rorapp.functions.mortality_chit_helper import draw_mortality_chits


class MortalityChitTests(TestCase):
    """
    Ensure that the `draw_mortality_chits` function behaves correctly.
    """

    def test_draw_mortality_chits(self):
        for draw_count in range(1, 11):
            self.do_draw_mortality_chits_test(draw_count)

    def do_draw_mortality_chits_test(self, draw_count):
        all_possible_chit_values = list(range(1, 31))
        all_drawn_chits: List = []
        for i in range(5000):
            chits = draw_mortality_chits(draw_count)
            if draw_count <= 4:
                # If we're drawing 4 or fewer chits, then we should draw at most 10 chits
                # It's possible to draw more than 10 chits, but it's extremely unlikely
                self.assertLessEqual(
                    len(chits), 10, f"drew {chits} on draw count of {draw_count}"
                )
            if draw_count >= 5:
                # The deck contains only 4 "None" chits, so if we're drawing X chits,
                # we are guaranteed to draw at least X-4 chits
                self.assertGreaterEqual(
                    len(chits),
                    draw_count - 4,
                    f"drew {chits} on draw count of {draw_count}",
                )
            all_drawn_chits.extend(chits)
            all_drawn_chits = list(set(all_drawn_chits))

        # With 5000 draws, we should have drawn each chit at least once
        # It's possible to not draw a chit, but it's extremely unlikely
        self.assertEqual(all_possible_chit_values, all_drawn_chits)
