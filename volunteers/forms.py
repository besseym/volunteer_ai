from django import forms
from django.core.exceptions import ValidationError
from .models import Volunteer, VolunteerOpportunity, Category


class VolunteerOpportunityForm(forms.ModelForm):
    """Form for creating and editing volunteer opportunities."""

    class Meta:
        model = VolunteerOpportunity
        fields = ['title', 'description', 'date', 'category']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter opportunity title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the volunteer opportunity',
                'rows': 4,
                'required': True
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise ValidationError('Title is required.')
        return title.strip()

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description or not description.strip():
            raise ValidationError('Description is required.')
        return description.strip()

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            raise ValidationError('Date is required.')
        return date


class VolunteerForm(forms.ModelForm):
    """Form for volunteer sign-up."""

    class Meta:
        model = Volunteer
        fields = ['name', 'age', 'expertise', 'opportunity']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'required': True
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your age',
                'min': 18,
                'required': True
            }),
            'expertise': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your skills and expertise',
                'rows': 3,
                'required': True
            }),
            'opportunity': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise ValidationError('Name is required.')
        return name.strip()

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None:
            raise ValidationError('Age is required.')
        if age < 18:
            raise ValidationError('You must be at least 18 years old to volunteer.')
        return age

    def clean_expertise(self):
        expertise = self.cleaned_data.get('expertise')
        if not expertise or not expertise.strip():
            raise ValidationError('Expertise description is required.')
        return expertise.strip()


class OpportunityFilterForm(forms.Form):
    """Form for filtering volunteer opportunities."""

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search opportunities...'
        })
    )