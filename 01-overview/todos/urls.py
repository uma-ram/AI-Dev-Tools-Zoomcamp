from django.urls import path
from . import views

urlpatterns = [
    path('', views.TodoListView.as_view(), name='todo-list'),
    path('<int:pk>/edit/', views.TodoUpdateView.as_view(), name='todo-update'),
    path('<int:pk>/delete/', views.TodoDeleteView.as_view(), name='todo-delete'),
    path('<int:pk>/toggle/', views.toggle_resolved, name='todo-toggle'),
]