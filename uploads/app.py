from flask import Flask, request, jsonify
import os
import ast
import json
import pip._vendor.requests as requests

app = Flask(__name__)


@app.route('/api/code', methods=['GET', 'POST'])
def handle_code():
    code_ctx = []
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    if file:
        # Save the file to a location where it can be accessed by your code analysis module.    
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)

        with open(file_path, 'r') as code_file:
            code_content = code_file.read()

        # Now, code_content is a string containing the code from the uploaded file.

        # Convert the code file to a format that can be parsed by GPT or your code understanding module.
        # This might involve parsing the code into an Abstract Syntax Tree (AST) and converting the AST into a format that GPT can understand.

        # Parse the code into an AST.
        tree = ast.parse(code_content)

        # Convert the AST into a string representation.
        ast_string = ast.dump(tree)

        code_ctx.append({"message": ast_string, "role": "user"})
        code_ctx.append({"message": 'Awesome, thanks for giving me your code to analyze', "role": "assistant"})
        codectxfile = open(file_path+'.ctx.txt', 'w')

        content = {"key": code_ctx}

        codectxfile.write(str(content))
        codectxfile.close

        # Now, ast_string is a string representation of the AST.

        return jsonify({'message': 'File successfully uploaded'}), 200


@app.route('/api/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    if 'query' not in data:
        return jsonify({'error': 'No messages provided'}), 400
    msg = {"message": data['query'], "role": "user"}

    filename = data["filename"]

    if not os.path.exists("uploads/" + filename  + ".ctx.txt"):
        return jsonify({'error': 'File Does Not Exist'}), 400
    code_ctx = [] #should no longer be global when you're done

    os.chdir(os.getcwd() + '/uploads')
    with open(filename + ".ctx.txt", 'r') as f:
        content = f.read()

    content = ast.literal_eval(content)
    
    code_ctx = content["key"]
    code_ctx.append(msg)

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
        "messages": code_ctx,
        "model": "claude-instant-v1",
        "task_id": "1",
        "user_name": "test"
    }

    # Make the POST request to the API
    # response = requests.post(data['task_id'], data['user_name'], data['model'], query, code_ctx)
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))
    response_msg = response.json()['result']
    
    code_ctx.append({"role": "assistant", "message": response_msg})
    
    #write code_ctx back into the file it came from
    codectxfile = open(filename + ".ctx.txt", 'w')
    codectxfile.write(str(code_ctx))
    codectxfile.close
    
    # Parse the response
    if response.status_code == 200:
        resultjson = response.json()
        result = resultjson.get('result', 'No Response Found')
        return jsonify(result), 200
    else:
        return jsonify({'error': "An error occurred: " + response.text}), 400


if __name__ == '__main__':
    app.run(debug=True)
