from django.shortcuts import render
from django.utils import timezone
from blog.models import Post,PostView, Category
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from blog.forms import CommentForm,SearchForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import PostForm
import blango_auth
from blog.models import Post
from django.urls import reverse
from blango_auth.views import profile 



# Create your views here.
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post_view, created = PostView.objects.get_or_create(post = post)
    post_view.view_count += 1
    post_view.save()
    if request.user.is_active:
        if request.method == "POST":
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit = False)
                comment.content_object = post
                comment.creator = request.user
                comment.save()
                return redirect(request.path_info)
        else:
            comment_form = CommentForm()
    else:
        comment_form = None  

    return render(request, "blog/post-detail.html", {"post": post,"comment_form": comment_form, "view_count": post_view.view_count})


def index(request):
    posts = Post.objects.filter(published_at__lte=timezone.now())

    return render(request, "blog/index.html", {"posts": posts})




def category_posts(request, category_id):
    category = Category.objects.get(pk=category_id)
    posts = Post.objects.filter(category=category)
    return render(request, 'blog/category_posts.html', {'category': category, 'posts': posts})


def my_view(request):
    profile_url = reverse('profile')
    context = {'profile_url': profile_url}
    return render(request, 'blango_auth/profile.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user 
            post.save()
            print('post created')
            return redirect(my_view)
        else:
            print(form.errors)
    else:
        form = PostForm()
    return render(request, 'blog/create_post.html', {'form': form})

@login_required
def edit_post(request, post_id):
    post = Post.objects.get(pk=post_id, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PostForm(instance=post)

    return render(request, 'edit_post.html', {'form': form, 'post': post})



def search_view(request):
    form = SearchForm(request.GET)
    results = []

    if form.is_valid():
        query = form.cleaned_data['query']
        results = Post.objects.filter(content__icontains = query)
        if(len(results) == 0):
            results = Post.objects.filter(title__icontains = query)

    return render(request, 'blog/results.html', {'form': form, 'results': results})



@login_required
def edit_profile(request):
    user = request.user
    