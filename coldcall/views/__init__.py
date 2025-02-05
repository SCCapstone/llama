#views to create, modify, and view student info
from .views_course import AddCourseView, ClassDetailsView, CourseHomePageView
#views related to data management (i.e CSV import/export)
from .views_data import AddStudentImportView, ExportClassFileView
#views for core functionality (i.e registration and homepage)
from .views_main import CreateAccountView, HomePageView, StudentRandomizerView
#views to create, modify, and view student info
from .views_student import AddEditStudentManualView, StudentMetricsView, StudentRatingEditView, StudentUpdateView

