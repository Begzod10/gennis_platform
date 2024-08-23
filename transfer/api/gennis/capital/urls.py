from django.urls import path
from .views import OldCapitalCreateView

urlpatterns = [
    path('old_capital_create/', OldCapitalCreateView.as_view(), name='old-capital-create'),

]
