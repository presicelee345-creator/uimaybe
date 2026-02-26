from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', include('ncbw.urls')),
]

urlpatterns += staticfiles_urlpatterns()
