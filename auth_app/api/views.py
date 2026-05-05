from django.contrib.auth import authenticate, get_user_model

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from quiz_management_app.models import User
from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            data = {
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.pk
            }
            return Response({"detail": "User created successfully!"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      #login view, die JWT-Token in Cookies speichert  
class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Führt den Login durch, erzeugt Access- und Refresh-Token
    und speichert beide als HttpOnly-Cookies in der Response.
    """

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
        except:
            return Response(
                {"detail": "Ungültige Anmeldedaten."},
                status=status.HTTP_400_BAD_REQUEST
            )
        refresh = response.data.get('refresh')
        access = response.data.get('access')
        

       

        response.set_cookie(
            key='access_token',
            value=access,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        response.set_cookie(
            key='refresh_token',    
            value=refresh,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        User = get_user_model()
        user = User.objects.get(username=request.data.get('username'))
    


        response.data = {"detail": "Login successfully!", "user": {"id": user.id, "username": user.username, "email": user.email   }}
        return response
    
    
class CookieRefreshView(TokenRefreshView):
    """
    Aktualisiert den Access Token mithilfe eines im Cookie gespeicherten Refresh Tokens
    und setzt den neuen Access Token als HttpOnly-Cookie in der Response.
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        #refresh token nicht im Cookie gefunden
        if refresh_token is None:
            return Response({"detail": "Refresh token not provided"}, status=status.HTTP_401_UNAUTHORIZED)   
        
        serializer =self.get_serializer(data={'refresh': refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except:    
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
        
        access_token = serializer.validated_data.get('access')
        response = Response({"detail": "Token refreshed"})
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        return response
    
class CookieDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    """
    Führt den Logout durch, indem die Access- und Refresh-Token-Cookies gelöscht werden.
    """

    def post(self, request, *args, **kwargs):
        response = Response({"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid"})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
        