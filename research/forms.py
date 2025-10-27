from django import forms

class ResearchForm(forms.Form):
    topic = forms.CharField(
        label='Market Topic (e.g., "AI in healthcare")',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
