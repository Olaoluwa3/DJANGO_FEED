from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Profile(models.Model):   #User profile. Whenever a new user is created
    first_name = models.CharField(max_length=200,blank=True)
    last_name = models.CharField(max_length=200,blank=True)
    email = models.EmailField(max_length=300,blank=True)
    dob = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE) #One to One relationship with User entity that comes with Django
    friends = models.ManyToManyField(User,blank=True, related_name='friends') #A profile or user can have many friends with other users
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.username}"  #Return the username of the user whenever this class is called

STATUS_CHOICES = (
    ('sent','sent'),
    ('accepted','accepted')
)

class Relationship(models.Model):   #Allows establishment of relationship between 2 profiles
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')   #foreign key to the profile class. When sending a friend request, we'll be the sender
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver') #we can also be the receiver
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="sent") #the default status created is sent. When request accepted, it changes to accepted
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    

class Post(models.Model):   #Related to any post made
    description = models.CharField(max_length=255, blank=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)  #Who is making the post. Foreign key to the user entity 
    image = models.ImageField(upload_to='images',blank=True) #All images uploaded will be saved to images folder. blank=True bc not required to have an image
    date_posted = models.DateTimeField(auto_now_add=True) #Automatically adds a date

    def __str__(self):
        return self.description   #returns the description of post

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)  #Foreignkey to the post class
    username = models.ForeignKey(User, related_name='details', on_delete=models.CASCADE) #Who is commenting on the post
    text = models.CharField(max_length=200)  #what the text of the comment says
    date_added = models.DateTimeField(auto_now_add=True,blank=True)  #date comment added

    def __str__(self):
        return self.text
    
    
class Like(models.Model):
	username = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)  #who liked a post. Foreign key to the user
	post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE) #What post did they like. Foreign key to the post


