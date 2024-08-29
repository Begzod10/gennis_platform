from django.urls import path, include

urlpatterns = [
    path('teachers/', include('transfer.api.gennis.teacher.urls')),
    path('capital/', include('transfer.api.gennis.capital.urls')),
    path('books/', include('transfer.api.gennis.books.urls')),
    path('users/', include('transfer.api.gennis.user.urls')),
    path('rooms/', include('transfer.api.gennis.room.urls')),
    path('time_table/', include('transfer.api.gennis.time_table.urls')),

]
