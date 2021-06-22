import pandas            as pd
import numpy             as np
import pickle
import json


class Electrical_Consumption(object):

    def __init__(self):
        # loading the scaler methods for the selected numerical features
        self.pop_ocup_scaler = pickle.load(open('parameters/pop_ocup_scaler.pkl', 'rb'))
        self.pim_se_scaler = pickle.load(open('parameters/pim_se_scaler.pkl', 'rb'))
        self.temp_min_se_scaler = pickle.load(open('parameters/temp_min_se_scaler.pkl', 'rb'))
        self.pmc_a_se_scaler = pickle.load(open('parameters/pmc_a_se_scaler.pkl', 'rb'))
        self.manual_selected_features = pickle.load(open('parameters/manual_selected_features.pkl', 'rb'))

    def features_engineering(self, df):
        ''' creating and transforming the dataframes's features '''

        # modifying the 'data' column, because it came as a string type
        df['data'] = df['data'].astype('datetime64[ns]')

        # creating the 'ano' column in the 'df' dataframe
        df['ano'] = df['data'].dt.year

        # creating the 'mes' column in the 'df' dataframe
        df['mes'] = df['data'].dt.month

        # creating the 'mes_seno' column in the 'df' dataframe
        df['mes_seno'] = df['mes'].apply(lambda x: np.sin(x * (2. * np.pi / 12)))

        # removing the 'mes' column from the 'df' dataframe
        df.drop(columns=['mes'], inplace=True)

        # modifying the 'data' column as a string type again, so we can send it through the API request
        df['data'] = df['data'].astype('str')

        return df

    def data_preparation(self, df):
        ''' rescaling the dataframe's numerical features '''

        # transforming the 'pop_ocup' column in the 'df' dataframe, with its imported scaler method
        pop_ocup_list = [i[0] for i in self.pop_ocup_scaler.transform(df[['pop_ocup']].values)]
        df['pop_ocup'] = pop_ocup_list

        # transforming the 'pim_se' column in the 'df' dataframe, with its imported scaler method
        pim_se_list = [i[0] for i in self.pim_se_scaler.transform(df[['pim_se']].values)]
        df['pim_se'] = pim_se_list

        # transforming the 'temp_min_se' column in the 'df' dataframe, with its imported scaler method
        temp_min_se_list = [i[0] for i in self.temp_min_se_scaler.transform(df[['temp_min_se']].values)]
        df['temp_min_se'] = temp_min_se_list

        # transforming the 'pmc_a_se' column in the 'df' dataframe, with its imported scaler method
        pmc_a_se_list = [i[0] for i in self.pmc_a_se_scaler.transform(df[['pmc_a_se']].values)]
        df['pmc_a_se'] = pmc_a_se_list

        return df

    def get_predict(self, model, df):
        ''' Filtering the features that will be used to predict the electrical consumption '''

        # instantiating the 'selected_features' list, with only the selected features names
        selected_features = self.manual_selected_features

        # filtering the 'df' dataframe with only the 'selected_features' and saving it as 'df_copy' dataframe
        df_copy = df.copy()[selected_features]

        # creating the 'ind_se' column with the final SE industry electrical consumption predicted values
        df_copy['ind_se'] = np.expm1(model.predict(df_copy))

        # creating the 'data' column, by copying it from the 'df' dataframe
        df_copy['data'] = df['data']

        return df_copy[['data', 'ind_se']].to_json(orient='records')