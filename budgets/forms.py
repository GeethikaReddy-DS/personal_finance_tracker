from django import forms
from .models import Budget


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'limit', 'period', 'start_date', 'end_date']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Budget limit', 'step': '0.01'}),
            'period': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            from transactions.models import Category
            self.fields['category'].queryset = Category.objects.filter(user=user, type='expense')

    def clean(self):
        cleaned_data = super().clean()
        limit = cleaned_data.get('limit')
        
        if limit and limit <= 0:
            raise forms.ValidationError("Budget limit must be greater than 0")
        
        return cleaned_data
