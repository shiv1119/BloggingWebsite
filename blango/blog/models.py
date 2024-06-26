from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django_summernote.fields import SummernoteTextField

# Create your models here.

class Tag(models.Model):
    value = models.TextField(max_length=500)
    
    
    def __str__(self):
        return self.value
    
class Category(models.Model):
    name = models.TextField(max_length=500,blank=False,null=False)
    
    def __str__(self):
        return self.name
    
    
class Comment(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type","object_id")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    title = models.TextField(max_length=1500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/",blank=True, null=True)
    slug = models.SlugField(unique=True)
    summary = SummernoteTextField()
    content = SummernoteTextField()
    tags = models.ManyToManyField(Tag, related_name="posts")
    comments = GenericRelation(Comment)
   
    
    
    def __str__(self):
        return self.title
    
    
class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    view_count = models.PositiveIntegerField(default=0)
    

class AuthorProfile(models.Model):
    gender_choices = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Others'),
        ('P', 'Prefer Not To Say'),
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="profile"
    )
    bio = models.TextField()
    profile_images = models.ImageField(upload_to="profile_images/")
    user_date_of_birth = models.DateField()
    user_gender = models.CharField(max_length=1, choices=gender_choices)
    
    
    def __str__(self):
        return f"{self.__class__.__name__} object for {self.user}"