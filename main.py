from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# Connect to the SQLite database
conn = sqlite3.connect('tasks.db',check_same_thread=False)
cursor = conn.cursor()

# Create the tasks table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        due_date TEXT NOT NULL,
        status TEXT NOT NULL
    )
''')
conn.commit()

# Endpoint to create a new task
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    due_date = data.get('due_date')
    status = data.get('status', 'Incomplete')

    # Validate input
    if not title or not description or not due_date:
        return jsonify({'error': 'Missing required fields'}), 400

    # Insert new task into the database
    cursor.execute('INSERT INTO tasks (title, description, due_date, status) VALUES (?, ?, ?, ?)',
                   (title, description, due_date, status))
    conn.commit()

    task_id = cursor.lastrowid
    task = {
        'id': task_id,
        'title': title,
        'description': description,
        'due_date': due_date,
        'status': status
    }
    return jsonify({'message': 'Task created successfully', 'task': task}), 201

# Endpoint to retrieve a single task by its ID
@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()

    if task:
        task_dict = {
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'due_date': task[3],
            'status': task[4]
        }
        return jsonify({'task': task_dict})
    return jsonify({'error': 'Task not found'}), 404

# Endpoint to update an existing task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()

    if task:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        due_date = data.get('due_date')
        status = data.get('status')

        # Validate input
        if not title or not description or not due_date or not status:
            return jsonify({'error': 'Missing required fields'}), 400

        # Update task in the database
        cursor.execute('''
            UPDATE tasks
            SET title = ?, description = ?, due_date = ?, status = ?
            WHERE id = ?
        ''', (title, description, due_date, status, task_id))
        conn.commit()

        task_dict = {
            'id': task_id,
            'title': title,
            'description': description,
            'due_date': due_date,
            'status': status
        }
        return jsonify({'message': 'Task updated successfully', 'task': task_dict})
    return jsonify({'error': 'Task not found'}), 404

# Endpoint to delete a task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()

    if task:
        # Delete task from the database
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        return jsonify({'message': 'Task deleted successfully'})
    return jsonify({'error': 'Task not found'}), 404

# Endpoint to list all tasks with pagination
@app.route('/tasks', methods=['GET'])
def list_tasks():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    offset = (page - 1) * per_page

    cursor.execute('SELECT * FROM tasks LIMIT ? OFFSET ?', (per_page, offset))
    tasks = cursor.fetchall()

    task_list = []
    for task in tasks:
        task_dict = {
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'due_date': task[3],
            'status': task[4]
        }
        task_list.append(task_dict)

    return jsonify({'tasks': task_list, 'total_tasks': len(task_list)})

if __name__ == '__main__':
    app.run()
