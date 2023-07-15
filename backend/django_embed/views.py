from os.path import join
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.decorators import login_required

from bokeh.document import Document
from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.themes import Theme

from .models import Log
import subprocess

@login_required
def run_subprocess(request):
    command = ['python', '--version']
    process = subprocess.run(command, capture_output=True, text=True)
    output = process.stdout
    Log.objects.create(user=request.user, output=output)
    return redirect('view_logs')  # assuming this is the name of your log view

@login_required
def view_logs(request):
    logs = Log.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'logs.html', {'logs': logs})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserChangeForm(instance=request.user)
        
    return render(request, 'profile.html', {'form': form})


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html', {})

def sea_surface_handler(doc: Document) -> None:
    df = sea_surface_temperature.copy()
    source = ColumnDataSource(data=df)

    plot = figure(x_axis_type="datetime", y_range=(0, 25), y_axis_label="Temperature (Celsius)",
                  title="Sea Surface Temperature at 43.18, -70.43")
    plot.line("time", "temperature", source=source)

    def callback(attr: str, old: Any, new: Any) -> None:
        if new == 0:
            data = df
        else:
            data = df.rolling(f"{new}D").mean()
        source.data = dict(ColumnDataSource(data=data).data)

    slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
    slider.on_change("value", callback)

    doc.add_root(column(slider, plot))


def with_request(f):
    def wrapper(doc):
        return f(doc, doc.session_context.request)
    return wrapper


@with_request
def sea_surface_handler_with_template(doc: Document, request: Any) -> None:
    sea_surface_handler(doc)
    doc.template = """
{% block title %}Embedding a Bokeh Apps In Django{% endblock %}
{% block preamble %}
<style>
.bold { font-weight: bold; }
</style>
{% endblock %}
{% block contents %}
    <div>
    This Bokeh app below is served by a <span class="bold">Django</span> server for {{ username }}:
    {{ request }}
    </div>
    {{ super() }}
{% endblock %}
    """
    doc.template_variables["username"] = request.user
    print(doc.session_context.request.arguments)
    doc.template_variables["request"] = doc.session_context.request.arguments


def sea_surface(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "embed.html", dict(script=script))


def sea_surface_custom_uri(request: HttpRequest) -> HttpResponse:
    script = server_document(request._current_scheme_host + "/sea_surface_custom_uri")
    return render(request, "embed.html", dict(script=script))