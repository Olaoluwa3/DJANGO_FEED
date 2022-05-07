from django.urls import path
from . import views

app_name = 'FeedApp'

urlpatterns = [
    path('', views.index, name='index'),  #Basically the home page
    path('profile/', views.profile, name='profile'),
    path('myfeed', views.myfeed, name='myfeed'),
    path('new_post', views.new_post, name='new_post'),
    path('friendsfeed', views.friendsfeed, name='friendsfeed'),
    path('comments/<int:post_id>/', views.comments, name='comments'),  #Path to the comments of a specific post
    path('friends/', views.friends, name='friends'),
    ]

    