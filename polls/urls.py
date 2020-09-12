
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


from .views import PollDeleteView, PollDeleteView, UserPollListView
urlpatterns = [
    path('poll/new/',views.add_poll, name='poll-create'),
    path('',views.home, name='home'),
    path('user/<str:username>/',UserPollListView.as_view(), name='user-polls'),
    path('poll/<str:link>/',views.poll_detail, name='poll-detail'),
    path('poll/<str:link>/result/',views.result, name='poll-result'),
    path('poll/<int:pk>/delete/',PollDeleteView.as_view(), name='poll-delete'),
]



# if settings.DEBUG:
#     urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)