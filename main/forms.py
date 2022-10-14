from django import forms
from account.models import Urls

class UrlAddForm(forms.ModelForm):
    link = forms.CharField(label='link', widget=forms.Textarea)

    class Meta:
        model = Urls
        fields = ('old_url', )
    