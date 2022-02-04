from django.urls import path

from api import views

urlpatterns = [
    path("riskattribution", views.risk_attribution),
    path("backtest", views.backtest_portfolio),
    path("pricecoveragesuggest", views.price_coverage_suggest),
    path("alphavantagesuggest", views.alpha_vantage_suggest),
    path("hypotheticaldrawdown", views.hypothetical_drawdown_simulation),
    path("stockoverview", views.stock_overview)
]
