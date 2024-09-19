from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("home", home, name="home"),

    path("ind/<model_str>/<id>", ind, name="ind"),
    path("ind_info/<model_str>/<id>", ind_info, name="ind_info"),
    path("list/<model_str>", list, name="list"),
    path("new/<model_str>", new, name="new"),
    path("new/<model_str>/<id>/<return_to>", new, name="new"),
    path("edit/<model_str>/<id>", edit, name="edit"),
    path("edit/<model_str>/<id>/<return_to>", edit, name="edit"),
    path("delete/<model_str>/<id>", delete, name="delete"),
    path("order/<model_str>/<dir>/<id>", order, name="order"),
    path("active/<model_str>/<id>", active, name="active"),
    path("add_note/<model_str>/<id>", add_note, name="add_note"),
    path("action/<action_type>/<return_to>/<model_str>/<id>", action, name="action"),

    path("add_upcoming_jobs/<day_adj>", add_upcoming_jobs, name="add_upcoming_jobs"),
    path("add_patient_job/<patient_id>/<jobtype_id>", add_patient_job, name="add_patient_job"),
    path("allocate_job/<job_id>/<staff_id>", allocate_job, name="allocate_job"),
    path("add_shift/<day_adj>/<shift_id>/<staff_id>", add_shift, name="add_shift"),
    path("add_preferred_shift/<day>/<shift_id>/<staff_id>", add_preferred_shift, name="add_preferred_shift"),
    path("job_notes/<model_str>/<id>", job_notes, name="job_notes"),

    path("custom_logout", custom_logout, name="custom_logout"),
    path("custom_login", custom_login, name="custom_login"),
    path("signup", signup, name="signup"),
    path("switch_user/<user_type>", switch_user, name="switch_user"),
    path("test_sms/<model_str>/<id>", test_sms, name="test_sms"),
    path("sms_job/<model_str>/<id>", sms_job, name="sms_job"),

    path("create_financial_spreadsheet/<month_id>", create_financial_spreadsheet, name="create_financial_spreadsheet"),
    path("file_upload/<model_str>", file_upload, name="file_upload"),
    path("file_to_db/<model_str>/<id>", file_to_db, name="file_to_db"),

    path('search', search, name="search")

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
