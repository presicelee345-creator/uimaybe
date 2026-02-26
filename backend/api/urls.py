from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/signup',  views.signup,        name='signup'),
    path('auth/signin',  views.signin,        name='signin'),
    path('auth/user',    views.get_user_view, name='get_user'),
    path('auth/signout', views.signout,       name='signout'),

    # Track
    path('track/select', views.select_track, name='select_track'),
    path('track',        views.get_track,    name='get_track'),

    # Progress
    path('progress/<str:track_id>', views.get_progress,       name='get_progress'),
    path('progress/course',         views.mark_course_complete, name='mark_course'),
    path('progress/quiz',           views.submit_quiz,         name='submit_quiz'),

    # Admin
    path('admin/users',            views.admin_users,       name='admin_users'),
    path('admin/reports',          views.admin_reports,     name='admin_reports'),
    path('admin/users/<str:user_id>', views.admin_delete_user, name='admin_delete_user'),
]
