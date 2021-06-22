import pickle
import pandas as pd
from flask import Flask, request, Response
from classes.electrical_consumption import Electrical_Consumption
import os

# loading model trained from pickle file
with open('models/rfr_final.pkl', 'rb') as file:
    model = pickle.load(file)

# initializing API
app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def electrical_consumption_prediction():
    test_json = request.get_json()

    if test_json:

        # unique observation
        if isinstance(test_json, dict):
            test_raw = pd.DataFrame(test_json, index=[0])

        # multiple observations
        else:  # multiple Example
            test_raw = pd.DataFrame(test_json, columns=test_json[0].keys())

        # instantiating EC class
        pipeline = Electrical_Consumption()

        # manipulating features
        test_raw_features = pipeline.features_engineering(test_raw)

        # rescaling and encoding features to predict
        test_raw_prepared = pipeline.data_preparation(test_raw_features)

        # predicting
        df_response = pipeline.get_predict(model, test_raw_prepared)

        return df_response

    else:

        return Response("{}", status=200, mimetype='application/json')


if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)