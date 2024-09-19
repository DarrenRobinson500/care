from django.forms import *
from .models import *

class PatientForm(ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'active', 'photo']
        widgets = {
            'name': TextInput(attrs={'class':'form-control'}),
            'active': CheckboxInput(attrs={'class': 'form-check-input'}),
            "photo": FileInput(attrs={"class": "form-control"}),
        }

class StaffForm(ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'manager', 'active', 'user', 'user_type', 'colour_no', 'photo']
        widgets = {
            'name': TextInput(attrs={'class':'form-control'}),
            'colour_no': TextInput(attrs={'class':'form-control'}),
            'manager': Select(attrs={'class':'form-control'}),
            'user': Select(attrs={'class':'form-control'}),
            'user_type': Select(attrs={'class':'form-control'}),
            'active': CheckboxInput(attrs={'class': 'form-check-input'}),
            "photo": FileInput(attrs={"class": "form-control"}),
        }

class AvailableShiftForm(ModelForm):
    class Meta:
        model = AvailableShift
        fields = ['start', 'end', 'active']
        widgets = {
            'start': TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end': TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'active': CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ShiftForm(ModelForm):
    class Meta:
        model = Shift
        fields = ['staff', 'date', 'shift', 'notes']
        widgets = {
            'staff': Select(attrs={'class': 'form-control'}),
            'date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shift': Select(attrs={'class': 'form-control'}),
            'notes': Textarea(attrs={'class': 'form-control'}),
        }

class JobTypeForm(ModelForm):
    class Meta:
        model = JobType
        fields = ['name', 'recurring', 'medication', 'start', 'end', 'amount', 'duration']
        labels = {
            'amount': "Standard Cost",
            'duration': "Duration (minutes)",
        }
        widgets = {
            'name': TextInput(attrs={'class':'form-control'}),
            'start': TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end': TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'amount': NumberInput(attrs={'class': 'form-control'}),
            'duration': NumberInput(attrs={'class': 'form-control'}),
            'recurring': CheckboxInput(attrs={'class': 'form-check-input'}),
            'medication': CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class RecurringJobForm(ModelForm):
    class Meta:
        model = RecurringJob
        fields = ['patient', 'jobtype', 'frequency']
        widgets = {
            'patient': Select(attrs={'class':'form-control'}),
            'jobtype': Select(attrs={'class':'form-control'}),
            'frequency': Select(attrs={'class': 'form-control'}),
        }

class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = ['patient', 'jobtype', 'staff', 'date_time_requested', 'notes']
        widgets = {
            'patient': Select(attrs={'class':'form-control'}),
            'jobtype': Select(attrs={'class':'form-control'}),
            'staff': Select(attrs={'class': 'form-control'}),
            'date_time_requested': DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': Textarea(attrs={'class': 'form-control'}),
        }

class MedicationTypeForm(ModelForm):
    class Meta:
        model = MedicationType
        fields = ("name", "category")
        widgets = {
            "name": TextInput(attrs={"class": "form-control"}),
            "category": TextInput(attrs={"class": "form-control"}),
        }

class MedicationForm(ModelForm):
    class Meta:
        model = Medication
        fields = ("medication_type", "dosage", "frequency", )
        widgets = {
            "medication_type": Select(attrs={"class": "form-control"}),
            "dosage": TextInput(attrs={"class": "form-control"}),
            "frequency": Select(attrs={"class": "form-control"}),
        }

class FrequencyForm(ModelForm):
    class Meta:
        model = Frequency
        fields = ['name', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'per_day']
        widgets = {
            'name': TextInput(attrs={'class':'form-control'}),
            'sunday': CheckboxInput(attrs={'class': 'form-check-input'}),
            'monday': CheckboxInput(attrs={'class': 'form-check-input'}),
            'tuesday': CheckboxInput(attrs={'class': 'form-check-input'}),
            'wednesday': CheckboxInput(attrs={'class': 'form-check-input'}),
            'thursday': CheckboxInput(attrs={'class': 'form-check-input'}),
            'friday': CheckboxInput(attrs={'class': 'form-check-input'}),
            'saturday': CheckboxInput(attrs={'class': 'form-check-input'}),
            'per_day': NumberInput(attrs={'class': 'form-control'}),
        }

class InfoCategoryForm(ModelForm):
    class Meta:
        model = InfoCategory
        fields = ["category"]
        widgets = {
            # 'database': Select(attrs={'class': 'form-control'}),
            'category': TextInput(attrs={'class': 'form-control'}),
        }

class InfoFieldForm(ModelForm):
    class Meta:
        model = InfoField
        fields = ["database", "category", "field", "data_type"]
        widgets = {
            'database': Select(attrs={'class': 'form-control'}),
            'category': Select(attrs={'class': 'form-control'}),
            'field': TextInput(attrs={'class': 'form-control'}),
            'data_type': Select(attrs={'class': 'form-control'}),
        }

class InfoTextForm(ModelForm):
    class Meta:
        model = Info
        fields = ["content_text"]
        labels = {'content_text': ""}
        widgets = {
            'content_text': TextInput(attrs={'class': 'form-control'}),
        }

class InfoTextAreaForm(ModelForm):
    class Meta:
        model = Info
        fields = ["content_text"]
        labels = {'content_text': ""}
        widgets = {
            'content_text': Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class InfoDateForm(ModelForm):
    class Meta:
        model = Info
        fields = ["content_date"]
        labels = {'content_date': ""}
        widgets = {
            'content_date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class InfoNumberForm(ModelForm):
    class Meta:
        model = Info
        fields = ["content_number"]
        labels = {'content_number': ""}
        widgets = {
            'content_number': NumberInput(attrs={'class': 'form-control'}),
        }

class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ["heading", "content"]
        widgets = {
            'heading': TextInput(attrs={'class': 'form-control'}),
            'content': Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ("name", "type", "document")
        widgets = {
            "name": TextInput(attrs={"class": "form-control"}),
            "type": Select(attrs={"class": "form-control"}),
            "document": FileInput(attrs={"class": "form-control"}),
        }


forms = [PatientForm, StaffForm, AvailableShiftForm, ShiftForm, MedicationTypeForm, MedicationForm, JobTypeForm, RecurringJobForm, JobForm, FrequencyForm, NoteForm, InfoCategoryForm, InfoFieldForm]