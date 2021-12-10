from django.urls import path
from . import views
from plotlyplot.dash_apps.finished_apps import simpleexample
urlpatterns = [
#    path("",views.home,name="home")
    path("plot/",views.plot_fao,name="plot_fao")
]
