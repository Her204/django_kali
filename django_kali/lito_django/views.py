from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .models import ToDoList, Item
from .forms import CreateNewList
# Create your views here.

def index(request,id):
    ls = ToDoList.objects.get(id=id)
    if ls in request.user.todolist.all():
        if request.method == "POST":
            print(request.POST)
            if request.POST.get("save"):
                for item in ls.item_set.all():
                    p = request.POST
                    if "on"==p.get("c"+str(item.id)):
                        item.complete = True
                    else:
                        item.complete = False
                    item.save()
            elif request.POST.get("newItem"):
                txt = request.POST.get("new")
                print(txt)
                if len(txt) > 1:
                    ls.item_set.create(text=txt,complete=True)
                else:
                    print("invalid")
        return render(request,"lito_django/list.html",{"ls":ls})
    return render(request,"lito_django/view.html",{})

def home(response):
    return render(response,"lito_django/home.html",{})

def create(response):
    if response.method == "POST":
        form = CreateNewList(response.POST)
        if form.is_valid():
            n = form.cleaned_data["name"]
            t = ToDoList(name=n)
            t.save()
            response.user.todolist.add(t)
        return HttpResponseRedirect("/%i" %t.id)
    else:
        form = CreateNewList()
    return render(response,"lito_django/create.html",{"form":form})

def view(response):
    return render(response,"lito_django/view.html",{})

from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
import pandas as pd

df = pd.read_csv("../../DATA_ANALYSIS/sales_data.csv")


class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        #"""Return 7 labels for the x-axis."""
        return df.Day.sort_values().unique().tolist()

    def get_providers(self):
        #"""Return names of datasets."""
        return ["Cost","Profit","Revenue"]

    def get_data(self):
        #"""Return 3 datasets to plot."""

        return [df.Cost.tolist()[:10500],
                df.Profit.tolist()[:10500],
                df.Revenue.tolist()[:10500]]


line_chart = TemplateView.as_view(template_name='lito_django/line_chart.html')
line_chart_json = LineChartJSONView.as_view()
