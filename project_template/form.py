from django import forms

class QueryForm(forms.Form):
	q = forms.CharField(label= '',
						widget=forms.TextInput(attrs={'placeholder': 'Your Input', 'class' : 'form-control'}),
						max_length=1000)