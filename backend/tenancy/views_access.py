from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from audit.services import create_audit_record
from tenancy.capabilities import role_allows
from tenancy.models import Invitation, TenantMembership, TenantMFAPolicy
from tenancy.permissions import HasActiveTenant
from tenancy.serializers_access import (
    InvitationAcceptSerializer,
    InvitationSerializer,
    MembershipSerializer,
    MFAPolicySerializer,
)
from tenancy.services.invitations import accept_invitation, create_invitation


class InvitationListCreateView(generics.ListCreateAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated, HasActiveTenant]

    def get_queryset(self):
        return Invitation.objects.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        membership = TenantMembership.objects.get(
            user=self.request.user, tenant=self.request.tenant, is_active=True,
        )
        if not role_allows(membership.role, 'users.manage'):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Capability users.manage is required.')
        invitation = create_invitation(
            tenant=self.request.tenant, invited_by=self.request.user,
            email=serializer.validated_data['email'], role=serializer.validated_data['role'],
        )
        serializer.instance = invitation
        create_audit_record(
            actor=self.request.user, action='invitation.created', resource_type='Invitation',
            resource_id=invitation.id, tenant_id=self.request.tenant.id,
            correlation_id=getattr(self.request, 'correlation_id', ''),
            detail={'role': invitation.role},
        )


class InvitationAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InvitationAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitation = accept_invitation(raw=serializer.validated_data['token'], user=request.user)
        if invitation is None:
            return Response({'detail': 'Invalid or expired invitation.'}, status=400)
        create_audit_record(
            actor=request.user, action='invitation.accepted', resource_type='Invitation',
            resource_id=invitation.id, tenant_id=invitation.tenant_id,
            correlation_id=getattr(request, 'correlation_id', ''),
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class MembershipListView(generics.ListAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated, HasActiveTenant]

    def get_queryset(self):
        return TenantMembership.objects.filter(tenant=self.request.tenant).select_related('user')


class MembershipDetailView(generics.UpdateAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated, HasActiveTenant]
    http_method_names = ['patch']

    def get_queryset(self):
        membership = TenantMembership.objects.get(
            user=self.request.user, tenant=self.request.tenant, is_active=True,
        )
        if not role_allows(membership.role, 'users.manage'):
            return TenantMembership.objects.none()
        return TenantMembership.objects.filter(tenant=self.request.tenant)

    def perform_update(self, serializer):
        target = self.get_object()
        new_role = serializer.validated_data.get('role', target.role)
        new_active = serializer.validated_data.get('is_active', target.is_active)
        if target.role == 'admin' and (new_role != 'admin' or not new_active):
            admins = TenantMembership.objects.filter(
                tenant=self.request.tenant, role='admin', is_active=True,
            ).count()
            if admins <= 1:
                from rest_framework.exceptions import ValidationError
                raise ValidationError('The last active administrator cannot be removed.')
        serializer.save()


class MFAPolicyView(generics.RetrieveUpdateAPIView):
    serializer_class = MFAPolicySerializer
    permission_classes = [IsAuthenticated, HasActiveTenant]
    http_method_names = ['get', 'patch']

    def get_object(self):
        membership = TenantMembership.objects.get(
            user=self.request.user, tenant=self.request.tenant, is_active=True,
        )
        if self.request.method == 'PATCH' and not role_allows(
            membership.role, 'organization.manage',
        ):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Capability organization.manage is required.')
        return TenantMFAPolicy.objects.get_or_create(tenant=self.request.tenant)[0]
