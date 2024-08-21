from django.urls import path, include

urlpatterns = [
    path('teachers/', include('transfer.api.teacher.urls')),
    path('capital/', include('transfer.api.capital.urls')),
    path('books/', include('transfer.api.books.urls')),
    path('users/', include('transfer.api.user.urls')),
    path('rooms/', include('transfer.api.room.urls')),
    path('time_table/', include('transfer.api.time_table.urls')),

]
