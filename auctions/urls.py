from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<str:title>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("closed_listing/<str:title>", views.passive_listing, name="passive_listing"),
    path('all_categories/<str:category>', views.category_listing, name="category_listing"),
    path('categories', views.categories, name="categories")
]
