from django import forms
import uuid

class GroupIdForm(forms.Form):
    group_id = forms.CharField(label='Group ID', max_length=20)
    
    
    
class Master_To_req(forms.Form):
    uuids = forms.CharField(widget=forms.Textarea)

    def clean_uuids(self):
        uuids_str = self.cleaned_data['uuids']
        uuids_list = [uuid.UUID(uuid_str.strip()) for uuid_str in uuids_str.split(',') if uuid_str.strip()]
        return uuids_list
    
    
    
class OldUUIDForm(forms.Form):
    scrap_uuids = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    resharp_uuids = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
