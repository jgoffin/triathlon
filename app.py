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
    print(request)
    if request.method == 'POST':
        data = request.form
        data_dict = {
            'bike_time_secs': int(data['bike']),
            'run_time_secs': int(data['run']),
            'age': int(data['age']) if data['age'] else None,
            'gender': data.get('gender',None),
            'age_flag': 1 if data['age'] else 0,
            't1_secs': int(data['t1']) if data['t1'] else None,
            't2_secs': int(data['t2']) if data['t2'] else None,
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