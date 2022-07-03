from django.urls import path

from api import views

urlpatterns = [
    path("riskattribution", views.risk_attribution),
    path("backtest", views.alator_backtest),
    path("incomesim", views.antevorta_simulation),
    path("pricecoveragesuggest", views.price_coverage_suggest),
    path("hypotheticaldrawdown", views.hypothetical_drawdown_simulation),
]
