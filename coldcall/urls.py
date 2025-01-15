from django.urls import path, include

from . import views

# app_name = "coldcall"
#may be causing namespace conflicts
#commented above out because i was having errors with making login - cade
urlpatterns = [
    #path("", include("coldcall.urls")),
    path("",views.HomePageView.as_view(), name="home"),

    
    #account management
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register', views.CreateAccountView.as_view(), name="register"),

    #path("home/", views.HomePageView.as_view(), name="home"),
    path("<int:course_id>/", views.CourseHomePageView.as_view(), name="course_home"),
    #path("<int:course_id>/randomizer", views.StudentRandomizerView.as_view(), name="randomizer"),
    # removing variable int from randomizer url so that you can open it and select a course from within the page - cade
    path("randomizer", views.StudentRandomizerView.as_view(), name="randomizer"),
    #path("student/<int:student_id>", views.StudentMetricsView.as_view(), name="student_metrics"),
    # edited to int:pk which now works - cade
    path("student/<int:pk>", views.StudentMetricsView.as_view(), name="student_metrics"),
    path("addeditstudents/manual", views.AddEditStudentManualView.as_view(), name="addedit_student_manual"),
    path("addeditstudents/manual/<int:student_id>", views.AddEditStudentManualView.as_view(), name="addedit_student_manual_with_id"),
    path("addstudents/import", views.AddStudentImportView.as_view(), name="add_student_import"),
    path("addcourse", views.AddCourseView.as_view(), name="add_course"),
    
    path("student/<int:student_id>/update", views.StudentUpdateView.as_view(), name="student_update"),
    # path("class/<int:class_id>/details", views.ClassDetailsView.as_view(), name="class_details"),
    # path("student/<int:student_id>/update_score", views.StudentScoreUpdateView.as_view(), name="student_score_update"),
    # path("students/filter", views.FilterStudentsByScoreView.as_view(), name="filter_students_by_score"),
    path("randomizer/", views. StudentRandomizerView.as_view(), name="randomizer"),
]