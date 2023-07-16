from flask import Flask, jsonify
import psutil  # a library for getting info about the system

app = Flask(__name__)

@app.route('/info')
def info():
    return jsonify({
        'cores': psutil.cpu_count(),
        'memory': psutil.virtual_memory().total,
        # add any other information you want here
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0')  # allow connections from any IP
