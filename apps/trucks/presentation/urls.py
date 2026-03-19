from django.urls import path

from apps.trucks.presentation.dashboard_views import DashboardAPIView
from apps.trucks.presentation.views import (
    FipeBrandsAPIView,
    FipeModelsAPIView,
    FipeYearsAPIView,
    TruckListCreateAPIView,
    TruckUpdateAPIView,
)

urlpatterns = [
    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),
    path("trucks/", TruckListCreateAPIView.as_view(), name="truck-list-create"),
    path("trucks/<uuid:truck_id>/", TruckUpdateAPIView.as_view(), name="truck-update"),
    path("fipe/brands/", FipeBrandsAPIView.as_view(), name="fipe-brands"),
    path("fipe/brands/<str:brand_id>/models/", FipeModelsAPIView.as_view(), name="fipe-models"),
    path(
        "fipe/brands/<str:brand_id>/models/<str:model_id>/years/",
        FipeYearsAPIView.as_view(),
        name="fipe-years",
    ),
]
