from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import DateField

from . models import HostSearch, CustSearch
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    def clean_email(self):  # Define own cleaning method for organisations
        email_passed = self.cleaned_data.get('email')
        if not email_passed.endswith('@iitdh.ac.in'):
            raise forms.ValidationError("Invalid Email. Please register with your email registered to IIT Dharwad")

        return email_passed

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', ]


class ProfileForm(forms.ModelForm):
    birth_date = DateField(input_formats=settings.DATE_INPUT_FORMATS)

    class Meta:
        model = Profile
        fields = ('bio', 'birth_date')


class HostSearchForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(HostSearchForm, self).__init__(*args, **kwargs)

        ## GreenWheels
        self.fields['source_point'].help_text = 'Enter Source as Location Coordinates'
        self.fields['source_point'].label = 'Starting From'
        self.fields['source_point'].initial = 'Eg. 11.3234 -0.782122'

        self.fields['dest_point'].help_text = 'Enter Destination as Location Coordinates'
        self.fields['dest_point'].label = 'Traveling to'
        self.fields['dest_point'].initial = 'Eg. 21.3983 -4.52104'

        self.fields['AC'].help_text = 'Do you plan to switch on AC during the period of journey'

        self.fields['seats_vac'].help_text = 'Number of Seats vacant for Passengers'
        self.fields['seats_vac'].label = 'Passenger Seats'
        self.fields['seats_vac'].initial = '1'


    class Meta:
        model = HostSearch
        fields = ['source_point', 'dest_point', 'AC', 'seats_vac']
        widgets = {'task_by': forms.HiddenInput()}


class CustSearchForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CustSearchForm, self).__init__(*args, **kwargs)

        ## GreenWheels
        self.fields['pickup_loc'].help_text = 'Enter Source as Location Coordinates'
        self.fields['pickup_loc'].label = 'Starting From'
        self.fields['pickup_loc'].initial = 'Eg. 11.3234 -0.782122'

        self.fields['drop_loc'].help_text = 'Enter Destination as Location Coordinates'
        self.fields['drop_loc'].label = 'Traveling to'
        self.fields['drop_loc'].initial = 'Eg. 21.3983 -4.52104'

        self.fields['AC_pref'].help_text = 'Do you prefer AC'

        self.fields['seats_req'].help_text = 'Number of Seats Required'
        self.fields['seats_req'].label = 'Num. Passengers'
        self.fields['seats_req'].initial = '1'

    def clean(self):  # Custom clean method

        # doc_passed = self.cleaned_data.get('document')
        # doc_name = doc_passed.name  # Set PrintDoc name as doc_passed.name for further reference
        # if not doc_name.endswith('.pdf'):
        #     self.add_error('description', "Please upload only PDF Files")
        # return self.cleaned_data
        pass

    class Meta:
        model = CustSearch
        fields = ['pickup_loc', 'drop_loc', 'AC_pref', 'seats_req']


# class ConfirmForm(forms.ModelForm):  # Form for confirming print task
#
#     class Meta:
#         model = PrintDocs
#         fields = ['is_confirmed']
#
#     def __init__(self, *args, **kwargs):
#         super(ConfirmForm, self).__init__(*args, **kwargs)
#
#         self.fields['is_confirmed'].label = 'I would like to confirm this print. '
