from flask import Flask, jsonify, request
from flask_cors import CORS

from budget import Budget, Simulator

import uuid

# config
DEBUG = True

ORIGIN_IP   = '94.130.179.105'
ORIGIN_URL  = 'http://budget.bsdro.org:8080'

app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={ r'/api/*': {'origins': ORIGIN_URL} })

BUDGET = [
  {
      'id'      : uuid.uuid4().hex,
      'datetime': '01.01.2019 00:00:00',
      'budget'  : '07.00',
  },
  {
      'id'      : uuid.uuid4().hex,
      'datetime': '01.04.2019 00:00:00',
      'budget'  : '00.00',
  },
  {
      'id'      : uuid.uuid4().hex,
      'datetime': '01.07.2019 00:00:00',
      'budget'  : '01.00',
  },
]

@app.route('/api/ping', methods=['GET'])
def pong():
    return jsonify('pong!')

@app.route('/api/budget', methods=['GET', 'POST'])
def budget():
    response = {'status': 'success'}
    if request.method == 'POST':
        payload = request.get_json()
        BUDGET.append({
          'id': uuid.uuid4().hex,
          'datetime': payload.get('datetime'),
          'budget'  : payload.get('budget'),
            })
        response['message'] = 'Budget item added!'
    else:
        response['budget'] = sorted(BUDGET, key=lambda item: item['datetime'])
    return jsonify(response)

@app.route('/api/budget/<budget_id>', methods=['PUT', 'DELETE'])
def one_budget(budget_id):
    response = { 'status': 'success' }
    if request.method == 'PUT':
        payload = request.get_json()
        remove_budget(budget_id)
        BUDGET.append({
          'id': uuid.uuid4().hex,
          'datetime': payload.get('datetime'),
          'budget'  : payload.get('budget'),
            })
        response['message'] = 'Budget item updated!'
    elif request.method == 'DELETE':
        remove_budget(budget_id)
        response['message' ] = 'Budget item removed!'
    return jsonify(response)

@app.route('/api/simulator', methods=['POST'])
def run_simulation():
    response = { 'status': 'success' }
    budget = Budget.from_item_dict( format_budget() )
    sim = Simulator(budget)
    sim.generate_costs()

    response['simulation'] = sim.get_summary()

    return jsonify(response)

def remove_budget(budget_id):
    for item in BUDGET:
        if item['id'] == budget_id:
            BUDGET.remove(item)
            return True
    return False

def format_budget():
    budget = {}
    for item in BUDGET:
        budget[item['datetime']] = item['budget']
    return budget

if __name__ == '__main__':
    app.run(host = ORIGIN_IP)
