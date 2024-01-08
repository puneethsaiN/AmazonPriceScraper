from django import forms

class newProdForm(forms.Form):
    searchText = forms.CharField(label="",max_length=200)