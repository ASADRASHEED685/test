from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from .models import UserDetail
from .serializers import UserDetailSerializer

class UserDetailViewSet(viewsets.ModelViewSet):
    """
    - PUBLIC: create (anyone) -> Send email to admin when a non-admin submits.
    - ADMIN: list, retrieve, update (PUT/PATCH), destroy (soft delete), custom actions:
       - POST /api/users/{id}/hard_delete/  -> permanently delete
       - POST /api/users/{id}/restore/      -> restore soft-deleted record
       - GET  /api/users/deleted/           -> list soft-deleted records
    """
    # queryset shows only active records (non-deleted)
    queryset = UserDetail.objects.all()
    serializer_class = UserDetailSerializer

    def get_permissions(self):
        # create is open to public (AllowAny). All other actions require admin.
        if self.action == "create":
            return [permissions.AllowAny()]
        # allow admin-only for other actions
        return [permissions.IsAdminUser()]

    def create(self, request, *args, **kwargs):
        """
        Save submission. If the requester is NOT an admin (i.e., a public user),
        send email notification to admin.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        userdetail = serializer.save()

        # send email only if not created by an admin staff (so public submissions trigger email)
        user = getattr(request, "user", None)
        is_by_admin = bool(user and getattr(user, "is_staff", False) and user.is_authenticated)
        if not is_by_admin:
            subject = "New User Detail Submitted"
            message = (
                f"New user detail submission:\n\n"
                f"Name: {userdetail.name}\n"
                f"Father Name: {userdetail.father_name}\n"
                f"Date of Birth: {userdetail.date_of_birth}\n"
                f"Email: {userdetail.email}\n"
                f"Phone: {userdetail.phone_number}\n"
                f"Submitted at: {userdetail.created_at}\n"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete by default (mark is_deleted=True).
        Admin can permanently delete via the hard_delete action.
        """
        instance = self.get_object()  # uses queryset (only active), OK
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="deleted", permission_classes=[permissions.IsAdminUser])
    def deleted(self, request):
        """List soft-deleted records (admin only)."""
        qs = UserDetail.all_objects.filter(is_deleted=True)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="hard_delete", permission_classes=[permissions.IsAdminUser])
    def hard_delete(self, request, pk=None):
        """Permanently delete a record (admin only)."""
        obj = get_object_or_404(UserDetail.all_objects, pk=pk)
        obj.delete()
        return Response({"detail": "Permanently deleted."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="restore", permission_classes=[permissions.IsAdminUser])
    def restore(self, request, pk=None):
        """Restore a soft-deleted record (admin only)."""
        obj = get_object_or_404(UserDetail.all_objects, pk=pk)
        if not obj.is_deleted:
            return Response({"detail": "Record is not deleted."}, status=status.HTTP_400_BAD_REQUEST)
        obj.restore()
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
