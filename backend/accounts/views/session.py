from django.contrib.auth import authenticate, logout
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import LoginSerializer
from audit.services import create_audit_record


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].strip().casefold()
        user = authenticate(
            request, username=email, password=serializer.validated_data['password'],
        )
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=401)
        if not user.is_active or user.email_verified_at is None:
            return Response({'detail': 'Account is not available.'}, status=403)
        request.session.flush()
        request.session['pre_mfa_user_id'] = str(user.id)
        request.session.cycle_key()
        return Response({'detail': 'MFA required.'}, status=status.HTTP_202_ACCEPTED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        create_audit_record(
            actor=request.user, action='auth.logout', resource_type='User',
            resource_id=request.user.id,
            correlation_id=getattr(request, 'correlation_id', ''),
        )
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'id': str(request.user.id), 'email': request.user.email})
