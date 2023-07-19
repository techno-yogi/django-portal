from bokeh.models import ColumnDataSource, DataTable, HoverTool, TableColumn
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column
from bokeh.themes import Theme
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
from tornado import gen
import psycopg2
from asgiref.sync import sync_to_async
from django_embed.models import Log, Job, Task, User, JobType, Task, Host
from bokeh.document.locking import without_document_lock

# Create a data source to enable refreshing of fill
source = ColumnDataSource(dict(job_id=[], status=[], job_type=[], submit_time=[], log_path=[]))

conn = psycopg2.connect(database='django-portal', user='postgres', password='postgresadmin', host='localhost', port='5432')
cursor = conn.cursor()

# Create a new plot
p = figure(x_range=(0, 100), y_range=(0, 100), title='Job Progress', tools="")
p.vbar(x='job_id', top='progress', width=0.5, source=source, 
       color=factor_cmap('status', palette=Spectral6, factors=['queued', 'running', 'completed']))

# Add a hover tool
hover = HoverTool()
hover.tooltips = [
    ("Job ID", "@job_id"),
    ("Status", "@status"),
    ("Job Type", "@job_type"),
    ("Submit Time", "@submit_time"),
    ("Log Path", "@log_path"),
]
p.add_tools(hover)

# Add a data table
columns = [
    TableColumn(field="job_id", title="Job ID"),
    TableColumn(field="status", title="Status"),
    TableColumn(field="job_type", title="Job Type"),
    TableColumn(field="submit_time", title="Submit Time"),
    TableColumn(field="log_path", title="Log Path"),
]
data_table = DataTable(source=source, columns=columns, editable=True, index_position=-1)

# Arrange the plot and data table in a vertical configuration
layout = column(p, data_table)

doc = curdoc()
doc.add_root(layout)

@without_document_lock
@gen.coroutine
def update():
    
    # Query the database for the time of the last job submission
    # cursor.execute("SELECT MAX(SubmitTime) FROM django_embed_job")
    #last_submit_time = cursor.fetchone()[0]

    @sync_to_async
    def get_last_submit_time():
        print(Job.objects.first())
        return
    
    @sync_to_async
    def add_new_job():
        user = User.objects.create_user(username='testuse2', password='12345')
        job_type = JobType.objects.create(name='test')
        log = 'test_path'
        host = Host.objects.create(name='Test Host', ip_address='127.0.0.1')
        job = Job.objects.create(user=user, job_type=job_type, host=host, log_file=log)
        task = Task.objects.create(user=user, job=job)
        print(task, job, host, log, job_type, user)
    
    @sync_to_async
    def _update_data_source(doc):
        # Update the data source with new job status data
        job = Job.objects.first()
        print(job.log_file)
        source.stream(dict(
            job_id=[job.job_id], 
            status=[job.status], 
            job_type=[job.job_type.name],
            submit_time=[job.submit_time],
            log_path=[job.log_file],
        ))

    yield get_last_submit_time()

    yield doc.session_context.with_locked_document(_update_data_source)
    #yield add_new_job()
    # if last_submit_time is not None:
    #     # Query the database for the details of the jobs from the last submission
    #     cursor.execute("SELECT * FROM Job WHERE SubmitTime=?", (last_submit_time,))
    #     rows = cursor.fetchall()

    #     # Update the data source with new job status data
    #     source.stream(dict(
    #         job_id=[row[0] for row in rows], 
    #         status=[row[1] for row in rows], 
    #         progress=[row[2] for row in rows],
    #         submit_time=[row[3] for row in rows],
    #         num_tasks=[row[4] for row in rows],
    #         complete_time=[row[5] for row in rows],
    #         output_dir=[row[6] for row in rows],
    #         system_config=[row[7] for row in rows]
    #     ))

# Add a periodic callback to be run every 500 milliseconds
doc.add_periodic_callback(update, 1000)
