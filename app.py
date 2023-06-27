from flask import Flask, request, jsonify
import os
import ast

app = Flask(__name__)

@app.route('/api/code', methods=['POST'])
def handle_code():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    print('penis')
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
        ast_string = ast.dump(tree)

        # Now, ast_string is a string representation of the AST.

        return jsonify({'message': 'File successfully uploaded'}), 200


@app.route('/api/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    if 'query' not in data:
        return jsonify({'error': 'No query in the request'}), 400

    query = data['query']

    # TODO: Pass the query to your query understanding module. 
    # This might involve using natural language processing techniques or the GPT-3 model to understand the query in the context of the code.

    print('Query received: ' + query)
    return jsonify({'message': 'Query successfully received'}), 200


@app.route('/api/answer', methods=['POST'])
def handle_answer():
    data = request.get_json()
    if 'query' not in data or 'code' not in data:
        return jsonify({'error': 'The request must contain a query and code'}), 400

    query = data['query']
    code = data['code']

    # TODO: Generate an answer based on the query and code.
    # This might involve using the GPT-3 model to generate a natural language answer based on the query and the understood code.

    # Placeholder for the generated answer.
    answer = "Generated answer goes here."

    return jsonify({'answer': answer}), 200

if __name__ == '__main__':
    app.run(debug=True)
