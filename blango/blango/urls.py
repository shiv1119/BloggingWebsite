"""
URL configuration for blango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from django.conf import settings
import blog.views
import blango_auth.views
from django_registration.backends.activation.views import RegistrationView
from blango_auth.forms import BlangoRegistrationForm
from blog.views import category_posts,edit_post,create_post,my_view
from blog.views import search_view


urlpatterns = [
    # path('accounts/logout/', logout_view, name='logout_view'),
    path('category/<int:category_id>/', category_posts, name='category_posts'),
    path('admin/', admin.site.urls),
    path("accounts/register/",RegistrationView.as_view(form_class=BlangoRegistrationForm),name="django_registration_register"),
    path("accounts/", include("django_registration.backends.activation.urls")),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/profile/", blango_auth.views.profile, name="profile"),
    path("accounts/custom_logout/", blango_auth.views.custom_logout, name="custom_logout"),
    path("", blog.views.index),
    path("post/<slug>/", blog.views.post_detail, name="blog-post-detail"),
    # path('category/<int:category_id>/', category_posts, name='category_posts'),
    path('accounts/profile/create_post/', create_post, name='create_post'),
    path('edit_post/<int:post_id>/', edit_post, name='edit_post'),
    path('accounts/profile/', my_view, name='my_view'),
    path('results/', search_view, name='search_view'),
    path('summernote/', include('django_summernote.urls')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
     
from django.urls import reverse

profile_url = reverse('profile')