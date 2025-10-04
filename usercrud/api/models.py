from django.db import models

# Create your models here.
# api/models.py
from django.db import models
from django.utils import timezone

class ActiveManager(models.Manager):
    """Manager returning only non-deleted records."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class UserDetail(models.Model):
    name = models.CharField(max_length=150)
    father_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    email = models.EmailField(max_length=254)
    phone_number = models.CharField(max_length=20)

    # soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # managers
    objects = ActiveManager()   # default manager: only active
    all_objects = models.Manager()  # all records (including deleted)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])

    def __str__(self):
        return f"{self.name} ({self.email})"
