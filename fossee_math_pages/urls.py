from django.urls import path

from . import views

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from django.conf.urls import url, include


urlpatterns = [
    path('', views.index, name='index'),
    path('admin_add_internship/', views.admin_add_internship, name='admin_add_internship'),
    path('admin_add_user/', views.admin_add_user, name='admin_add_user'),
    path('admin_manage_internship/', views.admin_manage_internship, name='admin_manage_internship'),
    path('admin_view_intern/', views.admin_view_intern, name='admin_view_intern'),
    path('admin_add_intern/', views.admin_add_intern, name='admin_add_intern'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('home_topics/', views.home_topics, name='home_topics'),
    path('home_view_data/', views.home_view_data, name='home_view_data'),
    path('intern_add_data/', views.intern_add_data, name='intern_add_data'),
    path('intern_view_internship/', views.intern_view_internship, name='intern_view_internship'),
    path('intern_edit_data/', views.intern_edit_data, name='intern_edit_data'),
    path('intern_view_data/', views.intern_view_data, name='intern_view_data'),
    path('intern_view_topic/', views.intern_view_topic, name='intern_view_topic'),
    path('internship/', views.internship, name='internship'),
    path('login/', views.user_login, name='login'),
    path('staff_add_subtopic/', views.staff_add_subtopic, name='staff_add_subtopic'),
    path('staff_add_topics/', views.staff_add_topics, name='staff_add_topics'),
    path('staff_aprove_contents/', views.staff_aprove_contents, name='staff_aprove_contents'),
    path('staff_manage_intern/', views.staff_manage_intern, name='staff_manage_intern'),
    path('staff_view_interns/', views.staff_view_interns, name='staff_view_interns'),
    path('staff_view_internship/', views.staff_view_internship, name='staff_view_internship'),
    path('staff_view_topic/', views.staff_view_topic, name='staff_view_topic'),
    path('logout/', views.user_logout, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)