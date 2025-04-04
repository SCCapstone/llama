#views to create, modify, and view student info
from .views_class import AddClassView, ClassDetailsView, ClassHomePageView
#views related to data management (i.e CSV import/export)
from .views_data import AddStudentImportView, ExportClassFileView
#views for core functionality (i.e registration and homepage)
from .views_main import CreateAccountView, LoginView, HomePageView, StudentRandomizerView, ProfileView, ChangePasswordView
#views to create, modify, and view student info
from .views_student import AddStudentManualView, EditStudentView, StudentMetricsView, StudentRatingEditView, StudentUpdateView, StudentDeleteView, AddNoteView, DeleteNoteView
from .views_manage_classes import ManageClassesView
from .views_class import EditClassView

