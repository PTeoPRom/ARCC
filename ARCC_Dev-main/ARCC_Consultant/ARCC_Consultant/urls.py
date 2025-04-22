"""
URL configuration for ARCC_Consultant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from ARCC_Api import views
from ARCC_Dashboard import views as dashboard_views

def redirect_to_login(request):
    return redirect('/api/v1/login/')

urlpatterns = [
    path('', redirect_to_login),  # Redirige la ruta raíz a la página de login
    path('admin/', admin.site.urls),
    path('api/v1/agent_data/', include('ARCC_Api.urls')),
    path('api/v1/', include('ARCC_Api.urls')),
    path("gen_reporte/", dashboard_views.generador_reporte_view, name="reporte"),
    path("stream_reporte/<int:case_id>/", dashboard_views.stream_reporte, name="stream_reporte"),
    path("mostrar_reporte/<int:case_id>/", dashboard_views.mostrar_reporte_view, name="mostrar_reporte"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
