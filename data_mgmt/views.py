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
        yields_dict = {}
        for y in yields:
            yields_dict[y.name] = y.to_dict()
        return JsonResponse(status=status.HTTP_200_OK, data=yields_dict, safe=False)
    elif type_of_graph == 2:
        # plot_three_portfolios_graph
        three_best_portfolios_dict = {}
        sectors_dict = {}
        for portfolio in three_best_portfolios:
            three_best_portfolios_dict[int(portfolio.index[0])] = portfolio.to_dict(orient='records')
        pct_change_table_dict = pct_change_table.to_dict(orient='records')
        for s in sectors:
            sectors_dict[s.name] = s.to_dict()
        data = {
            'three_best_portfolios': three_best_portfolios_dict,
            'three_best_sectors_weights': three_best_sectors_weights,
            'sectors': sectors_dict,
            'pct_change_table': pct_change_table_dict
        }
        return JsonResponse(status=status.HTTP_200_OK, data=data, safe=False)
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

