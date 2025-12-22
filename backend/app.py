from flask import Flask, jsonify, request
import os
import logging
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_cors import CORS

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = app.logger

app.config['MONGO_DBNAME'] = os.environ.get('MONGODB_DATABASE', 'mongotask')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/mongotask')

mongo = PyMongo(app)

CORS(app)

@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    """Retrieve all tasks from the database."""
    try:
        tasks = mongo.db.tasks
        result = []
        for field in tasks.find():
            result.append({'_id': str(field['_id']), 'title': field.get('title', '')})
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in get_all_tasks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/task', methods=['POST'])
def add_task():
    """Add a new task to the database."""
    try:
        tasks = mongo.db.tasks
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
            
        title = data['title']
        task_id = tasks.insert_one({'title': title}).inserted_id
        new_task = tasks.find_one({'_id': task_id})
        
        result = {'title': new_task['title'], '_id': str(new_task['_id'])}
        return jsonify({'result': result})
    except Exception as e:
        logger.error(f"Error in add_task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/task/<id>', methods=['PUT'])
def update_task(id):
    """Update an existing task's title."""
    try:
        tasks = mongo.db.tasks
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400

        title = data['title']
        tasks.find_one_and_update(
            {'_id': ObjectId(id)}, 
            {"$set": {"title": title}}
        )
        new_task = tasks.find_one({'_id': ObjectId(id)})
        result = {'title': new_task['title']}
        return jsonify({"result": result})
    except Exception as e:
        logger.error(f"Error in update_task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/task/<id>', methods=['DELETE'])
def delete_task(id):
    """Delete a task by ID."""
    try:
        tasks = mongo.db.tasks
        response = tasks.delete_one({'_id': ObjectId(id)})
        if response.deleted_count == 1:
            result = {'message': 'record deleted'}
        else:
            result = {'message': 'no record found'}
        return jsonify({'result': result})
    except Exception as e:
        logger.error(f"Error in delete_task: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')