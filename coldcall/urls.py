from django.urls import path, include

from . import views

# app_name = "coldcall"
#may be causing namespace conflicts
#commented above out because i was having errors with making login - cade
urlpatterns = [
    # Account management
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register', views.CreateAccountView.as_view(), name="register"),
    
    # Home
    path("",views.HomePageView.as_view(), name="home"),
    
    # Opening the specified course 
    path("<int:course_id>/", views.CourseHomePageView.as_view(), name="course_home"),

    # Students
    path("student/<int:pk>", views.StudentMetricsView.as_view(), name="student_metrics"),
    path("student/<int:pk>/<int:performance_id>", views.StudentRatingEditView.as_view(), name="edit_rating"),
    path("addeditstudents/manual", views.AddEditStudentManualView.as_view(), name="addedit_student_manual"),
    path("addeditstudents/manual/<int:student_id>", views.AddEditStudentManualView.as_view(), name="addedit_student_manual_with_id"),  
    path("student/<int:student_id>/update", views.StudentUpdateView.as_view(), name="student_update"),
    path("student/<int:student_id>/delete", views.StudentDeleteView.as_view(), name="student_delete"),
    path('drop_student/<int:student_id>/', views.StudentDeleteView.as_view, name='drop_student'),
    path('transfer_student/<int:student_id>/', views.StudentUpdateView.as_view(), name='transfer_student'),

    # Add course 
    path("addcourse", views.AddCourseView.as_view(), name="add_course"),

    # Import From 
    path("addstudents/import", views.AddStudentImportView.as_view(), name="add_student_import"),

    # Export To File 
    path("exportclassfile", views.ExportClassFileView.as_view(), name="export_class_file"),

    # Randomizer
    path("randomizer", views.StudentRandomizerView.as_view(), name="randomizer"),
    # Unsure URLS (Were already commented out)
    # path("class/<int:class_id>/details", views.ClassDetailsView.as_view(), name="class_details"),
    # path("student/<int:student_id>/update_score", views.StudentScoreUpdateView.as_view(), name="student_score_update"),
    # path("students/filter", views.FilterStudentsByScoreView.as_view(), name="filter_students_by_score"),

    # Manage Classes
    path("manageclasses", views.ManageClassesView.as_view(), name="manage_classes"),

    # Edit Course
    path("editcourse/<int:course_id>", views.EditCourseView.as_view(), name="edit_course"),
]