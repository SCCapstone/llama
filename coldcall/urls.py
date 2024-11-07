from django.urls import path
from django.contrib import admin

from . import views

app_name = "coldcall"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("admin/", admin.site.urls),
    path("home/", views.HomePageView.as_view(), name="home"),
    path("<int:course_id>/", views.CourseHomePageView.as_view(), name="course_home"),
    path("<int:course_id>/randomizer", views.StudentRandomizerView.as_view(), name="randomizer"),
    path("student/<int:student_id>", views.StudentMetricsView.as_view(), name="student_metrics"),
    path("addstudents/manual", views.AddStudentManualView.as_view(), name="add_student_manual"),
    path("addstudents/import", views.AddStudentImportView.as_view(), name="add_student_import"),
    path("addstudents/addcourse", views.AddCourseView.as_view(), name="add_course"),
    path("editclasses/<int:course_id>/<int:student_id>/manual", views.EditStudentManualView.as_view(), name="edit_student_manual"),
    path("editclasses/<int:course_id>/<int:student_id>/csv", views.EditStudentCSVView.as_view(), name="edit_student_csv"),
]