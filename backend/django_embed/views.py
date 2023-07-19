from os.path import join
from typing import Any
from asgiref.sync import async_to_sync

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
from bokeh.models import ColumnDataSource, DataTable, HoverTool, TableColumn
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column
from bokeh.themes import Theme
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
from tornado import gen
import sqlite3

from django_embed.models import Log, Job, Task, User

from .models import Log
from bokeh_apps import job_visualizer

import subprocess
    
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from tasks.sample_tasks import create_task


def home(request):
    return render(request, "home.html")


@csrf_exempt
def run_task(request):
    if request.POST:
        task_type = request.POST.get("type")
        task = create_task.delay(int(task_type))
        return JsonResponse({"task_id": task.id}, status=202)


@csrf_exempt
def get_status(request, task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JsonResponse(result, status=200)

@login_required
def stream_logs(request, job_id):
    job = get_object_or_404(Job, job_id=job_id)
    if request.user != job.user:
        return HttpResponse(status=403)
    with open(job.log_file, 'r') as log_file:
        return HttpResponse(log_file.read())

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

def get_latest_job():
    print('hello')
    return Job.objects.latest('submit_time').first()

async def async_get_latest_job():
    print('hello')
    latest_job = await sync_to_async(get_latest_job)()
    return latest_job

def job_visualizer_handler(doc, request):
    # Create a data source to enable refreshing of fill
    source = ColumnDataSource(dict(job_id=[], status=[], progress=[], submit_time=[], num_tasks=[], complete_time=[], output_dir=[], system_config=[]))

    # Create a new plot
    p = figure(x_range=(0, 100), y_range=(0, 100), title='Job Progress', tools="")
    p.vbar(x='job_id', top='progress', width=0.5, source=source, 
        color=factor_cmap('status', palette=Spectral6, factors=['queued', 'running', 'completed']))

    # Add a hover tool
    hover = HoverTool()
    hover.tooltips = [
        ("Job ID", "@job_id"),
        ("Status", "@status"),
        ("Progress", "@progress"),
        ("Submit Time", "@submit_time"),
        ("Number of Tasks", "@num_tasks"),
        ("Complete Time", "@complete_time"),
        ("Output Directory", "@output_dir"),
        ("System Config", "@system_config")
    ]
    p.add_tools(hover)

    # Add a data table
    columns = [
        TableColumn(field="job_id", title="Job ID"),
        TableColumn(field="status", title="Status"),
        TableColumn(field="progress", title="Progress"),
        TableColumn(field="submit_time", title="Submit Time"),
        TableColumn(field="num_tasks", title="Number of Tasks"),
        TableColumn(field="complete_time", title="Complete Time"),
        TableColumn(field="output_dir", title="Output Directory"),
        TableColumn(field="system_config", title="System Config")
    ]
    data_table = DataTable(source=source, columns=columns, editable=True, index_position=-1)

    # Arrange the plot and data table in a vertical configuration
    layout = column(p, data_table)

    doc.add_root(layout)

    @without_document_lock
    @gen.coroutine
    async def update():
        #Query the database for the time of the last job submission
        query = await async_get_latest_job()
        print(query)

        if query is not None:
            rows = query

            # Update the data source with new job status data
            source.stream(dict(
                job_id=[row[0] for row in rows], 
                status=[row[1] for row in rows], 
                progress=[row[2] for row in rows],
                submit_time=[row[3] for row in rows],
                num_tasks=[row[4] for row in rows],
                complete_time=[row[5] for row in rows],
                output_dir=[row[6] for row in rows],
                system_config=[row[7] for row in rows]
            ))

    # Add a periodic callback to be run every 500 milliseconds
    doc.add_periodic_callback(update, 500)

@with_request
def job_visualizer_with_template(doc: Document, request: Any) -> None:
    job_visualizer_handler(doc, request)
    doc.template = """
{% extends 'base_generic.html' %}
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

