from .views import *
from rest_framework import routers

router = routers.SimpleRouter()

router.register('upload', UploadDealsViewSet, basename='upload')
router.register('best', BestCustomersViewSet, basename='best')


router.register('upload_v2', UploadDealsVer2ViewSet, basename='upload_v2')
router.register('best_v2', BestCustomersVer2ViewSet, basename='best_v2')

urlpatterns = router.urls
