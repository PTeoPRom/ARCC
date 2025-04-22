from django.shortcuts import redirect
from django.urls import reverse

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lista de URLs que NO requieren autenticación
        public_urls = [
            '/api/v1/login',  # Sin slash final para coincidir con cualquier variante
            '/api/v1/auth/login',
            '/api/v1/auth/token/refresh',
            '/api/v1/auth/token/verify',
            '/admin',
            '/static',  # Para archivos estáticos
        ]

        # Verificar si la URL actual NO está en la lista de públicas
        if not any(request.path.startswith(url) for url in public_urls):
            if not request.user.is_authenticated:
                # Si el usuario no está autenticado, redirigir al login
                return redirect('/api/v1/login/')

        response = self.get_response(request)
        return response 