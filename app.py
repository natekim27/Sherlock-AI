from flask import Flask, request, jsonify
import os
import ast
import json
import pip._vendor.requests as requests

app = Flask(__name__)

code_ctx = ''
@app.route('/api/code', methods=['GET', 'POST'])
def handle_code():
    global code_ctx
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    if file:
        # Save the file to a location where it can be accessed by your code analysis module.    
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)
        print('File received: ' + file.filename)
        print('File received and saved to: ' + file_path)

        with open(file_path, 'r') as code_file:
            code_content = code_file.read()

        # Now, code_content is a string containing the code from the uploaded file.

        # Convert the code file to a format that can be parsed by GPT or your code understanding module.
        # This might involve parsing the code into an Abstract Syntax Tree (AST) and converting the AST into a format that GPT can understand.

        # Parse the code into an AST.
        tree = ast.parse(code_content)

        # Convert the AST into a string representation.
        ast_string = ast.dump(tree, include_attributes=True)

        code_ctx = ast_string

        print('here is your code, in readable form: ' + ast_string)

        # Now, ast_string is a string representation of the AST.

        return jsonify({'message': 'File successfully uploaded'}), 200


@app.route('/api/query', methods=['POST'])
def handle_query():
    global code_ctx
    data = request.get_json()
    if 'messages' not in data:
        return jsonify({'error': 'No messages provided'}), 400

    # Extract the last user's message as the query
    messages = data['messages']
    user_messages = [message for message in messages if message['role'] == 'user']
    if not user_messages:
        return jsonify({'error': 'No user messages provided'}), 400
    query = user_messages[-1]['message']
    # Define the API endpoint
    endpoint = 'https://smartprompt-globaldev.zoomdev.us/v1/zoom-ai-hackathon/invoke'

    # Define the headers. Replace 'api-key' with Claude.
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJpbnRlZ3JhdGlvbi1hZGxlciIsImF1ZCI6InNtYXJ0X3Byb21wdCIsImV4cCI6MTY4ODQ5MDcwMX0.KYfmZ_HuQDd5Yhe0IXpkWWLJqkJ0ZHdjkkYPvWxJhN9fxru7iIRCZqd8BY8UBub7eovWhDxNIucoS1Dd5wj4LQ'
    }

    # Define the data. The 'prompt' is the query from the user.
    # 'max_tokens' is the maximum length of the generated response.
    data = {
        "messages": [
            {
                "role": "user",
                "message": query
            }
        ],
        "model": "claude-instant-v1",
        "task_id": "1",
        "user_name": "test"
    }

    # Make the POST request to the API
    response = requests.post(data['task_id'], data['user_name'], data['model'], query, code_ctx)

    response = requests.post(endpoint, headers=headers, data=json.dumps(data))

    # Parse the response
    if response.status_code == 200:
        resultjson = response.json()
        result = resultjson.get('result', 'No Response Found')
        return jsonify(result), 200
    else:
        return jsonify({'error': "An error occurred: " + response.text}), 400


@app.route('/api/answer', methods=['POST'])
def handle_answer():
    data = request.get_json()
    if 'query' not in data or 'code' not in data:
        return jsonify({'error': 'The request must contain a query and code'}), 400

    query = data['query']
    code = data['code']

    # TODO: Generate an answer based on the query and code.
    # Use LLM model to generate a natural language answer based on the query and the understood code.

    # Placeholder for the generated answer.
    answer = "Generated answer goes here."

    return jsonify({'answer': answer}), 200

if __name__ == '__main__':
    app.run(debug=True)