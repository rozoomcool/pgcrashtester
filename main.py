from flask import Flask, request, jsonify
import subprocess
import os
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
    # Установите переменные окружения для pgbench
    os.environ['PGUSER'] = 'postgres'
    os.environ['PGPASSWORD'] = 'root'
    # Инициализация базы данных для тестирования
    # init_cmd = ['sudo', '-u', 'postgres', 'pgbench', '-i', '-s', scale_factor, dbname]
    # subprocess.run(init_cmd, check=True)
    # Запуск теста
    run_cmd = ['sudo', '-u', 'postgres', 'pgbench', '-c', clients, '-j', threads, dbname]
    process = subprocess.run(run_cmd, capture_output=True, text=True, check=True)
    
    return jsonify({'output': process.stdout})
    
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)