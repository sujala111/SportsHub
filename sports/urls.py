from django.urls import path
from sports import views

app_name = 'sports'

urlpatterns = [
    path('choose_favorites/', views.choose_favorite_sports, name='choose_favorites'),
    path('tournament_list/', views.tournament_list, name='tournament_list'),
    path('delete_tournament/<int:t_id>', views.delete_tournament, name='delete_tournament'),
    path('coaching_centers_list/', views.coaching_centers_list, name='coaching_centers_list'),
    path('create_coaching_centers/', views.create_coaching_centers, name='create_coaching_centers'),
    path('my_coaching_centers/', views.user_coaching_centers, name='my_coaching_centers'),
    path('delete_coaching_centers/<int:c_id>', views.delete_coaching_centers, name='delete_coaching_centers'),
]
