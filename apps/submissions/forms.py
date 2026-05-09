from django import forms


class SubmissionForm(forms.Form):
    language = forms.ChoiceField(choices=[("python", "Python")])
    source_code = forms.CharField(widget=forms.Textarea(attrs={"rows": 18}))
