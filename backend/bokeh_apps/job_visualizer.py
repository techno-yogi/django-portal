from bokeh.models import ColumnDataSource, DataTable, HoverTool, TableColumn
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column
from bokeh.themes import Theme
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
from tornado import gen
import sqlite3

from django_embed.models import Log, Job, Task, User

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

doc = curdoc()
doc.add_root(layout)

@gen.coroutine
def update():
    pass
    # Query the database for the time of the last job submission

    # if last_submit_time is not None:
    #     # Query the database for the details of the jobs from the last submission
    #     c.execute("SELECT * FROM Jobs WHERE SubmitTime=?", (last_submit_time,))
    #     rows = c.fetchall()

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

# # Add a periodic callback to be run every 500 milliseconds
# doc.add_periodic_callback(update, 500)
