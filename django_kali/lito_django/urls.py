from django.urls import path
from . import views
from .views import line_chart, line_chart_json


urlpatterns = [
    path("<int:id>",views.index,name="index"),
    path("",views.home,name="home"),
    path("home",views.home,name="home"),
    path("create/",views.create,name="create"),
    path("view/",views.view,name="view"),
    path('chart', line_chart, name='line_chart'),
    path('chartJSON', line_chart_json, name='line_chart_json'),
]
