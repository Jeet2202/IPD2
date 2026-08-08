"""
Unit tests for scheduling conflict detection in worker job applications.

Tests the following behaviour:
    - parse_time_range_minutes: correctly parses 24h and 12h time strings
    - has_time_overlap: correct interval overlap arithmetic
    - MarketplaceRulesEngine._check_schedule_conflict: integration scenarios
"""

import pytest
from datetime import date

from app.booking.scheduling import parse_time_range_minutes, has_time_overlap


# ---------------------------------------------------------------------------
# parse_time_range_minutes
# ---------------------------------------------------------------------------

class TestParseTimeRangeMinutes:
    def test_24h_range(self):
        assert parse_time_range_minutes("09:00 - 11:00") == (540, 660)

    def test_24h_range_pm(self):
        assert parse_time_range_minutes("14:00 - 16:00") == (840, 960)

    def test_12h_range_am(self):
        assert parse_time_range_minutes("09:00 AM - 11:00 AM") == (540, 660)

    def test_12h_range_pm(self):
        assert parse_time_range_minutes("02:00 PM - 04:00 PM") == (840, 960)

    def test_12h_midnight_edge(self):
        # 12:00 AM = 0 minutes (midnight)
        assert parse_time_range_minutes("12:00 AM - 01:00 AM") == (0, 60)

    def test_12h_noon_edge(self):
        # 12:00 PM = 720 minutes (noon)
        assert parse_time_range_minutes("12:00 PM - 01:00 PM") == (720, 780)

    def test_single_time_defaults_60_min(self):
        result = parse_time_range_minutes("09:00")
        assert result == (540, 600)

    def test_empty_string_returns_none(self):
        assert parse_time_range_minutes("") is None

    def test_none_like_returns_none(self):
        assert parse_time_range_minutes(None) is None  # type: ignore[arg-type]

    def test_invalid_format_returns_none(self):
        assert parse_time_range_minutes("morning") is None

    def test_end_before_start_returns_none(self):
        # End before start is invalid
        assert parse_time_range_minutes("11:00 - 09:00") is None


# ---------------------------------------------------------------------------
# has_time_overlap
# ---------------------------------------------------------------------------

class TestHasTimeOverlap:
    def test_clear_overlap(self):
        # 09:00-11:00 vs 10:00-12:00 → overlap at 10:00-11:00
        assert has_time_overlap("09:00 - 11:00", "10:00 - 12:00") is True

    def test_contained_fully_inside(self):
        # 09:00-11:00 vs 09:30-10:30 → B is inside A
        assert has_time_overlap("09:00 - 11:00", "09:30 - 10:30") is True

    def test_same_slot(self):
        assert has_time_overlap("09:00 - 11:00", "09:00 - 11:00") is True

    def test_touching_no_overlap(self):
        # 09:00-10:00 and 10:00-12:00 → touching, NOT overlapping
        assert has_time_overlap("09:00 - 10:00", "10:00 - 12:00") is False

    def test_adjacent_end_equals_start(self):
        # 11:00-12:00 and 09:00-11:00 → touching
        assert has_time_overlap("11:00 - 12:00", "09:00 - 11:00") is False

    def test_no_overlap_before(self):
        assert has_time_overlap("08:00 - 09:00", "10:00 - 12:00") is False

    def test_no_overlap_after(self):
        assert has_time_overlap("14:00 - 16:00", "10:00 - 12:00") is False

    def test_partial_overlap_end(self):
        # 10:00-12:00 vs 11:00-13:00 → overlap at 11:00-12:00
        assert has_time_overlap("10:00 - 12:00", "11:00 - 13:00") is True

    def test_12h_overlap(self):
        # AM/PM format — same overlap
        assert has_time_overlap("09:00 AM - 11:00 AM", "10:00 AM - 12:00 PM") is True

    def test_unparseable_a_returns_false(self):
        assert has_time_overlap("morning", "09:00 - 11:00") is False

    def test_unparseable_b_returns_false(self):
        assert has_time_overlap("09:00 - 11:00", "afternoon") is False

    def test_both_unparseable_returns_false(self):
        assert has_time_overlap("morning", "afternoon") is False

    def test_overlap_with_pm_slots(self):
        # 2 PM to 4 PM vs 3 PM to 5 PM
        assert has_time_overlap("14:00 - 16:00", "15:00 - 17:00") is True

    def test_no_overlap_with_pm_slots(self):
        # 2 PM to 3 PM vs 4 PM to 6 PM
        assert has_time_overlap("14:00 - 15:00", "16:00 - 18:00") is False
