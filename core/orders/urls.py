from django.urls import path

from .views import (
    CreateOrderView,
    OrderListView,
    OrderDetailView,
    VerifyPaymentView,
    StartPaymentView,
)


app_name = 'orders'

urlpatterns = [
    path(
        "create/",
        CreateOrderView.as_view(),
        name="create-order"
    ),

    path(
        "",
        OrderListView.as_view(),
        name="order-list"
    ),

    path(
        "<int:pk>/",
        OrderDetailView.as_view(),
        name="order-detail"
    ),
    path(
        "<int:order_id>/start-payment/",
        StartPaymentView.as_view(),
        name="start-payment"
    ),
    path(
        "verify-payment/",
        VerifyPaymentView.as_view(),
        name="verify-payment"
    ),
]