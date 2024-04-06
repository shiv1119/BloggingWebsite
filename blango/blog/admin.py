from django.contrib import admin
from blog.models import Tag, Post, Comment,Category, PostView, AuthorProfile

# Register your models here.



class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Post, PostAdmin)
admin.site.register(PostView)
admin.site.register(AuthorProfile)
