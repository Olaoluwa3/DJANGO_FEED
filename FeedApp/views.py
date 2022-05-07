import re
from django.dispatch import receiver
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



@login_required   #Helps prevent unauthorized access. Not needed for the home page 
def profile(request):
    profile = Profile.objects.filter(user=request.user)  #We use user (in Profile class) to get the specific profile of a user. Used filter instead of get because get does not work with profile.exists
    if not profile.exists(): #if a profile doesnt exist for this user
        Profile.objects.create(user=request.user) #create one for them
    profile = Profile.objects.get(user=request.user)    #Now we can get it because we know it exists

    if request.method != 'POST':  #Means the method is GET and is just trying to load the webpage
        form = ProfileForm(instance=profile) #Load a specific instance of the profile. Forms were created in forms.py
    else:  #Trying to save to the database (request method is post)
        form = ProfileForm(instance=profile,data=request.POST) #data coming in from the webpage is what we'll save
        if form.is_valid(): 
            form.save()
            return redirect('FeedApp:profile') #Take them to profile page (Stay in same page)

    context = {'form': form}  #send the form through the context dictionary to profile.html file
    return render(request, 'FeedApp/profile.html', context)


@login_required
def myfeed(request):
    comment_count_list = []   #To hold the number of comments for each post
    like_count_list = []  #To hold the number of likes for each post
    posts = Post.objects.filter(username=request.user).order_by('-date_posted')   #filter allows us to get all the posts; sort by date; all the posts that belong to a certain user
    for p in posts: #For each post
        c_count = Comment.objects.filter(post=p).count()  #see how many comments a specific post has
        l_count = Like.objects.filter(post=p).count()    #count how many likes a specific post has
        comment_count_list.append(c_count)  
        like_count_list.append(l_count)
    zipped_list = zip(posts, comment_count_list, like_count_list)  #iterate through it all at the same time in order to pass it all to context; each post, the number of comments, the number of likes

    context = {'posts':posts, 'zipped_list':zipped_list}
    return render(request, 'FeedApp/myfeed.html', context)  #render it to myfeed page


@login_required
def new_post(request):
    if request.method != 'POST':  #If get request, load an empty form
        form = PostForm()
    else:
        form = PostForm(request.POST,request.FILES)   #Get everything coming in from the form, save the image that comes with the files
        if form.is_valid():
            new_post=form.save(commit=False)  #Saving but not writing to the database yet
            new_post.username = request.user  #Assign the username first
            new_post.save()    #Now can save
            return redirect('FeedApp:myfeed')

    context = {'form':form}
    return render(request, 'FeedApp/new_post.html', context)


@login_required
def friendsfeed(request):
    comment_count_list = []
    like_count_list = []
    friends = Profile.objects.filter(user=request.user).values('friends')
    posts = Post.objects.filter(username__in=friends).order_by('-date_posted')
    for p in posts:
        c_count = Comment.objects.filter(post=p).count()
        l_count = Like.objects.filter(post=p).count()
        comment_count_list.append(c_count)
        like_count_list.append(l_count)
    zipped_list = zip(posts, comment_count_list, like_count_list)

    if request.method == 'POST' and request.POST.get("like"):          #need to put in name of button (like)
        post_to_like = request.POST.get("like")       #get the value of the button
        print(post_to_like)
        like_already_exists = Like.objects.filter(post_id=post_to_like,username=request.user)
        if not like_already_exists.exists():
            Like.objects.create(post_id=post_to_like, username=request.user)
            return redirect("FeedApp:friendsfeed")   #will refresh the page and the number of likes should go up by 1

    context = {'posts':posts, 'zipped_list':zipped_list}
    return render(request, 'FeedApp/friendsfeed.html', context)



@login_required
def comments(request, post_id):
    if request.method == 'POST' and request.POST.get("btn1"):   #check to see if request is post and submit button was clicked
        comment = request.POST.get("comment")   #get the comment text that is in the box. We named the input in html 'comment'
        Comment.objects.create(post_id=post_id, username=request.user, text=comment, date_added=date.today()) #create a new comment object

    comments = Comment.objects.filter(post=post_id)  #Get all the comments for a particular post
    post = Post.objects.get(id=post_id)  #Get the corresponding post as well so we know what post it is associated to

    context = {'post':post, 'comments':comments}
    return render(request, 'FeedApp/comments.html', context)


@login_required
def friends(request):
    #get the admin_profile and user profile to create the first relationship
    admin_profile = Profile.objects.get(user=1)  #First person the be created is the admin
    user_profile = Profile.objects.get(user=request.user)

    #to get My friends
    user_friends = user_profile.friends.all()  #Get a list of all friends
    user_friends_profiles = Profile.objects.filter(user__in=user_friends) #Get the profiles of all user friends

    #to get Friend Requests sent
    user_relationships = Relationship.objects.filter(sender=user_profile)
    request_sent_profiles = user_relationships.values('receiver')  #Get profile of all people we sent request to

    #to get eligible profiles - exclude the user, their existing friends, and driend requests sent already
    all_profiles = Profile.objects.exclude(user=request.user).exclude(id__in=user_friends_profiles).exclude(id__in=request_sent_profiles)


    #to get friend requests received by the user
    request_received_profiles = Relationship.objects.filter(receiver=user_profile, status='sent')

    #if this is the first time to access the friends request page, create the first relationship
    #with the admin of the website (so the admin is friends with everyone)

    if not user_relationships.exists():    # 'filter' works with exists; 'get' does not
        Relationship.objects.create(sender=user_profile, receiver=admin_profile, status='sent')


    
    # check to see WHICH submit button was pressed (sending a friend request or accepting a friend request)

    #this is to process all send requests
    if request.method == 'POST' and request.POST.get("send_requests"):
        receivers = request.POST.getlist("send_requests") #get list of all the values
        print(receivers)  #a query set of profile ids
        for receiver in receivers:
            receiver_profile = Profile.objects.get(id=receiver)
            Relationship.objects.create(sender=user_profile, receiver=receiver_profile, status='sent')
        return redirect('FeedApp:friends')


    #this is to process all receive requests
    if request.method == 'POST' and request.POST.get("receive_requests"):
        senders = request.POST.getlist("receive_requests")    #get list of all people that sent friend requests   
        for sender in senders:
            #update the relationship model for the sender to status 'accepted'
            Relationship.objects.filter(id=sender).update(status='accepted')

            #create a relationship object to access the sender's user id
            #to add to the friends list of the user
            relationship_obj = Relationship.objects.get(id=sender)
            user_profile.friends.add(relationship_obj.sender.user)  #Add a friend to the user's profile

            #add the user to the friends list of the sender's profile
            relationship_obj.sender.friends.add(request.user)  #relationship_obj.sender is the friend (other person)


    context = {'user_friends_profiles':user_friends_profiles, 'user_relationships':user_relationships,
                'all_profiles':all_profiles, 'request_received_profiles':request_received_profiles}

    return render(request, 'FeedApp/friends.html', context)      
    






