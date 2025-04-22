from django import forms
from .models import One
from django import forms
from .models import One

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class U_form(forms.ModelForm):
    class Meta:
        model = One
        fields = ["text", "photo", "quantity", "rating", "price"]
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '1', 'max': '5'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class User_registration(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User 
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(User_registration, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

class RatingForm(forms.Form):
    rating = forms.FloatField(
        min_value=1,
        max_value=5,
        required=True,
        label="Rate this product (1-5)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': 'Enter rating from 1 to 5'
        })
    )

# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
# class U_form(forms.ModelForm):
#     class Meta:
#         model=One
#         fields=["text","photo",'quantity', 'rating',"price"]
# class User_registration(UserCreationForm):
#     email=forms.EmailField()
#     class Meta:
#         model=User 
#         fields=('username','email','password1','password2')
# class RatingForm(forms.Form):
#     rating = forms.FloatField(min_value=1, max_value=5, required=True, label="Rate this product (1-5)", widget=forms.NumberInput(attrs={'step': '0.1'}))
