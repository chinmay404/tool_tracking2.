from django import forms
from .models import ProductIndex

class ProductIndexForm(forms.ModelForm):
    balancing_report = forms.FileField(label='Balancing Report', required=False)
    drawing = forms.FileField(label='Drawing', required=False)
    inspection_report = forms.FileField(label='Inspection Report', required=False)

    class Meta:
        model = ProductIndex
        fields = '__all__'

        
class ProductIndexPrintForm(forms.ModelForm):
    uploaded_file = forms.FileField(label='Upload File', required=False)

    class Meta:
        model = ProductIndex
        fields = ['is_printed']
        widgets = {'is_printed': forms.CheckboxInput(attrs={'class': 'printed-checkbox'})}
