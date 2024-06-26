from django.contrib import admin
from blog.models import Tag, Post, Comment,Category, PostView, AuthorProfile
from django_summernote.admin import SummernoteModelAdmin

# Register your models here.


class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('summary','content',)  
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(PostView)
admin.site.register(AuthorProfile)
