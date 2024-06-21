from numbers import Number
import json
from django.template.context_processors import csrf
from django.views.decorators.http import require_http_methods
from crispy_forms.utils import render_crispy_form
from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework import status

from service.util import web_actions
from service.util import data_management
# from our_core.forms import AlgorithmPreferencesForm, InvestmentPreferencesForm, AdministrativeToolsForm
from our_core.models import TeamMember, QuestionnaireA, QuestionnaireB
from users.models import InvestorUser


# def homepage(request):
#     context = {'team_members': TeamMember.objects.all()}
#     return render(request, 'core/homepage.html', context=context)


# def about(request):
#     return render(request, 'core/about.html', context={'title': 'About Us'})


@login_required
# @require_http_methods(["GET", "POST"])
@api_view(["GET", "POST"])
def administrative_tools_form(request):
    if request.user.is_superuser is False:
        return JsonResponse(status=status.HTTP_403_FORBIDDEN, safe=False)
    if request.method == 'GET':
        models_data: dict[Number] = data_management.get_models_data_from_collections_file()
        # context = {
        #     'title': 'Administrative Tools',
        #     'form': AdministrativeToolsForm(initial=models_data),
        # }
        # return render(request, 'core/form.html', context=context)
        return JsonResponse(status=status.HTTP_200_OK, data=models_data, safe=False)
    elif request.method == 'POST':
        # form = AdministrativeToolsForm(request.POST)
        data = request.data
        print(data)
        try:
        # if form.is_valid():  # CREATE and UPDATE
            # Access cleaned data from the form
            with transaction.atomic():
                num_por_simulation = data['num_por_simulation']
                min_num_por_simulation = data['min_num_por_simulation']
                record_percent_to_predict = data['record_percent_to_predict']
                test_size_machine_learning = data['test_size_machine_learning']
                selected_ml_model_for_build = data['selected_ml_model_for_build']
                gini_v_value = data['gini_v_value']
                data_management.update_models_data_settings(
                    num_por_simulation=num_por_simulation,
                    min_num_por_simulation=min_num_por_simulation,
                    record_percent_to_predict=record_percent_to_predict,
                    test_size_machine_learning=test_size_machine_learning,
                    selected_ml_model_for_build=selected_ml_model_for_build,
                    gini_v_value=gini_v_value,
                )
            # messages.success(request, message="Successfully updated models' data.")
            data['message'] = "Successfully updated models' data."
            return JsonResponse(status=status.HTTP_200_OK, data=data, safe=False)
        # else:  # CREATE and UPDATE
        except Exception as e:
            # context = {
            #     'title': 'Administrative Tools',
            #     'form': form,
            # }
            # ctx = {}
            # ctx.update(csrf(request))
            # form_html = render_crispy_form(form=context['form'], context=ctx)
            # return HttpResponse(form_html)
            return JsonResponse(status=status.HTTP_409_CONFLICT, data=None, safe=False)
    else:
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST, safe=False)


@login_required
# @require_http_methods(["GET", "POST"])
@api_view(["GET", "POST"])
def capital_market_algorithm_preferences_form(request):
    try:
        preferences = QuestionnaireA.objects.get(user=request.user)
    except QuestionnaireA.DoesNotExist:
        preferences = None
    if request.method == 'GET':
        pass
        # if preferences is None:  # CREATE
            # context = {
            #     'title': 'Fill Form',
            #     'form': AlgorithmPreferencesForm(form_type='create')
            # }
            # return render(request, 'core/form.html', context=context)
            # form = AlgorithmPreferencesForm(form_type='create')
            # return JsonResponse(status=status.HTTP_201_CREATED, data="Created!", safe=False)
        # else:  # UPDATE
            # context = {
            #     'title': 'Update Filled Form',
            #     'form': AlgorithmPreferencesForm(form_type='update', instance=preferences)
            # }
            # return render(request, 'core/form.html', context=context)
            # form = AlgorithmPreferencesForm(form_type='update', instance=preferences)
            # return JsonResponse(status=status.HTTP_201_CREATED, data="updated!", safe=False)
    elif request.method == 'POST':
        if preferences is None:  # CREATE
            # form = AlgorithmPreferencesForm(request.POST)
            data = request.data
            questionnaire = QuestionnaireA(user=request.user)
            questionnaire.ml_answer = data['ml_answer']
            questionnaire.model_answer = data['model_answer']
            questionnaire.save()
            data['message'] = "Successfully created!."
            return JsonResponse(status=status.HTTP_201_CREATED, data=data, safe=False)
        else:  # UPDATE
            # form = AlgorithmPreferencesForm(request.POST, instance=preferences)
            data = request.data
            questionnaire = QuestionnaireA.objects.get(user=request.user)
            questionnaire.ml_answer = data['ml_answer']
            questionnaire.model_answer = data['model_answer']
            questionnaire.save()
            data['message'] = "Successfully Updated!."
            return JsonResponse(status=status.HTTP_201_CREATED, data=data, safe=False)

        # if form.is_valid():  # CREATE and UPDATE
        #     form.instance.user = request.user
        #     form.save()
        #     return redirect('capital_market_investment_preferences_form')
        # else:  # CREATE and UPDATE
        #     context = {
        #         'title': 'Update Filled Form',
        #         'form': form,
        #     }
        #     ctx = {}
        #     ctx.update(csrf(request))
        #     form_html = render_crispy_form(form=context['form'], context=ctx)
        #     return HttpResponse(form_html)
    else:
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST, safe=False)


@login_required
@api_view(["GET", "POST"])
def capital_market_investment_preferences_form(request):
    try:
        questionnaire_a = get_object_or_404(QuestionnaireA, user=request.user)
        print(questionnaire_a, "wowwwww")
    except Http404:
        return HttpResponse("You must have an instance of QuestionnaireA to fill this form.", status=404)

    # Each user fills this form, and it gets a rating from 3 to 9
    try:
        questionnaire_b = QuestionnaireB.objects.get(user=request.user)
    except QuestionnaireB.DoesNotExist:
        questionnaire_b = None
        # Retrieve the UserPreferencesA instance for the current user

    #     I don't think we really need the GET??
    if request.method == 'GET':
        pass
    #     try:
    #         investor_user: InvestorUser = InvestorUser.objects.get(user=request.user)
    #         stocks_collections_number: str = investor_user.stocks_collection_number
    #     except InvestorUser.DoesNotExist:
    #         stocks_collections_number: str = '1'
    #     if questionnaire_b is None:  # CREATE
    #         context = {
    #             'title': 'Fill Form',
    #             'form': InvestmentPreferencesForm(
    #                 form_type='create',
    #                 user_preferences_instance=questionnaire_a,
    #                 collections_number=stocks_collections_number,
    #             )
    #         }
    #         return render(request, 'core/form.html', context=context)
    #     else:  # UPDATE
    #         context = {
    #             'title': 'Update Filled Form',
    #             'form': InvestmentPreferencesForm(
    #                 form_type='update',
    #                 instance=questionnaire_b,
    #                 user_preferences_instance=questionnaire_a,
    #                 collections_number=stocks_collections_number,
    #             )
    #         }
    #         return render(request, 'core/form.html', context=context)

    elif request.method == 'POST':
        # if questionnaire_b is None:  # CREATE
        #     form = InvestmentPreferencesForm(
        #         request.POST,
        #         user_preferences_instance=questionnaire_a
        #     )
        # else:  # UPDATE
        #     form = InvestmentPreferencesForm(
        #         request.POST,
        #         user_preferences_instance=questionnaire_a,
        #         instance=questionnaire_b
        #     )
        # if form.is_valid():  # CREATE and UPDATE
        if True:
            # DEBUGGING, without this the code won't work
            # print("", form.errors)
            # Sum answers' values
            try:
                investor_user: InvestorUser = InvestorUser.objects.get(user=request.user)
                stocks_collections_number: str = investor_user.stocks_collection_number
            except InvestorUser.DoesNotExist:
                stocks_collections_number: str = '1'
            # answer_1_value = int(form.cleaned_data['answer_1'])
            # answer_2_value = int(form.cleaned_data['answer_2'])
            # answer_3_value = int(form.cleaned_data['answer_3'])
            # answers_sum = answer_1_value + answer_2_value + answer_3_value
            # Form instance
            # questionnaire_b: QuestionnaireB = form.instance
            # questionnaire_b.user = request.user
            # questionnaire_b.answers_sum = answers_sum
            # questionnaire_b.save()
            # form.save()
            data = request.data
            if questionnaire_b is None:
                questionnaire_b = QuestionnaireB(user=request.user)
                questionnaire_b.answer_1 = data['answer_1']
                questionnaire_b.answer_2 = data['answer_2']
                questionnaire_b.answer_3 = data['answer_3']
                answers_sum = data['answer_1'] + data['answer_2'] + data['answer_3']
                questionnaire_b.answers_sum = answers_sum
                questionnaire_b.save()
            else:
                questionnaire_b.answer_1 = data['answer_1']
                questionnaire_b.answer_2 = data['answer_2']
                questionnaire_b.answer_3 = data['answer_3']
                answers_sum = data['answer_1'] + data['answer_2'] + data['answer_3']
                questionnaire_b.answers_sum = answers_sum
                questionnaire_b.save()
            (
                annual_max_loss, annual_returns, annual_sharpe, annual_volatility, daily_change, monthly_change,
                risk_level, sectors_names, sectors_weights, stocks_symbols, stocks_weights, total_change, portfolio) \
                = web_actions.create_portfolio_and_get_data(answers_sum, stocks_collections_number, questionnaire_a)
            try:
                investor_user = InvestorUser.objects.get(user=request.user)
                # If we get here, it means that the user is on UPDATE form (there is InvestorUser instance)
                print("updateeeeeeeeeeeee")
                investor_user.risk_level = risk_level
                investor_user.stocks_symbols = stocks_symbols
                investor_user.stocks_weights = stocks_weights
                investor_user.sectors_names = sectors_names
                investor_user.sectors_weights = sectors_weights
                investor_user.annual_returns = annual_returns
                investor_user.annual_max_loss = annual_max_loss
                investor_user.annual_volatility = annual_volatility
                investor_user.annual_sharpe = annual_sharpe
                investor_user.total_change = total_change
                investor_user.monthly_change = monthly_change
                investor_user.daily_change = daily_change
                # how there wasn't  a save originally?!?!!!?
                investor_user.save()
                data['message'] = "Successfully Updated!."
                return JsonResponse(status=status.HTTP_201_CREATED, data=data, safe=False)
            except InvestorUser.DoesNotExist:
                # If we get here, it means that the user is on CREATE form (no InvestorUser instance)
                InvestorUser.objects.create(
                    user=request.user,
                    risk_level=risk_level,
                    total_investment_amount=0,
                    stocks_symbols=stocks_symbols,
                    stocks_weights=stocks_weights,
                    sectors_names=sectors_names,
                    sectors_weights=sectors_weights,
                    annual_returns=annual_returns,
                    annual_max_loss=annual_max_loss,
                    annual_volatility=annual_volatility,
                    annual_sharpe=annual_sharpe,
                    total_change=total_change,
                    monthly_change=monthly_change,
                    daily_change=daily_change,
                )
            # Frontend
            web_actions.save_three_user_graphs_as_png(user=request.user, portfolio=portfolio)
            data['message'] = "Successfully Created!."
            return JsonResponse(status=status.HTTP_201_CREATED, data=data, safe=False)
            # return redirect('profile_portfolio')

        # else:  # CREATE and UPDATE
        #     context = {
        #         'form': form,
        #     }
        #     ctx = {}
        #     ctx.update(csrf(request))
        #     form_html = render_crispy_form(form=context['form'], context=ctx)
        #     return HttpResponse(form_html)
    else:
        raise Http404
