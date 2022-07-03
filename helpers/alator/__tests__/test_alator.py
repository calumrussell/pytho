from typing import Dict
from django.test import SimpleTestCase
from unittest.mock import patch, Mock

from helpers.prices.data import FakeData, InvestPySource

from ..fixedweight import (
    FixedSignalBackTestWithPriceAPI,
)
from ..base import (
    AlatorUnusableInputException,
    AlatorClientInput,
)
from api.models import Coverage


class TestFixedSignalBackTestWithPriceAPI(SimpleTestCase):
    def setUp(self):
        self.data: Dict[int, InvestPySource] = {}
        self.data[0] = FakeData.get_investpy(1, 0.01, 100)
        self.data[1] = FakeData.get_investpy(2, 0.02, 100)
        return

    @patch("helpers.alator.fixedweight.Coverage")
    @patch("helpers.alator.fixedweight.prices.PriceAPIRequests")
    def test_that_errors_from_investpy_are_handled(self, mock_price, mock_coverage):

        fake_query = []
        fake_query.append(Coverage(id=0, ticker="SPY"))
        fake_query.append(Coverage(id=1, ticker="CAC"))

        mock = Mock()
        mock.filter.return_value = fake_query
        mock_coverage.objects = mock

        client_input = AlatorClientInput(
            assets=[1, 2],
            weights=[0.5, 0.5],
        )
        bt = FixedSignalBackTestWithPriceAPI(client_input)

        mock1 = Mock()
        mock1.get_overlapping.side_effect = ValueError("foo")
        mock_price.return_value = mock1
        self.assertRaises(
            AlatorUnusableInputException,
            bt.run,
        )

        mock1.get_overlapping.side_effect = ConnectionError("foo")
        self.assertRaises(
            AlatorUnusableInputException,
            bt.run,
        )

        mock1.get_overlapping.side_effect = IndexError("foo")
        self.assertRaises(
            AlatorUnusableInputException,
            bt.run,
        )

        mock1.get_overlapping.side_effect = RuntimeError("foo")
        self.assertRaises(
            AlatorUnusableInputException,
            bt.run,
        )
        return

    @patch("helpers.alator.fixedweight.Coverage")
    @patch("helpers.alator.fixedweight.prices.PriceAPIRequests")
    def test_that_throws_error_with_valid_but_bad_input(
        self, mock_price, mock_coverage
    ):
        mock = Mock()

        fake_query = []

        mock.filter.return_value = fake_query
        mock_coverage.objects = mock

        mock1 = Mock()
        mock1.get_overlapping.return_value = self.data
        mock_price.return_value = mock1

        client_input = AlatorClientInput(
            assets=[3, 4],
            weights=[0.5, 0.5],
        )
        """ This tests for the user querying assets which aren't in the database Coverage"""
        self.assertRaises(
            AlatorUnusableInputException,
            FixedSignalBackTestWithPriceAPI,
            client_input,
        )

        fake_query.append(Coverage(id=0, ticker="SPY"))
        fake_query.append(Coverage(id=1, ticker="CAC"))

        client_input1 = AlatorClientInput(
            assets=[1, 2],
            weights=[0.5, 0.5],
        )
        mock1.get_overlapping.return_value = []
        mock_price.return_value = mock1
        """ This tests for the user querying assets for which there is a Coverage object but
        which have no data for some reason
        """
        bt = FixedSignalBackTestWithPriceAPI(client_input1)

        self.assertRaises(AlatorUnusableInputException, bt.run)
        return

    @patch("helpers.alator.fixedweight.Coverage")
    @patch("helpers.alator.fixedweight.prices.PriceAPIRequests")
    def test_that_it_can_init(self, mock_price, mock_coverage):
        mock = Mock()

        fake_query = []
        fake_query.append(Coverage(id=0, ticker="SPY"))
        fake_query.append(Coverage(id=1, ticker="CAC"))

        mock.filter.return_value = fake_query
        mock_coverage.objects = mock

        mock1 = Mock()
        mock1.get_overlapping.return_value = self.data
        mock_price.return_value = mock1

        client_input = AlatorClientInput(
            assets=[0, 1],
            weights=[0.5, 0.5],
        )
        bt = FixedSignalBackTestWithPriceAPI(client_input)
        bt.run()
        self.assertTrue(bt.results["mdd"])
        self.assertTrue(bt.results["vol"])
        self.assertTrue(bt.results["cagr"])
        self.assertTrue(bt.results["sharpe"])
        return
