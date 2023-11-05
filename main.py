from flask import Flask, request, jsonify
import subprocess
import os
import psutil
import json
app = Flask(__name__)

@app.route('/bench', methods=['POST'])
def bench():
    if not request.json:
        return jsonify({'error': 'ты че? махаться будешь?'})
    data = request.json or {}
    dbname = data.get('dbname', 'lamtech_db')
    scale_factor = data.get('scaleFactor', 1)
    clients = data.get('clients', 1)
    threads = data.get('threads', 2)
    seconds = data.get('seconds', 10)
    # Установите переменные окружения для pgbench
    os.environ['PGUSER'] = 'postgres'
    os.environ['PGPASSWORD'] = 'root'
    # Инициализация базы данных для тестирования
    # init_cmd = ['sudo', '-u', 'postgres', 'pgbench', '-i', '-s', scale_factor, dbname]
    # subprocess.run(init_cmd, check=True)
    # Запуск теста
    run_cmd = ['sudo', '-u', 'postgres', 'pgbench', '-c', clients, '-j', threads, '-T', seconds, dbname]
    process = subprocess.run(run_cmd, capture_output=True, text=True, check=True)

    result = process.stdout.split('\n')
     
    result.pop(-1)
    print(result[0])

    return json.dumps(result)

@app.route('/performance', methods=['GET'])
def performance():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    partitions = psutil.disk_partitions()
    
    resp = {
        'cpu': f'{cpu_usage:.2f}%',
        'memory-total': f"{memory.total / (1024**2):.2f} MB",
        'memory-used': f"{memory.used / (1024**2):.2f} MB",
        'memory-free': f"{memory.free / (1024**2):.2f} MB",
        'partitions': {}
        }
    
    for part in partitions:
        usage = psutil.disk_usage(part.mountpoint)
        resp['partitions'][part.device] = {
            'total': f"{usage.total / (1024**3):.2f} GB",
            'used': f"{usage.used / (1024**3):.2f} GB",
            'free': f"{usage.free / (1024**3):.2f} GB",
        }
    
    return jsonify(resp)

@app.route('/restartdb', methods=['GET'])
def restartdb():
    run_cmd = ['systemctl', 'restart', 'postgresql']
    process = subprocess.run(run_cmd, capture_output=True, text=True, check=True)
    
    return jsonify(process.stdout)

@app.route('/killdb', methods=['GET'])
def killdb():
    run_cmd = ['systemctl', 'stop', 'postgresql']
    process = subprocess.run(run_cmd, capture_output=True, text=True, check=True)
    
    return jsonify(process.stdout)

@app.route('/logs', methods=['GET'])
def get_logs():
    run_cmd = ['cp', '/var/log/postgresql/postgresql-12-main.log', 'logs.log']
    precess = subprocess.run(run_cmd, capture_output=True, text=True, check=True)
    
    f = open('./logs.log', 'r')


    return f.read()

@app.route('/backup', methods=['POST'])
def backup():
    os.environ['PGUSER'] = 'postgres'
    os.environ['PGPASSWORD'] = 'root'
    
    run_cmd = ['sudo', '-u', 'postgres', 'pg_dump', '-U', 'postgres', '-d', 'lamtech_db']

    pg_dump_command = [
    'pg_dump',
    '-h', 'localhost',    # Хост сервера PostgreSQL
    '-U', 'postgres',  # Имя пользователя PostgreSQL
    '-d', 'lamtech_db',  # Имя базы данных
    '-f', 'backup.sql'     # Имя файла для сохранения резервной копии
    ]

    # Запуск утилиты pg_dump
    try:
        subprocess.run(pg_dump_command, check=True)
        return "Резервная копия успешно создана"
    except subprocess.CalledProcessError as e:
        return f"Произошла ошибка при создании резервной копии: {e}"

@app.route('/restore', methods=['POST'])
def restore():
    os.environ['PGUSER'] = 'postgres'
    os.environ['PGPASSWORD'] = 'root'

    pg_dump_command = [
    'psql',
    '-h', 'localhost',    # Хост сервера PostgreSQL
    '-U', 'postgres',  # Имя пользователя PostgreSQL
    '-d', 'lamtech_db',  # Имя базы данных
    '-a',
    '-f', 'backup.sql'     # Имя файла для сохранения резервной копии
    ]

    # Запуск утилиты pg_restore
    try:
        subprocess.run(pg_dump_command, check=True)
        return "Резервная копия успешно восстановлена"
    except subprocess.CalledProcessError as e:
        return f"Произошла ошибка при восстановлении резервной копии: {e}"

    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
