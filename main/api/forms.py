# forms.py
from django import forms

class ActivationForm(forms.Form):
    id = forms.CharField(label='Enter ID', widget=forms.TextInput(attrs={'placeholder': 'Enter ID'}))


class BatchActivationForm(forms.Form):
    new_uuids = forms.CharField(max_length=255)
    
    
    
class ReportUploadForm(forms.Form):
    balancing_report = forms.FileField(label='Balancing Report', required=False)
    drawing = forms.FileField(label='Drawing', required=False)
    inspection_report = forms.FileField(label='Inspection Report', required=False)