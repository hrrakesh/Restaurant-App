from django import forms
from .models import User, UserProfile



class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password',]
    
    def clean(self):
        cleaned_data =  super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "password does not match"
            )

class UserProfileForm(forms.ModelForm):
    
    # this below shows the over-writing the field on front end part
    address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'start typing..', 
        'required':'required'
        }))
    
    profile_picture = forms.ImageField(widget=forms.FileInput(attrs={'class':'btn btn-info'}))
    cover_photo = forms.ImageField(widget=forms.FileInput(attrs={'class':'btn btn-info'}))
    
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_photo', 'address', 'country', 'state', 'city', 'pincode',
                  'latitude', 'longitude']
    
    # Fields to make read-only
    read_only_fields = ['latitude', 'longitude']


    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field in self.read_only_fields:
                self.fields[field].widget.attrs['readonly'] = 'readonly'


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name','phone_number']
