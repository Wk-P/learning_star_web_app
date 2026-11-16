from django.urls import path

from . import views

urlpatterns = [
    path('', views.CategoryTreeView.as_view()),
    path('me/permissions/', views.MyPermissionsView.as_view()),
    path('admin/categories/', views.AdminCategoryListView.as_view()),
    path('admin/categories/<int:pk>/', views.AdminCategoryDetailView.as_view()),
    path('admin/languages/', views.AdminLanguageListView.as_view()),
    path('admin/languages/<int:pk>/', views.AdminLanguageDetailView.as_view()),
    path('permissions/tree/', views.PermissionTreeView.as_view()),
    path('permissions/users/<int:user_id>/', views.UserPermissionsView.as_view()),
    path('<slug:slug>/<str:kind>/', views.LanguageMediaView.as_view()),
]
