from django.urls import path, include

from . import views

# app_name = "coldcall"
#may be causing namespace conflicts
#commented above out because i was having errors with making login - cade
urlpatterns = [
    path("index", views.IndexView.as_view(), name="index"),
    #path("", include("coldcall.urls")),
    path("",views.HomePageView.as_view(), name="home"),

    
    #added this path to make a login page - cade
    path('accounts/', include('django.contrib.auth.urls')),

    #path("home/", views.HomePageView.as_view(), name="home"),
    path("<int:course_id>/", views.CourseHomePageView.as_view(), name="course_home"),
    #path("<int:course_id>/randomizer", views.StudentRandomizerView.as_view(), name="randomizer"),
    # removing variable int from randomizer url so that you can open it and select a course from within the page - cade
    path("randomizer", views.StudentRandomizerView.as_view(), name="randomizer"),
    #path("student/<int:student_id>", views.StudentMetricsView.as_view(), name="student_metrics"),
    # edited to int:pk which now works - cade
    path("student/<int:pk>", views.StudentMetricsView.as_view(), name="student_metrics"),
    path("addstudents/manual", views.AddStudentManualView.as_view(), name="add_student_manual"),
    path("addstudents/import", views.AddStudentImportView.as_view(), name="add_student_import"),
    path("addcourse", views.AddCourseView.as_view(), name="add_course"),
    path("editclasses/<int:course_id>/<int:student_id>/manual", views.EditStudentManualView.as_view(), name="edit_student_manual"),
    path("editclasses/<int:course_id>/<int:student_id>/csv", views.EditStudentCSVView.as_view(), name="edit_student_csv"),
]