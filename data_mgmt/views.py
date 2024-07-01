import pandas as pd
from django.shortcuts import render

from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework import status

from service.util.data_management import *
from our_core.models import QuestionnaireA, QuestionnaireB
from service.config import settings as settings_service
from service.util.graph import helpers
from service.util import helpers as helpers2
from service.util import data_management

@login_required
@api_view(["GET"])
def get_specific_plot(request, type_of_graph):
    try:
        investor_user: InvestorUser = InvestorUser.objects.get(user=request.user)
        stocks_collection_number: str = investor_user.stocks_collection_number
    except InvestorUser.DoesNotExist:
        stocks_collection_number: str = '1'
    try:
        questionnaire_a = QuestionnaireA.objects.get(user=request.user)
    except QuestionnaireA.DoesNotExist:
        return JsonResponse(status=status.HTTP_403_FORBIDDEN, data="QuestionnareA missing!", safe=False)
    try:
        type_of_graph: int = int(type_of_graph)
    except ValueError:
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST, data="Invalid type_of_graph value!", safe=False)
    stocks_symbols = get_stocks_symbols_from_collection(stocks_collection_number)
    ml_answer = questionnaire_a.ml_answer
    model_answer = questionnaire_a.model_answer
    db_tuple = get_extended_data_from_db(
        stocks_symbols, ml_answer, model_answer, stocks_collection_number)
    sectors_data, sectors, closing_prices_table, three_best_portfolios, three_best_sectors_weights, pct_change_table, yields = db_tuple
    if type_of_graph == 1:
        labels: list[str] = ['Low Risk', 'Medium Risk', 'High Risk']
        monthly_yields: list[pd.Series] = [None] * len(yields)  # monthly yield change
        monthly_changes: list[pd.Series] = [None] * len(yields)  # yield changes
        df_describes: list[pd.Series] = [None] * len(yields)  # describe of yield changes
        for i in range(len(yields)):
            # Convert the index to datetime if it's not already in the datetime format
            curr_yield = yields[i]
            if not pd.api.types.is_datetime64_any_dtype(curr_yield.index):
                yields[i].index = pd.to_datetime(curr_yield.index)

            monthly_yields[i]: pd.Series = curr_yield.resample('M').first()
            monthly_changes[i]: pd.Series = monthly_yields[i].pct_change().dropna() * 100
            df_describes[i]: pd.Series = monthly_changes[i].describe().drop(["count"], axis=0)
            df_describes[i]: pd.Series = df_describes[i].rename(
                index={'mean': 'Mean Yield', 'std': 'Standard Deviation',
                       '50%': '50%(Median)', '25%': '25%(Q1)',
                       '75%': '75%(Q3)', 'max': 'Max', 'min': 'Min'})
        df_dict = {}
        i = 0
        for df in df_describes:
            df_dict[labels[i]] = df.to_dict()
            i += 1
        return JsonResponse(status=status.HTTP_200_OK, data=df_dict, safe=False)
    elif type_of_graph == 2:
        # plot_three_portfolios_graph
        labels: list[str] = ['Safest', 'Sharpe', 'Max Returns']
        colors: list[str] = ['orange', 'green', 'red']
        max_returns_portfolio = three_best_portfolios[2]
        sharpe_portfolio = three_best_portfolios[1]
        min_variance_portfolio = three_best_portfolios[0]
        portfolios_dict = helpers.ThreePortfolios.sub_plots(
            colors, labels, max_returns_portfolio, sharpe_portfolio, min_variance_portfolio, sectors,
            three_best_sectors_weights
        )
        i = 0
        all_stocks = helpers2.get_all_stocks_table()
        for stock_list in three_best_portfolios:
            my_dict = stock_list.to_dict()
            final_dict = {}
            for key, value in my_dict.items():
                if 'Weight' in key:
                    stock = key.split()[0]
                    name = all_stocks.loc[all_stocks['Symbol'] == stock, 'description'].iloc[0]
                    value_f = next(iter(value.values()))
                    final_dict[name + " - " + key] = value_f
            portfolios_dict[labels[i]]['stocks'] = final_dict
            i += 1
        return JsonResponse(status=status.HTTP_200_OK, data=portfolios_dict, safe=False)
    elif type_of_graph == 3:
        # plot_stat_model_graph
        closing_prices_table_path = (settings_service.BASIC_STOCK_COLLECTION_REPOSITORY_DIR
                                     + stocks_collection_number + '/')
        data = {
            'stocks_symbols': stocks_symbols,
            'ml_answer': ml_answer,
            'model_answer': model_answer,
            'settings_service.NUM_OF_YEARS_HISTORY': settings_service.NUM_OF_YEARS_HISTORY,
            'closing_prices_table_path': closing_prices_table_path
        }
        return JsonResponse(status=status.HTTP_200_OK, data=data, safe=False)


@login_required
@api_view(["PUT"])
def update_all_tables(request):
    try:
        data_management.update_all_tables()
    except Exception as e:
        string = "Exception occured: " + str(e)
        return JsonResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=string, safe=False)
    return JsonResponse(status=status.HTTP_200_OK, data="Updated all tables!", safe=False)