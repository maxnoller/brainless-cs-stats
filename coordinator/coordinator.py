from flask import Flask, request, jsonify
import psycopg2
import os
import pika
from enum import Enum

app = Flask(__name__)

# Load database and RabbitMQ connection parameters from environment variables
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
AMQP_URL = os.environ.get('AMQP_URL')

# Enum for task status
class TaskStatus(Enum):
    NEW = 'New'
    FETCHING_CODE = 'FetchingCode'
    FETCHING_DEMO = 'FetchingDemo'
    PROCESSING = 'Processing'
    FINISHED = 'Finished'

# Set up database connection
def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

# Function to send message to RabbitMQ
def send_to_queue(match_code):
    connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
    channel = connection.channel()

    channel.queue_declare(queue='demo_codes', durable=True)
    channel.basic_publish(exchange='',
                          routing_key='demo_codes',
                          body=match_code,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    connection.close()

# Route to handle POST requests
@app.route('/create_task', methods=['POST'])
def create_task():
    try:
        # Extract data from POST request
        data = request.json
        match_code = data['match_code']
        demo_path = data.get('demo_path', None)

        # Insert data into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO "analyse-tasks" (match_code, demo_path) VALUES (%s, %s)',
                       (match_code, demo_path))
        conn.commit()

        # Send match_code to RabbitMQ
        send_to_queue(match_code)

        # Close database connection
        cursor.close()
        conn.close()

        return jsonify({"message": "Task created successfully with status 'New'"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
