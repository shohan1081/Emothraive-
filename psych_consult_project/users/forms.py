# # users/forms.py

# from django import forms
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.contrib.auth import get_user_model
# from .models import User

# User = get_user_model()


# class CustomUserCreationForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     first_name = forms.CharField(max_length=150, required=True)
#     last_name = forms.CharField(max_length=150, required=True)
#     phone = forms.CharField(max_length=20, required=False)
    
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data['email']
#         user.first_name = self.cleaned_data['first_name']
#         user.last_name = self.cleaned_data['last_name']
#         user.phone = self.cleaned_data.get('phone', '')
#         if commit:
#             user.save()
#         return user


# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'profile_image')


# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ('first_name', 'last_name', 'phone', 'profile_image')
#         widgets = {
#             'profile_image': forms.FileInput(attrs={'accept': 'image/*'}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field in self.fields.values():
#             field.widget.attrs['class'] = 'form-control'