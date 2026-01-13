from django.urls import path
from . import views

app_name = 'volunteers'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Opportunities
    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('opportunities/add/', views.opportunity_create, name='opportunity_create'),
    path('opportunities/<int:pk>/edit/', views.opportunity_edit, name='opportunity_edit'),
    path('opportunities/<int:pk>/delete/', views.opportunity_delete, name='opportunity_delete'),
    path('opportunities/<int:pk>/', views.opportunity_detail, name='opportunity_detail'),

    # Volunteers
    path('signup/', views.volunteer_signup, name='volunteer_signup'),
    path('signup/<int:opportunity_id>/', views.volunteer_signup, name='volunteer_signup_for_opportunity'),
    path('volunteers/', views.volunteer_list, name='volunteer_list'),
    path('volunteers/<int:pk>/delete/', views.volunteer_delete, name='volunteer_delete'),

    # API endpoints for React components
    path('api/opportunities/', views.api_opportunities, name='api_opportunities'),
    path('api/dashboard-stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
]