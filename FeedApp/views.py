import re
from django.shortcuts import render, redirect
from .forms import PostForm,ProfileForm, RelationshipForm
from .models import Post, Comment, Like, Profile, Relationship
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.http import Http404


# Create your views here.

# When a URL request matches the pattern we just defined, 
# Django looks for a function called index() in the views.py file. 

def index(request):
    """The home page for Learning Log."""
    return render(request, 'FeedApp/index.html')



@login_required
def profile(request):
    profile = Profile.objects.filter(user=request.user)  #We use user to get their profile.Used filter instead of get because get does not work with profile.exists
    if not profile.exists():
        Profile.objects.create(user=request.user)
    profile = Profile.objects.get(user=request.user)    #Now we can get it because we know it exists

    if request.method != 'POST':
        form = ProfileForm(instance=profile) #Get a specific instance of the profile
    else:  #Trying to save to the database
        form = ProfileForm(instance=profile,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('FeedApp:profile') #Take them back to profiel page

    context = {'form': form}
    return render(request, 'FeedApp/profile.html', context)


@login_required
def myfeed(request):
    comment_count_list = []
    like_count_list = []
    posts = Post.objects.filter(username=request.user).order_by('-date_posted')   #filter allows us to get all the posts; sort by date
    for p in posts:
        c_count = Comment.objects.filter(post=p).count()  #see how many comments a post has
        l_count = Like.objects.filter(post=p).count()    #count how many likes a post has
        comment_count_list.append(c_count)
        like_count_list.append(l_count)
    zipped_list = zip(posts, comment_count_list, like_count_list)  #iterate through it all at the same time in order to pass it all to context

    context = {'posts':posts, 'zipped_list':zipped_list}
    return render(request, 'FeedApp/myfeed.html', context)


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
    else:
        form = PostForm(request.POST,request.FILES)   #Get everything coming in from the form
        if form.is_valid():
            new_post=form.save(commit=False)
            new_post.username = request.user
            new_post.save()
            return redirect('FeedApp:myfeed')

    context = { 'form':form }
    return render(request, 'FeedApp/new_post.html', context)


@login_required
def comments(request, post_id):
    if request.method == 'POST' and request.POST.get("btn1"):   #check to see if request is post and submit button was clicked
        comment = request.POST.get("comment")
        Comment.objects.create(post_id=post_id, username=request.user, text=comment, date_added=date.today())

    comments = Comment.objects.filter(post=post_id)
    post = Post.objects.get(id=post_id)

    context = {'post':post, 'comments':comments}
    return render(request, 'FeedApp/comments.html', context)



    




