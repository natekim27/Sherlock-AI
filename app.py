from flask import Flask, request, jsonify
import os
import ast
import json
import pip._vendor.requests as requests

app = Flask(__name__)

code_context = ""

@app.route('/api/code', methods=['GET', 'POST'])
def handle_code():
    global code_context  # Use the global code_context variable

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
            code_lines = code_file.readlines()

        # Add line numbers to the code
        numbered_code_lines = [f"{i+1}: {line}" for i, line in enumerate(code_lines)]
        numbered_code = "".join(numbered_code_lines)

        # Now, numbered_code is a string containing the code from the uploaded file with line numbers.

        # Convert the code file to a format that can be parsed by GPT or your code understanding module.
        # This might involve parsing the code into an Abstract Syntax Tree (AST) and converting the AST into a format that GPT can understand.

        # Parse the code into an AST.
        tree = ast.parse(numbered_code)

        # Convert the AST into a string representation.
        ast_string = ast.dump(tree)

        # Now, ast_string is a string representation of the AST. You can use this as the code context for your GPT-3 queries.
        code_context = ast_string

        return jsonify({'message': 'File successfully uploaded'}), 200


@app.route('/api/query', methods=['POST'])
def handle_query():
    global code_context  # Use the global code_context variable

    query = request.json.get('query')

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Prepare the prompt for the LLM model by including the code context
    prompt = f'{code_context}\n{query}'

    # Define the API endpoint
    endpoint = 'https://smartprompt-globaldev.zoomdev.us/v1/zoom-ai-hackathon/invoke'

    # Define the headers. Replace 'your-api-key' with your actual OpenAI API key.
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-api-key'
    }

    # Define the data. The 'prompt' is the combination of code context and user query.
    # 'max_tokens' is the maximum length of the generated response.
    data = {
        'prompt': prompt,
        'max_tokens': 100
    }

    # Make the POST request to the API
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))

    # Parse the response
    if response.status_code == 200:
        result = response.json()
        return jsonify({'message': result['choices'][0]['text'].strip()}), 200
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
