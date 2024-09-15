import json
from typing import Union
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

def get_all_values_by_field_name(json_object: dict, field_name: str, path_constraints: list[str] = None):
    results = []
    if path_constraints is None:
        path_constraints = []

    def traverse(obj, _path_constraints):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == field_name and not _path_constraints:
                    results.append(value)
                elif isinstance(value, (dict, list)):
                    new_constraints = _path_constraints.copy()
                    if key in new_constraints:
                        new_constraints.remove(key)
                    traverse(value, new_constraints)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    traverse(item, _path_constraints)

    traverse(json_object, path_constraints)
    return results

def get_field_value_no_cache(json_object: dict, target_field: str, path_constraints: list[str] = None):
    if not json_object or not target_field:
        return None
    path = find_field_path(target_field, json_object, path_constraints)
    if path:
        return get_value_by_path(json_object, path)
    return None

def find_field_path(target_field: str, json_obj: dict, constraints_in_path: list[str] = None,
                        path: list[Union[str, int]] = None):
        if path is None:
            path = []
        if constraints_in_path is None:
            constraints_in_path = []

        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                if key == target_field and not constraints_in_path:
                    path.append(key)
                    return path
                elif isinstance(value, (dict, list)):
                    new_path = path.copy()
                    new_path.append(key)
                    new_constraints = constraints_in_path.copy()
                    if key in new_constraints:
                        new_constraints.remove(key)
                    result = find_field_path(target_field, value, new_constraints, new_path)
                    if result:
                        return result
        elif isinstance(json_obj, list):
            for index, item in enumerate(json_obj):
                new_path = path.copy()
                new_path.append(index)
                new_constraints = constraints_in_path.copy()
                result = find_field_path(target_field, item, new_constraints, new_path)
                if result:
                    return result
        return None

def get_value_by_path(json_obj: dict, path: list[Union[str, int]]):
    if not path:
        return json_obj

    current_key = path[0]

    if isinstance(json_obj, dict) and current_key in json_obj or \
            isinstance(json_obj, list) and isinstance(current_key, int) and current_key < len(json_obj):
        return get_value_by_path(json_obj[current_key], path[1:])
    return None
# Set your API key here
API_KEY = 'eyJzY29wZSI6InZldHJpYy5pbyIsImlhdCI6MTY4NjIzOTMyM30.IvK0iKvz5IiTTAkT8otgxLef3-AcIn3uqfZ-pu7KYws'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']

        # Since filter_type is always 'city', we set it directly
        filter_type = 'city'

        # Set up the headers with the API key
        headers = {
            'x-api-key': f'{API_KEY}',
            'Content-Type': 'application/json',
        }

        body = {
            'query': query,
            'filter_type': filter_type
        }

        response = requests.post(
            "https://api.vetric.io/facebook/v1/search/filters",
            json=body,
            headers=headers
        )

        data = response.json()
        nodes = get_all_values_by_field_name(data, 'node', ['data', 'edges'])
        locations = []
        for node in nodes:
            location_name = get_field_value_no_cache(node, 'name')
            location_id = get_field_value_no_cache(node, 'id')
            locations.append({'name': location_name, 'id': location_id})
        
        return jsonify(locations)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)