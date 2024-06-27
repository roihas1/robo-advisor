import math
import os
import django
import numpy as np
import pandas as pd
from django.conf import settings
from service.util import helpers, data_management
from service.util.data_management import upload_file_to_google_drive
from service.config import settings
from service.impl.sector import Sector
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

class Analyze_ML:
    def __init__(
            self, returns_stock: pd.DataFrame,
            table_index: pd.Index,
            record_percent_to_predict: float,
            is_closing_prices_mode: bool = False
    ):
        self._returns_stock: pd.DataFrame = returns_stock
        self._table_index: pd.Index = table_index
        self._record_percent_to_predict: float = record_percent_to_predict
        self._is_closing_prices_mode: bool = is_closing_prices_mode

    def linear_regression_model(
            self, test_size_machine_learning: str
    ) -> tuple[pd.DataFrame, np.longdouble, np.longdouble]:
        df, forecast_out = self.get_final_dataframe()

        # Added date
        df['Date'] = pd.to_datetime(self._table_index)

        X = np.array(df.drop(labels=['Label', 'Date'],
                             axis=1))  # All values of df[Col] (with Nan). Label = Values after shifting 5% up
        X = preprocessing.scale(X)  # Normalizing
        X_lately = X[-forecast_out:]  # The last 5% of df[Col] - for example the last 180 days from 10 years
        X = X[:-forecast_out]  # The first 95% of df[Col] - for example the first X days from 10 years
        df.dropna(inplace=True)  # drop rows with NA Values -  The first 95% of df[Col, Label, Date]
        y = np.array(df['Label'])  # The first 95% of df[Label] -  The first 95% of df[Label]

        # Label is the prediction for Col - 0.05% from time period of data to predict (exp- 180 days fowards)
        # for each day in df, the value in Col is the real value of the stock,
        # and the value in Label is the value in X days after, due to the shift (180 days if its 10 years).
        # X - df[Col] , y - df[Label] - both 95% of original dataframe
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=float(test_size_machine_learning)
        )

        clf = LinearRegression()
        clf.fit(X_train, y_train)  # training model - according to "test_size_machine_learning" - X% of training set

        forecast = clf.predict(X_lately)

        forecast_dates = pd.date_range(start=df['Date'].iloc[-1], periods=forecast_out + 1, freq='D')[1:]
        forecast_df = pd.DataFrame(index=forecast_dates, columns=['Forecast'])
        forecast_df['Forecast'] = forecast

        # Combine the original DataFrame and the forecast DataFrame
        combined_df = pd.concat([df, forecast_df])

        forecast_with_historical_returns_annual, expected_returns = self.calculate_returns(combined_df)
        return combined_df, forecast_with_historical_returns_annual, expected_returns

def get_collection_forcast(collection_json_data, path,
                            models_data: dict[dict, list, list, list, list], collection_num,
                            is_daily_running: bool = True):
    stocks_symbols = collection_json_data['stocksSymbols']
    sectors: list[Sector] = helpers.set_sectors(stocks_symbols)
    closing_prices_table = data_management.get_closing_prices_table(path)
    pct_change_table = closing_prices_table.pct_change()

    # Call Machine Learning
    pct_change_table, annual_return, excepted_returns = update_machine_learning(
        pct_change_table, closing_prices_table.index, models_data
    )
    print("sdfsdg")


def machine_learning_offset(models_data, table_index) -> tuple[int, float]:
    record_percent_to_predict: float = float(models_data["models_data"]["record_percent_to_predict"])
    num_of_rows: int = len(table_index)
    offset_row: int = int(math.ceil(record_percent_to_predict * num_of_rows))
    return offset_row, record_percent_to_predict

def update_machine_learning(returns_stock, table_index: pd.Index, models_data: dict,
                                              closing_prices_mode: bool = False) -> tuple:
    # Calculate offset of the table (get sub-table)
    offset_row, record_percent_to_predict = machine_learning_offset(models_data, table_index)

    selected_ml_model_for_build: int = int(models_data["models_data"]["selected_ml_model_for_build"])
    test_size_machine_learning: float = float(models_data["models_data"]["test_size_machine_learning"])
    selected_ml_model_for_build: str = settings.MACHINE_LEARNING_MODEL[selected_ml_model_for_build]
    is_ndarray_mode = False
    try:
        columns = returns_stock.columns
    except AttributeError:
        columns = returns_stock
        is_ndarray_mode = True
    if len(columns) == 0:
        raise AttributeError('columns length is invalid - 0. Should be at least 1')
    else:
        excepted_returns = None
        annual_return_with_forecast = None

        for i, stock in enumerate(columns):
            if is_ndarray_mode:
                stock_name = 0
            else:
                stock_name = str(stock)

            analyze: Analyze_ML = Analyze_ML(
                returns_stock=returns_stock[stock_name],
                table_index=table_index,
                record_percent_to_predict=float(record_percent_to_predict),
                is_closing_prices_mode=closing_prices_mode
            )

            if selected_ml_model_for_build == settings.MACHINE_LEARNING_MODEL[0]:  # Linear Regression
                df, annual_return_with_forecast, excepted_returns = \
                    analyze.linear_regression_model(test_size_machine_learning)
            # elif selected_ml_model_for_build == settings.MACHINE_LEARNING_MODEL[1]:  # Arima
            #     df, annual_return_with_forecast, excepted_returns = analyze.arima_model()
            # elif selected_ml_model_for_build == settings.MACHINE_LEARNING_MODEL[2]:  # Gradient Boosting Regressor
            #     df, annual_return_with_forecast, excepted_returns = analyze.lstm_model()
            # elif selected_ml_model_for_build == settings.MACHINE_LEARNING_MODEL[3]:  # Prophet
            #     df, annual_return_with_forecast, excepted_returns, plt = analyze.prophet_model()
            else:
                raise ValueError('Invalid machine model')
            if df['Label'][offset_row:].values.size == returns_stock[stock_name].size:
                returns_stock[stock_name] = df['Label'][offset_row:].values
            else:
                returns_stock[stock_name] = df['Label'].values

        return returns_stock, annual_return_with_forecast, excepted_returns






if __name__ == '__main__':


    models_data: dict[dict, list, list, list, list] = helpers.get_collection_json_data()
    for i in range(1, len(models_data)):
        curr_collection = models_data[str(i)][0]
        stocks_symbols = curr_collection['stocksSymbols']
        path = f'{settings.BASIC_STOCK_COLLECTION_REPOSITORY_DIR}{str(i)}/'  # where to save the datasets
        get_collection_forcast(curr_collection, path, models_data, str(i), True)


