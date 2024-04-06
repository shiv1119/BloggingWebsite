from django import forms
from blog.models import Comment
from crispy_forms.layout import Submit,Layout
from crispy_forms.helper import FormHelper
from blog.models import Post
from django.forms import ModelForm

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title','category','image','slug','summary', 'content', 'tags']

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)