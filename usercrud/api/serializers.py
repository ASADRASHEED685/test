# api/serializers.py
from rest_framework import serializers
from .models import UserDetail

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = [
            "id",
            "name",
            "father_name",
            "date_of_birth",
            "email",
            "phone_number",
            "is_deleted",
            "deleted_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["is_deleted", "deleted_at", "created_at", "updated_at"]

    def validate(self, data):
        """
        Ensure email and phone_number are unique among non-deleted records.
        This allows soft-deleted records to not block re-creation if preferred.
        """
        email = data.get("email", None)
        phone = data.get("phone_number", None)

        # For updating, allow same value on the instance being updated
        instance = getattr(self, "instance", None)

        if email:
            qs = UserDetail.all_objects.filter(email=email, is_deleted=False)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"email": "This email is already used by another active record."})

        if phone:
            qs = UserDetail.all_objects.filter(phone_number=phone, is_deleted=False)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"phone_number": "This phone number is already used by another active record."})

        return data
