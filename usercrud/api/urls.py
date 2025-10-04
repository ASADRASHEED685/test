# api/urls.py
from rest_framework.routers import DefaultRouter
from .views import UserDetailViewSet

router = DefaultRouter()
router.register(r"users", UserDetailViewSet, basename="userdetail")

urlpatterns = router.urls
