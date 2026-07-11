"""Unit tests for generate_svg.py."""

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from generate_svg import calculate_uptime, fetch_stats, generate_svg


class TestCalculateUptime(unittest.TestCase):
    """Tests for uptime calculation from created_at timestamp."""

    @patch("generate_svg.datetime")
    def test_uptime_basic(self, mock_dt):
        mock_dt.now.return_value = datetime(2025, 7, 11, 12, 0, 0, tzinfo=timezone.utc)
        mock_dt.strptime = datetime.strptime
        result = calculate_uptime("2020-10-03T15:14:30Z")
        self.assertEqual(result, "4 years, 9 months, 8 days")

    @patch("generate_svg.datetime")
    def test_uptime_exact_anniversary(self, mock_dt):
        mock_dt.now.return_value = datetime(
            2023, 10, 3, 15, 14, 30, tzinfo=timezone.utc
        )
        mock_dt.strptime = datetime.strptime
        result = calculate_uptime("2020-10-03T15:14:30Z")
        self.assertEqual(result, "3 years, 0 months, 0 days")

    @patch("generate_svg.datetime")
    def test_uptime_day_borrow(self, mock_dt):
        # March 1 - created Jan 31: should borrow from Feb
        mock_dt.now.return_value = datetime(2022, 3, 1, 0, 0, 0, tzinfo=timezone.utc)
        mock_dt.strptime = datetime.strptime
        result = calculate_uptime("2022-01-31T00:00:00Z")
        # Jan31 -> Feb28 = 28 days (1 month), Feb28 -> Mar1 = 1 day
        self.assertEqual(result, "0 years, 1 months, 1 days")

    @patch("generate_svg.datetime")
    def test_uptime_month_borrow(self, mock_dt):
        # Jan 15, 2022 - created March 20, 2021
        mock_dt.now.return_value = datetime(2022, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        mock_dt.strptime = datetime.strptime
        result = calculate_uptime("2021-03-20T00:00:00Z")
        # 0 years, 9 months, 26 days
        self.assertEqual(result, "0 years, 9 months, 26 days")

    @patch("generate_svg.datetime")
    def test_uptime_leap_year(self, mock_dt):
        # March 1, 2024 (leap year) - created Feb 28, 2024
        mock_dt.now.return_value = datetime(2024, 3, 1, 0, 0, 0, tzinfo=timezone.utc)
        mock_dt.strptime = datetime.strptime
        result = calculate_uptime("2024-02-28T00:00:00Z")
        self.assertEqual(result, "0 years, 0 months, 2 days")


class TestFetchStats(unittest.TestCase):
    """Tests for GitHub API fetching."""

    @patch("generate_svg.github_api_get")
    def test_fetch_stats_single_page(self, mock_get):
        user_data = {
            "public_repos": 15,
            "followers": 10,
            "following": 5,
            "created_at": "2020-10-03T15:14:30Z",
        }
        repos_data = [
            {"stargazers_count": 10},
            {"stargazers_count": 20},
            {"stargazers_count": 5},
        ]

        mock_get.side_effect = [user_data, repos_data]

        result = fetch_stats()
        self.assertEqual(result["repos"], 15)
        self.assertEqual(result["stars"], 35)
        self.assertEqual(result["followers"], 10)
        self.assertEqual(result["following"], 5)
        self.assertEqual(result["created_at"], "2020-10-03T15:14:30Z")

    @patch("generate_svg.github_api_get")
    def test_fetch_stats_pagination(self, mock_get):
        user_data = {
            "public_repos": 150,
            "followers": 3,
            "following": 1,
            "created_at": "2020-10-03T15:14:30Z",
        }
        # First page: 100 repos
        page1 = [{"stargazers_count": 1}] * 100
        # Second page: 50 repos
        page2 = [{"stargazers_count": 2}] * 50

        mock_get.side_effect = [user_data, page1, page2]

        result = fetch_stats()
        self.assertEqual(result["repos"], 150)
        self.assertEqual(result["stars"], 100 * 1 + 50 * 2)  # 200

    @patch("generate_svg.github_api_get")
    def test_fetch_stats_no_repos(self, mock_get):
        user_data = {
            "public_repos": 0,
            "followers": 0,
            "following": 0,
            "created_at": "2020-10-03T15:14:30Z",
        }
        mock_get.side_effect = [user_data, []]

        result = fetch_stats()
        self.assertEqual(result["repos"], 0)
        self.assertEqual(result["stars"], 0)


class TestGenerateSvg(unittest.TestCase):
    """Tests for SVG generation."""

    def setUp(self):
        self.stats = {
            "repos": 32,
            "stars": 140,
            "followers": 2,
            "following": 0,
            "created_at": "2020-10-03T15:14:30Z",
        }

    @patch("generate_svg.calculate_uptime", return_value="5 years, 0 months, 0 days")
    def test_svg_contains_dynamic_repos(self, _):
        svg = generate_svg(self.stats)
        self.assertIn(">32</tspan>", svg)

    @patch("generate_svg.calculate_uptime", return_value="5 years, 0 months, 0 days")
    def test_svg_contains_dynamic_stars(self, _):
        svg = generate_svg(self.stats)
        self.assertIn(">140</tspan>", svg)

    @patch("generate_svg.calculate_uptime", return_value="5 years, 0 months, 0 days")
    def test_svg_contains_dynamic_followers(self, _):
        svg = generate_svg(self.stats)
        self.assertIn(">2</tspan>", svg)

    @patch("generate_svg.calculate_uptime", return_value="5 years, 0 months, 0 days")
    def test_svg_contains_dynamic_following(self, _):
        svg = generate_svg(self.stats)
        self.assertIn('<tspan fill="#e5c07b">0</tspan>', svg)

    @patch("generate_svg.calculate_uptime", return_value="4 years, 9 months, 8 days")
    def test_svg_contains_uptime(self, _):
        svg = generate_svg(self.stats)
        self.assertIn("4 years, 9 months, 8 days", svg)

    @patch("generate_svg.calculate_uptime", return_value="5 years, 0 months, 0 days")
    def test_svg_structure_valid(self, _):
        svg = generate_svg(self.stats)
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.strip().endswith("</svg>"))

    @patch("generate_svg.calculate_uptime", return_value="5 years, 0 months, 0 days")
    def test_svg_contains_hardcoded_values(self, _):
        svg = generate_svg(self.stats)
        # ASCII art
        self.assertIn("~/projects", svg)
        # Contact
        self.assertIn("mauryasde@gmail.com", svg)
        # Bio
        self.assertIn("Identity theft is not a joke, Jim!", svg)
        # Username
        self.assertIn("sdeonvacation@github ~ neofetch", svg)
        # Color palette
        self.assertIn('fill="#e06c75"', svg)
        self.assertIn('fill="#c678dd"', svg)

    @patch("generate_svg.calculate_uptime", return_value="5 years, 0 months, 0 days")
    def test_svg_dimensions(self, _):
        svg = generate_svg(self.stats)
        self.assertIn('width="850"', svg)
        self.assertIn('height="480"', svg)

    @patch("generate_svg.calculate_uptime", return_value="5 years, 0 months, 0 days")
    def test_svg_stat_colors(self, _):
        """Repos/Followers use green, Stars/Following use yellow."""
        svg = generate_svg(self.stats)
        # Repos value in green
        self.assertIn('<tspan fill="#98c379">32</tspan>', svg)
        # Stars value in yellow
        self.assertIn('<tspan fill="#e5c07b">140</tspan>', svg)
        # Followers in green
        self.assertIn('<tspan fill="#98c379">2</tspan>', svg)
        # Following in yellow
        self.assertIn('<tspan fill="#e5c07b">0</tspan>', svg)


class TestGithubApiGet(unittest.TestCase):
    """Tests for API request construction."""

    @patch("generate_svg.urllib.request.urlopen")
    @patch("generate_svg.os.environ", {"GITHUB_TOKEN": "test-token-123"})
    def test_auth_header_when_token_present(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"login": "test"}'
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        from generate_svg import github_api_get

        github_api_get("/users/test")

        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_header("Authorization"), "Bearer test-token-123")

    @patch("generate_svg.urllib.request.urlopen")
    @patch("generate_svg.os.environ", {})
    def test_no_auth_header_without_token(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"login": "test"}'
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        from generate_svg import github_api_get

        github_api_get("/users/test")

        req = mock_urlopen.call_args[0][0]
        self.assertIsNone(req.get_header("Authorization"))

    @patch("generate_svg.urllib.request.urlopen")
    @patch("generate_svg.os.environ", {})
    def test_correct_url_construction(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"[]"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        from generate_svg import github_api_get

        github_api_get("/users/sdeonvacation/repos?per_page=100")

        req = mock_urlopen.call_args[0][0]
        self.assertEqual(
            req.full_url,
            "https://api.github.com/users/sdeonvacation/repos?per_page=100",
        )


if __name__ == "__main__":
    unittest.main()
