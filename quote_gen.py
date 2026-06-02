from flask import Flask, jsonify, request
import argparse
import asyncio

from agent_model import WorkflowInput, run_workflow

app = Flask(__name__, static_folder='.', static_url_path='')


def generate_quote(input_text: str) -> str:
    """Run the agent workflow and return the generated quote text."""
    result = asyncio.run(run_workflow(WorkflowInput(input_as_text=input_text)))

    if isinstance(result, dict):
        return result.get('output_text') or result.get('quote') or str(result)
    return str(result)


@app.route('/')
def index():
    return app.send_static_file('Index.html')


@app.route('/quote', methods=['GET'])
def quote():
    # Accept an optional `q` query parameter as input text
    input_text = request.args.get('q', 'Give me a short quote')
    try:
        quote_text = generate_quote(input_text)
        return f'<h1>Generated Quote</h1><p>{quote_text}</p>'
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def main() -> None:
    parser = argparse.ArgumentParser(description='Run OK-Computor quote generator.')
    parser.add_argument('--serve', action='store_true', help='Start the Flask web server')
    parser.add_argument('input_text', nargs='?', default='Give me a short quote', help='Input text for the agent workflow')
    args = parser.parse_args()

    if args.serve:
        app.run(debug=True)
    else:
        try:
            quote_text = generate_quote(args.input_text)
            print(quote_text)
        except Exception as e:
            print(f'Error: {e}')


if __name__ == '__main__':
    main()
