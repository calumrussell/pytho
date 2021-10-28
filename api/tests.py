from django.test import TestCase, Client
import json
from unittest.mock import patch
import pandas as pd
import numpy as np
import datetime

from helpers.prices.data import FakeData
from helpers.sample.sample import Sample

from .models import Coverage, RealReturns
from helpers.prices import InvestPySource


class TestPortfolioSimulator(TestCase):
    def setUp(self):
        self.c = Client()
        for i in range(100):
            instance = RealReturns.objects.create(
                id=100 + i,
                country="United States",
                year=1900 + i,
                eq_tr=0.09,
                bond_tr=0.09,
                bill_rate=0.09,
                inf=0.09,
                currency=0.09,
                eq_tr_local=0.09,
                bond_tr_local=0.08,
                eq_tr_usd=0.09,
                bond_tr_usd=0.09,
            )
            instance.save()
        for i in range(100):
            instance = RealReturns.objects.create(
                id=200 + i,
                country="United Kingdom",
                year=1900 + i,
                eq_tr=0.09,
                bond_tr=0.09,
                bill_rate=0.09,
                inf=0.09,
                currency=0.09,
                eq_tr_local=0.07,
                bond_tr_local=0.06,
                eq_tr_usd=0.09,
                bond_tr_usd=0.09,
            )
            instance.save()
        for i in range(100):
            instance = RealReturns.objects.create(
                id=300 + i,
                country="France",
                year=1900 + i,
                eq_tr=0.09,
                bond_tr=0.09,
                bill_rate=0.09,
                inf=0.09,
                currency=0.09,
                eq_tr_local=0.05,
                bond_tr_local=0.04,
                eq_tr_usd=0.09,
                bond_tr_usd=0.09,
            )
            instance.save()
        for i in range(100):
            instance = RealReturns.objects.create(
                id=400 + i,
                country="Germany",
                year=1900 + i,
                eq_tr=0.09,
                bond_tr=0.09,
                bill_rate=0.09,
                inf=0.09,
                currency=0.09,
                eq_tr_local=0.03,
                bond_tr_local=0.02,
                eq_tr_usd=0.09,
                bond_tr_usd=0.09,
            )
            instance.save()
        return

    def test_that_simulation_is_idempotent_with_countries_provided(self):

        weights = []
        weights.append([0.9, 0.1, 0.0, 0.0])
        weights.append([0.9, 0.1, 0.0, 0.0])
        sim_data = [
            Sample(country="France", start=1919, end=1958),
            Sample(country="United Kingdom", start=1935, end=1974),
            Sample(country="United Kingdom", start=1916, end=1955),
            Sample(country="Germany", start=1943, end=1982),
        ]

        req = {
            "weights": weights,
            "sim_data": sim_data,
            "sim_position": 2,
        }

        response = self.c.post(
            "/api/portfoliosim", req, content_type="application/json"
        )
        response_cagr = response.json()["simportfolio"]["cagr"]

        response1 = self.c.post(
            "/api/portfoliosim", req, content_type="application/json"
        )
        response1_cagr = response1.json()["simportfolio"]["cagr"]

        self.assertTrue(response_cagr == response1_cagr)
        return

    def test_error_conditions(self):

        sim_data = [
            Sample(country="France", start=1919, end=1958),
            Sample(country="United Kingdom", start=1935, end=1974),
            Sample(country="United Kingdom", start=1916, end=1955),
            Sample(country="Germany", start=1943, end=1982),
        ]

        ##Sim_data but no sim_position
        req = {
            "weights": [[1, 0, 0, 0]],
            "sim_data": sim_data,
        }
        response = self.c.post(
            "/api/portfoliosim", req, content_type="application/json"
        )
        self.assertTrue(response.status_code == 400)

        ##Sim_position but no sim_data
        req1 = {"sim_position": 2, "weights": [[1, 0, 0, 0], [1, 0, 0, 0]]}
        response1 = self.c.post(
            "/api/portfoliosim", req1, content_type="application/json"
        )
        self.assertTrue(response1.status_code == 400)

        ##Different length sim_position and sim_weights
        req2 = {
            "sim_position": 3,
            "weights": [[1, 0, 0, 0], [1, 0, 0, 0]],
            "sim_data": sim_data,
        }
        response2 = self.c.post(
            "/api/portfoliosim", req2, content_type="application/json"
        )
        self.assertTrue(response2.status_code == 400)
        return

    def test_main_simulation_flow(self):
        weights = []
        sim_data = None

        for i in range(30):
            weights.append([0.9, 0.1, 0.0, 0.0])

            if sim_data:
                req = {
                    "weights": weights,
                    "sim_data": sim_data,
                    "sim_position": i + 1,
                }
            else:
                req = {
                    "weights": weights,
                    "sim_position": i + 1,
                }

            response = self.c.post(
                "/api/portfoliosim", req, content_type="application/json"
            )
            if not sim_data:
                sim_data = response.json()["sim_data"]
        return


def create_fake_risk_attribution_data(obj):
    obj.c = Client()
    instance = Coverage.objects.create(
        id=666,
        country_name="united_states",
        name="S&P 500",
        security_type="index",
    )
    instance.save()
    instance = Coverage.objects.create(
        id=667,
        country_name="united_kingdom",
        name="FTSE 100",
        security_type="index",
    )
    instance.save()

    obj.fake_data = {}
    obj.fake_data[666] = FakeData.get_investpy(1, 0.01, 100)
    obj.fake_data[667] = FakeData.get_investpy(2, 0.02, 100)
    return


def risk_attribution_route_builder(query_string):
    all_base_routes = [
        "bootstrapriskattribution",
        "rollingriskattribution",
        "riskattribution",
    ]
    has_window = [
        5,
        5,
        False,
    ]

    routes = []
    for route, window in zip(all_base_routes, has_window):
        req_route = "/api/" + route + "?" + query_string
        if window:
            req_route += "&window=" + str(window)
        routes.append(req_route)
    return routes


class TestRiskAttributionRoutes(TestCase):
    """
    NOTE: this runs the standard testing for all the risk attribution routes,
    not all of the risk attribution routes need window testing
    """

    def setUp(self):
        create_fake_risk_attribution_data(self)
        return

    @patch("api.views.prices.PriceAPIRequests")
    def test_that_risk_attribution_runs(self, mock_obj):
        instance = mock_obj.return_value
        instance.get.return_value = self.fake_data

        routes = risk_attribution_route_builder(query_string="ind=666&dep=667")
        for r in routes:
            resp = self.c.get(r, content_type="application/json")
            self.assertTrue(resp.status_code == 200)
        return

    @patch("api.views.prices.PriceAPIRequests")
    def test_that_risk_attribution_throws_error_with_no_input(self, mock_obj):
        instance = mock_obj.return_value
        instance.get.return_value = self.fake_data

        routes = risk_attribution_route_builder(query_string="")
        for r in routes:
            resp = self.c.get(r, content_type="application/json")
            self.assertTrue(resp.status_code == 400)
        return

    @patch("api.views.prices.PriceAPIRequests")
    def test_that_risk_attribution_throws_error_with_bad_input(self, mock_obj):
        instance = mock_obj.return_value
        instance.get.return_value = self.fake_data

        routes = risk_attribution_route_builder(query_string="ind=666")
        for r in routes:
            resp = self.c.get(r, content_type="application/json")
            self.assertTrue(resp.status_code == 400)

        routes = risk_attribution_route_builder(query_string="dep=666")
        for r in routes:
            resp = self.c.get(r, content_type="application/json")
            self.assertTrue(resp.status_code == 400)

        routes = risk_attribution_route_builder(query_string="dep=Test&ind=Test")
        for r in routes:
            resp = self.c.get(r, content_type="application/json")
            self.assertTrue(resp.status_code == 400)

        response = self.c.get(
            "/api/bootstrapriskattribution?dep=666&ind=667&window=Test",
            content_type="application/json",
        )
        self.assertTrue(response.status_code == 400)

        response = self.c.get(
            "/api/rollingriskattribution?dep=666&ind=667&window=Test",
            content_type="application/json",
        )
        self.assertTrue(response.status_code == 400)

        return

    @patch("helpers.prices.api.PriceAPIRequest")
    def test_that_risk_attribution_catches_error_with_data_fetch(self, mock_obj):
        instance = mock_obj.return_value
        instance.get.return_value = {}

        routes = risk_attribution_route_builder(query_string="ind=667&dep=666")
        for r in routes:
            resp = self.c.get(r, content_type="application/json")
            self.assertTrue(resp.status_code == 404)
        return

    @patch("api.views.prices.PriceAPIRequests")
    def test_that_bootstrap_risk_attribution_catches_error_with_window_length(
        self, mock_obj
    ):
        instance = mock_obj.return_value
        instance.get.return_value = self.fake_data

        response = self.c.get(
            "/api/bootstrapriskattribution?ind=667&dep=666&window=9999",
            content_type="application/json",
        )
        self.assertTrue(response.status_code == 400)
        return

    @patch("api.views.prices.PriceAPIRequests")
    def test_that_rolling_risk_attribution_catches_error_with_window_length(
        self, mock_obj
    ):
        instance = mock_obj.return_value
        instance.get.return_value = self.fake_data

        response = self.c.get(
            "/api/rollingriskattribution?ind=667&dep=666&window=9999",
            content_type="application/json",
        )
        self.assertTrue(response.status_code == 400)
        return


class TestHistoricalDrawdownEstimator(TestCase):
    def setUp(self):
        self.c = Client()
        instance = Coverage.objects.create(
            id=666,
            country_name="united_states",
            name="S&P 500",
            security_type="index",
        )
        instance.save()
        instance1 = Coverage.objects.create(
            id=1,
            country_name="united_states",
            name="ff3factordaily-MKT-RF",
            security_type="factor",
        )
        instance1.save()
        self.fake_data = {}
        self.fake_data[666] = FakeData.get_investpy(1, 0.1, 1000)
        self.fake_data[1] = FakeData.get_factor(0, 0.1, 100)
        return

    @patch("api.views.prices.PriceAPIRequests")
    def test_that_drawdown_estimator_runs(self, mock_obj):
        instance = mock_obj.return_value
        instance.get.return_value = self.fake_data

        response = self.c.get(
            "/api/hypotheticaldrawdown?ind=1&dep=666", content_type="application/json"
        )
        self.assertTrue(response.status_code == 200)
        return

    @patch("api.views.prices.PriceAPIRequests")
    def test_that_drawdown_estimator_throws_error_with_no_input(self, mock_obj):
        instance = mock_obj.return_value
        instance.get.return_value = self.fake_data

        response = self.c.get(
            "/api/hypotheticaldrawdown", content_type="application/json"
        )
        self.assertTrue(response.status_code == 400)
        return

    @patch("api.views.prices.PriceAPIRequests")
    def test_that_drawdown_estimator_throws_error_with_bad_input(self, mock_obj):
        instance = mock_obj.return_value
        instance.get.return_value = self.fake_data

        response = self.c.get(
            "/api/hypotheticaldrawdown?ind=666", content_type="application/json"
        )
        self.assertTrue(response.status_code == 400)

        response = self.c.get(
            "/api/hypotheticaldrawdown?dep=666", content_type="application/json"
        )
        self.assertTrue(response.status_code == 400)

        response = self.c.get(
            "/api/hypotheticaldrawdown?dep=Test&ind=Test",
            content_type="application/json",
        )
        self.assertTrue(response.status_code == 400)
        return

    @patch("helpers.prices.api.PriceAPIRequest")
    def test_that_drawdown_estimator_catches_error_with_data_fetch(self, mock_obj):
        instance = mock_obj.return_value
        instance.get.return_value = {}

        response = self.c.get(
            "/api/hypotheticaldrawdown?dep=666&ind=1", content_type="application/json"
        )
        self.assertTrue(response.status_code == 404)
        return

    @patch("helpers.prices.api.PriceAPIRequest")
    def test_that_drawdown_estimator_catches_error_when_called_without_factor(
        self, mock_obj
    ):
        instance = mock_obj.return_value
        instance.get.return_value = self.fake_data

        self.fake_data[1] = FakeData.get_investpy(2, 0.2, 50)

        response = self.c.get(
            "/api/hypotheticaldrawdown?dep=666&ind=1", content_type="application/json"
        )
        self.assertTrue(response.status_code == 400)
        return


class TestBacktestPortfolio(TestCase):
    def setUp(self):
        self.c = Client()
        instance = Coverage.objects.create(
            id=666,
            country_name="united_states",
            name="S&P 500",
            security_type="index",
        )
        instance.save()

        self.fake_data = {}
        self.fake_data[666] = FakeData.get_investpy(1, 0.1, 100)
        return

    def test_that_get_fails(self):
        resp = self.c.get("/api/backtest")
        self.assertTrue(resp.status_code == 405)

    @patch("api.views.prices.PriceAPIRequests")
    def test_that_backtest_runs(self, mock_obj):
        instance = mock_obj.return_value
        instance.get.return_value = self.fake_data

        req = {"data": {"assets": [666], "weights": [1]}}
        response = self.c.post("/api/backtest", req, content_type="application/json")
        json_resp = json.loads(response.content.decode("utf-8"))
        self.assertTrue("data" in json_resp)

        data_resp = json_resp["data"]
        self.assertTrue("returns" in data_resp)
        self.assertTrue("cagr" in data_resp)
        self.assertTrue("vol" in data_resp)
        self.assertTrue("maxdd" in data_resp)
        self.assertTrue("cumReturns" in data_resp)
        self.assertTrue("equityCurve" in data_resp)
        self.assertTrue("returnsQuantiles" in data_resp)
        return

    @patch("api.views.prices.PriceAPIRequests")
    def test_that_backtest_throws_error_with_no_input(self, mock_obj):
        instance = mock_obj.return_value
        instance.get.return_value = self.fake_data

        req = {}
        req1 = {"data": {"assets": [], "weights": []}}

        response = self.c.post("/api/backtest", req, content_type="application/json")
        response1 = self.c.post("/api/backtest", req1, content_type="application/json")
        self.assertTrue(response.status_code == 400)
        self.assertTrue(response1.status_code == 404)
        return

    @patch("api.views.prices.PriceAPIRequests")
    def test_that_backtest_throws_error_with_bad_input(self, mock_obj):
        instance = mock_obj.return_value
        instance.get.return_value = self.fake_data

        req = {"data": {"assets": [666], "weights": []}}
        req1 = {"data": {"assets": [], "weights": [1]}}
        req2 = {"data": {"assets": ["bad"], "weights": [1]}}

        response = self.c.post("/api/backtest", req, content_type="application/json")
        response1 = self.c.post("/api/backtest", req1, content_type="application/json")
        response2 = self.c.post("/api/backtest", req2, content_type="application/json")
        self.assertTrue(response.status_code == 404)
        self.assertTrue(response1.status_code == 404)
        self.assertTrue(response2.status_code == 404)
        return

    @patch("api.views.prices.PriceAPIRequests")
    def test_that_backtest_throws_error_with_failed_data_fetch(self, mock_obj):
        instance = mock_obj.return_value
        instance.get.return_value = []

        req = {"data": {"assets": [666], "weights": [1]}}

        response = self.c.post("/api/backtest", req, content_type="application/json")
        self.assertTrue(response.status_code == 404)
        return
