from flask import Flask, jsonify, request
import asyncio

from agent_model import WorkflowInput, run_workflow

app = Flask(__name__, static_folder='.', static_url_path='')


@app.route('/')
def index():
    return app.send_static_file('Index.html')


@app.route('/quote', methods=['GET'])
def quote():
    # Accept an optional `q` query parameter as input text
    input_text = request.args.get('q', 'Give me a short quote')
    try:
        # run_workflow is async; run it synchronously here
        result = asyncio.run(run_workflow(WorkflowInput(input_as_text=input_text)))

        # result may be a dict with 'output_text' or nested values
        if isinstance(result, dict):
            quote_text = result.get('output_text') or result.get('quote') or str(result)
        else:
            quote_text = str(result)

        return jsonify({'quote': quote_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)