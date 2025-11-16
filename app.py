from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
LOGS_FOLDER = 'logs'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['LOGS_FOLDER'] = LOGS_FOLDER


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(REPORTS_FOLDER):
    os.makedirs(REPORTS_FOLDER)
if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)

# Dictionary to store task information
tasks = {}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        task_id = str(uuid.uuid4())
        output_filepath = os.path.join(app.config['REPORTS_FOLDER'], f'{task_id}.html')
        log_filepath = os.path.join(app.config['LOGS_FOLDER'], f'{task_id}.log')

        # Get the absolute path to the directory containing app.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        analyzer_script_path = os.path.join(script_dir, 'analyze.py')

        target_column = request.form.get('target_column')
        python_executable = os.path.expanduser("~/.pyenv/versions/3.11.14/bin/python")
        command = [python_executable, '-u', analyzer_script_path, filepath, output_filepath]
        if target_column:
            command.append(f'--target={target_column}')

        with open(log_filepath, 'w') as log_file:
            process = subprocess.Popen(
                command,
                stdout=log_file,
                stderr=subprocess.STDOUT
            )

        tasks[task_id] = {'process': process, 'status': 'pending'}

        return jsonify({'task_id': task_id})
    return jsonify({'error': 'File upload failed'})

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    if task_id not in tasks:
        output_filepath = os.path.join(app.config['REPORTS_FOLDER'], f'{task_id}.html')
        if os.path.exists(output_filepath):
             return jsonify({'status': 'complete'})
        return jsonify({'status': 'not_found'})


    task = tasks[task_id]
    process = task['process']
    return_code = process.poll()

    log_filepath = os.path.join(app.config['LOGS_FOLDER'], f'{task_id}.log')
    progress_message = ''
    try:
        if os.path.exists(log_filepath):
            with open(log_filepath, 'r') as log_file:
                progress_message = log_file.read().strip().split('\n')[-1]
    except Exception as e:
        progress_message = f"Could not read log file: {e}"

    if return_code is None:
        return jsonify({'status': 'pending', 'progress': progress_message})
    else:
        # Process finished
        if return_code == 0:
            output_filepath = os.path.join(app.config['REPORTS_FOLDER'], f'{task_id}.html')
            if os.path.exists(output_filepath):
                task['status'] = 'complete'
                return jsonify({'status': 'complete'})
            else:
                task['status'] = 'error'
                task['error'] = 'Analysis script finished successfully, but the report file was not generated. Check logs for details.'
                return jsonify({'status': 'error', 'message': task['error']})
        else:
            error_message = 'An unknown error occurred during analysis.'
            try:
                if os.path.exists(log_filepath):
                    with open(log_filepath, 'r') as log_file:
                        error_message = log_file.read()
            except Exception as e:
                error_message = f"Could not read log file: {e}"

            task['status'] = 'error'
            task['error'] = error_message
            return jsonify({'status': 'error', 'message': error_message})


@app.route('/report/<task_id>', methods=['GET'])
def get_report(task_id):
    return send_from_directory(app.config['REPORTS_FOLDER'], f'{task_id}.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
