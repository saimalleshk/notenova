from django import forms
from .models import NewsEntry

class NewsEntryAdminForm(forms.ModelForm):
    class Meta:
        model = NewsEntry
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['_save'] = forms.BooleanField(required=False, widget=forms.HiddenInput())
        self.fields['_save_and_chime'] = forms.BooleanField(required=False, widget=forms.HiddenInput())
        self.fields['_save_and_both'] = forms.BooleanField(required=False, widget=forms.HiddenInput())
