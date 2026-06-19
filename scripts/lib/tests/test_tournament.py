import unittest

from unittest.mock import patch
from datetime import datetime, timezone

from lib.tournament import (
    get_tournament_structure,
    get_points_threshold,
    get_points_earned,
    get_round_name,
    tour_in_progress,
)

from ops.format_models import (
    Player,
    Round,
)


class MockDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return datetime(2023, 5, 5, 10, 0, 0).replace(tzinfo=timezone.utc)


class TestTournament(unittest.TestCase):

    """
    a lot of these methods are basically just mapped arrays so these tests aren't super robust
    """

    def test_get_tournament_structure(self):
        cases = [
            (2023, 1000, { "code": "regional-name" }, (9, 6, 3)),
            (1999, 100, { "code": "regional-name" }, None),
        ]

        for case in cases:
            self.assertEqual(get_tournament_structure(*case[:3]), case[3])


    def test_get_points_threshold(self):
        cases = [
            (2023, 500, 128),
            (2024, 500, 128),
            (1999, 120, None),
        ]

        for case in cases:
            self.assertEqual(get_points_threshold(*case[:2]), case[2])


    def test_get_points_earned(self):
        cases = [
            (2023, 500, 32, False, 60),
            (2024, 800, 16, False, 80),
            (2025, 1000, 64, True, 150),
        ]

        for case in cases:
            self.assertEqual(get_points_earned(*case[:4]), case[4])


    def test_get_round_name(self):
        cases = [
            ("10", (8, 5, 0), 16, "10"),
            ("14", (8, 5, 0), 16, "Top 16"),
        ]

        for case in cases:
            self.assertEqual(get_round_name(*case[:3]), case[3])


    @patch('lib.tournament.datetime', MockDatetime)
    def test_tour_in_progress(self):
        cases = [
            (
                { "start": "2023-05-04", "end": "2023-05-05", "region": "North America" },
                {
                    "winner-winner": Player(
                        name='Winner Winner',
                        code='winner-winner',
                        country='',
                        place=1,
                        record={},
                        res=1,
                        cut=True,
                        p2=True,
                        drop=False,
                        points=False,
                        rounds=[
                            Round(
                                round=1,
                                tbl=1,
                                phase=3,
                                opp='loser-loser',
                                res='W',
                                rname='Finals'
                            )
                        ]
                    )
                },
                False,
            ),
            ({ "start": "2023-05-04", "end": "2023-05-05", "region": "North America" }, False, True),
        ]

        for case in cases:
            self.assertEqual(tour_in_progress(case[0], case[1]), case[2])

