from django.contrib.auth import get_user_model
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from blog.models import Post,PostView,Category


user_model = get_user_model()
register = template.Library()
@register.simple_tag(takes_context=True)
def author_details_tag(context):
    request = context["request"]
    current_user = request.user
    post = context["post"]
    author = post.author

    if author == current_user:
        return format_html("<strong>me</strong>")

    if author.first_name and author.last_name:
        name = f"{author.first_name} {author.last_name}"
    else:
        name = f"{author.username}"

    if author.email:
        prefix = format_html('<a href="mailto:{}">', author.email)
        suffix = format_html("</a>")
    else:
        prefix = ""
        suffix = ""

    return format_html("{}{}{}", prefix, name, suffix)



@register.simple_tag
def row():
    return '<div class="row">'

@register.simple_tag
def row(extra_classes=""):
    return format_html('<div class="row {}">', extra_classes)

@register.simple_tag
def endrow():
    return format_html("</div>")

@register.simple_tag
def col(extra_classes=""):
    return format_html('<div class="col {}">', extra_classes)


@register.simple_tag
def endcol():
    return format_html("</div>")


@register.inclusion_tag("blog/post-list.html")
def recent_posts(id=None):
    posts = Post.objects.exclude(pk=id).order_by('-published_at')[:5]
    return {"title": "Recent Posts", "posts": posts}


@register.inclusion_tag('blog/most_viewed_posts.html')
def most_viewed_posts(exclude_post_id=None):
    posts_excluded = Post.objects.exclude(id=exclude_post_id)
    most_viewed_posts = PostView.objects.filter(post__in=posts_excluded).order_by('-view_count')[:5]
    return {"title" : "Most Viewed Post", 'most_viewed_posts': most_viewed_posts}


@register.inclusion_tag('blog/user_posts.html')
def user_posts(request):
    user_posts = Post.objects.filter(author=request)
    return {'user_posts': user_posts}


@register.inclusion_tag('blog/posts_by_category.html')
def posts_by_category(category_id):
    category = Category.objects.get(pk=category_id)
    posts = Post.objects.filter(category=category)[:5]
    return {'category': category, 'posts': posts}