from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('consensus_engine.urls')),  # defaults to consensus app
    path('consensus/', include('consensus_engine.urls')),
    path('admin/', admin.site.urls),
]
