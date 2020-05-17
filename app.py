# Serve model as a flask application

import pickle
import pandas as pd
import numpy as np
from flask import Flask, request, render_template

model = None
app = Flask(__name__)


def load_model():
    global model
    # model variable refers to the global variable
    with open('rf_pipeline.pkl', 'rb') as f:
        model = pickle.load(f)


@app.route('/')
def home_endpoint():
    return render_template('home.html')


@app.route('/predict', methods=['POST'])
def get_prediction():
    # Works only for a single sample
    if request.method == 'POST':
        data = request.form
        print(data)
        bike_split = map(int, data['bike'].split(':'))
        # Sum hour, minute, seconds into a single seconds value
        bike_time_secs = sum([a*b for a, b in zip(bike_split, [3600, 60, 1])])

        run_split = map(int, data['run'].split(':'))
        # Sum hour, minute, seconds into a single seconds value
        run_time_secs = sum([a * b for a, b in zip(run_split, [3600, 60, 1])])

        if data['t1']:
            t1_split = map(int, data['t1'].split(':'))
            # Sum minute, seconds into a single seconds value
            t1_time_secs = sum([a * b for a, b in zip(t1_split, [ 60, 1])])
            t1_time_secs = None if data['t1']=="00:00" else t1_time_secs

        if data['t2']:
            t2_split = map(int, data['t2'].split(':'))
            # Sum minute, seconds into a single seconds value
            t2_time_secs = sum([a * b for a, b in zip(t2_split, [60, 1])])
            t2_time_secs = None if data['t2']=="00:00" else t2_time_secs


        data_dict = {
            'bike_time_secs': bike_time_secs,
            'run_time_secs': run_time_secs,
            'age': int(data['age']) if data['age'] else None,
            'gender': data.get('gender',None),
            'age_flag': 1 if data['age'] else 0,
            't1_secs': t1_time_secs if data['t1'] else None,
            't2_secs': t2_time_secs if data['t2'] else None,
            't1_flag': 1 if data['t1'] else 0,
            't2_flag': 1 if data['t2'] else 0,
        }
        print(data_dict)
        observation = pd.DataFrame(data_dict, index=[0])
        # Need logic to handle missing user-inputs, either client or server-side
        prediction = model.predict(observation)  # runs globally loaded model on the data

        return str(prediction[0])


if __name__ == '__main__':
    load_model()  # load model at the beginning once only
    app.run(host='0.0.0.0', port=80, debug=True)