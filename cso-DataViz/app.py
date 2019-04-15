from flask import Flask, render_template, request, jsonify
import sparql_queries

app = Flask(__name__)


@app.route('/')
def index_file():
    return render_template('index.html')


@app.route('/popupContent', methods=['GET'])
def popup_content():

    nuts_region = request.args.get('nuts_region')
    query_result = sparql_queries.get_popup(nuts_region)

    return jsonify(query_result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
