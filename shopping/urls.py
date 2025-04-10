from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .views import ProductDetailView, ProductsView, CartViewSet, OrderViewSet, PersonalDetailViewSet, CardDetailViewSet, \
    CategoryViewSet, CategoryProductsViewSet, PaymentView

router = DefaultRouter()


router.register('cartview', CartViewSet, basename='cartview')
router.register('orderview', OrderViewSet, basename='orderview')
router.register('category', CategoryViewSet, basename='category')
router.register('clothes', CategoryProductsViewSet,basename='clothes')
router.register('personaldetail', PersonalDetailViewSet, basename='personal-detail')
router.register('card-detail', CardDetailViewSet, basename='card-detail')






urlpatterns = [
    path('', include(router.urls)),
    path('products/', ProductsView.as_view(), name='product-list'),
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    # path('category/<str:category>/', .as_view(), name='category-products'),
    path('auth/', views.obtain_auth_token),
    path('payment/', PaymentView.as_view(), name='payment'),

]
