from .views import *
from rest_framework import routers

router = routers.SimpleRouter()

router.register('upload', UploadDealsViewSet, basename='upload')
router.register('best', BestCustomersViewSet, basename='best')

urlpatterns = router.urls
