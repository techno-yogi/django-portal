import sqlite3
from datetime import datetime

# Connect to the SQLite database
conn = sqlite3.connect('jobs.db')

# Create a cursor
c = conn.cursor()

# Drop the old Jobs table if it exists
c.execute('DROP TABLE IF EXISTS Jobs')

# Create the new Jobs table
c.execute('''
    CREATE TABLE Jobs (
        JobID text,
        Status text,
        Progress real,
        SubmitTime text,
        NumTasks integer,
        CompleteTime text,
        OutputDir text,
        SystemConfig text
    )
''')

# Insert example data
example_data = [
    ('job1', 'completed', 100, datetime.now().isoformat(), 10, datetime.now().isoformat(), '/output/dir1', 'config1'),
    ('job2', 'running', 50, datetime.now().isoformat(), 20, None, '/output/dir2', 'config2'),
    ('job3', 'queued', 0, datetime.now().isoformat(), 30, None, '/output/dir3', 'config3'),
]

c.executemany('INSERT INTO Jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?)', example_data)

# Save (commit) the changes
conn.commit()

# Close the connection
conn.close()
