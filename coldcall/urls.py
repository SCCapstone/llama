from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

# app_name = "coldcall"
#may be causing namespace conflicts
#commented above out because i was having errors with making login - cade
urlpatterns = [
    # Account management
    path('accounts/register', views.CreateAccountView.as_view(), name="register"),
    path('accounts/login', views.LoginView.as_view(), name="login"),
    path('accounts/login/', views.LoginView.as_view(), name="login"),

    # override django's default password reset views to custom templates
    path('accounts/reset_password/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/reset.html',
             email_template_name='registration/reset_email.html',
             subject_template_name='registration/reset_subject.txt'
         ),
         name='password_reset'),
    path('accounts/reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='registration/reset_sent.html'), name='password_reset_done'),
    path('accounts/reset_password/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/reset_complete.html'), name='password_reset_complete'),
    
    # no overrides, use defaul auth view
    path('accounts/logout', auth_views.LogoutView.as_view(), name="logout"),
    # Home
    path("",views.HomePageView.as_view(), name="home"),
    
    # Opening the specified class 
    path("<int:class_id>/", views.ClassHomePageView.as_view(), name="class_home"),

    # Students
    path("student/<int:pk>", views.StudentMetricsView.as_view(), name="student_metrics"),
    path("student/<int:pk>/<int:performance_id>", views.StudentRatingEditView.as_view(), name="edit_rating"),
    path("addstudents/manual/<int:class_id>", views.AddStudentManualView.as_view(), name="add_student_manual"),
    path("editstudent/<int:student_id>", views.EditStudentView.as_view(), name="edit_student"),
    path("student/<int:student_id>/update", views.StudentUpdateView.as_view(), name="student_update"),
    path("student/<int:student_id>/delete", views.StudentDeleteView.as_view(), name="student_delete"),
    path('drop_student/<int:student_id>/', views.StudentDeleteView.as_view, name='drop_student'),
    path('transfer_student/<int:student_id>/', views.StudentUpdateView.as_view(), name='transfer_student'),

    # Add class 
    path("addclass", views.AddClassView.as_view(), name="add_class"),

    # Import From 
    path("addstudents/import", views.AddStudentImportView.as_view(), name="add_student_import"),
    path("addstudents/import/<int:class_id>", views.AddStudentImportView.as_view(), name="add_student_import_with_id"),

    # Export To File 
    path("exportclassfile", views.ExportClassFileView.as_view(), name="export_class_file"),
    path("exportclassfile/<int:class_id>", views.ExportClassFileView.as_view(), name="export_class_file_with_id"),

    # Randomizer
    path("randomizer", views.StudentRandomizerView.as_view(), name="randomizer"),
    # Unsure URLS (Were already commented out)
    # path("class/<int:class_id>/details", views.ClassDetailsView.as_view(), name="class_details"),
    # path("student/<int:student_id>/update_score", views.StudentScoreUpdateView.as_view(), name="student_score_update"),
    # path("students/filter", views.FilterStudentsByScoreView.as_view(), name="filter_students_by_score"),

    # Manage Classes
    path("manageclasses", views.ManageClassesView.as_view(), name="manage_classes"),

    # Edit Class
    path("editclass/<int:class_id>", views.EditClassView.as_view(), name="edit_class"),

    # Helper view to add a note
    path('notes/<int:student_id>/', views.AddNoteView.as_view(), name='add_note'),
    path('notes/<int:student_id>/<int:note_id>/', views.DeleteNoteView.as_view(), name='delete_note'),
    
    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
]