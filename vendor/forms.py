from django import forms
from .models import Vendor, OpeningHours

class VendorForm(forms.ModelForm):
    vendor_license = forms.ImageField(widget=forms.FileInput(attrs={'class':'btn btn-info'}))
   
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license','rest_status']

    read_only_fields = ['']

    def __init__(self, *args, **kwargs):
        super(VendorForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field in self.read_only_fields:
                self.fields[field].widget.attrs['readonly'] = 'readonly'

class OpeningHoursForm(forms.ModelForm):
    
    class Meta:
        model = OpeningHours
        fields = ['day', 'from_hours', 'to_hours', 'is_holiday']