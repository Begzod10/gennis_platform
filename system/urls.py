from django.urls import path

from system.Api.get import (

    SystemList,
    SystemRetrieveAPIView
)
from system.Api.update_delete_create import (
    CreateSystem,
    SystemUpdateAPIView,
    SystemDestroyAPIView,
)

urlpatterns = [
    path('systems/', SystemList.as_view(), name='system-list'),
    path('systems/create/', CreateSystem.as_view(), name='system-create'),
    path('systems/<int:pk>/', SystemRetrieveAPIView.as_view(), name='system-detail'),
    path('systems/update/<int:pk>/', SystemUpdateAPIView.as_view(), name='system-update'),
    path('systems/delete/<int:pk>/', SystemDestroyAPIView.as_view(), name='system-delete'),
]
