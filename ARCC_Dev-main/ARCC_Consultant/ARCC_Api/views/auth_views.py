from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from ..serializers import UserSerializer

def login_page(request):
    # Verificar si la redirección viene de una página protegida
    protected_urls = ['/gen_reporte/', '/stream_reporte/', '/mostrar_reporte/','/api/v1/agent_data/']
    from_protected = any(request.META.get('HTTP_REFERER', '').endswith(url) for url in protected_urls)
    
    if request.method == 'POST':    
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('/gen_reporte/')
        else:
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    
    context = {}
    if from_protected:
        context['message'] = 'No se puede acceder a esta página sin inicio de sesión. Por favor, inicia sesión para continuar.'
    
    return render(request, 'login.html', context)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST) 