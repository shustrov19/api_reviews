from django.urls import path

from api.views import UserCreate, UserToken

app_name = 'users'

urlpatterns = [
    path('signup/', UserCreate.as_view(), name='signup'),
    path('token/', UserToken.as_view(), name='token'),
]
