from django.urls import path
from . import views

urlpatterns = [
    path('',                          views.login_page,         name='login'),
    path('signup/',                   views.signup_page,        name='signup'),
    path('logout/',                   views.logout_view,        name='logout'),
    path('dashboard/',                views.dashboard,          name='dashboard'),
    path('select-track/',             views.select_track,       name='select_track'),
    path('module/<str:track_id>/<int:module_index>/', views.module_detail, name='module_detail'),
    path('api/complete/',             views.mark_complete,      name='mark_complete'),
    path('api/quiz/',                 views.submit_quiz,        name='submit_quiz'),
    path('admin-dashboard/',          views.admin_dashboard,    name='admin_dashboard'),
    path('admin/delete/<uuid:user_id>/', views.admin_delete_user, name='admin_delete_user'),
]
