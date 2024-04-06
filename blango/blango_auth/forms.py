from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django_registration.forms import RegistrationForm
from blango_auth.models import User
from crispy_forms.layout import Layout, Submit
from blog.models import AuthorProfile
from django import forms
from blog.models import Post 

class BlangoRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User
        
    def __init__(self, *args, **kwargs):
        super(BlangoRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Register"))




class AuthorProfileForm(forms.ModelForm):
    class Meta:
        model = AuthorProfile
        fields = ['bio', 'profile_images', 'user_date_of_birth', 'user_gender']

    helper = FormHelper()
    helper.form_method = 'post'
    helper.layout = Layout(
        'bio',
        'profile_images',
        'user_date_of_birth',
        'user_gender',
        Submit('submit', 'Save Changes')
    )
    
    
