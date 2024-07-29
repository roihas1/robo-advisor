from crispy_forms.templatetags.crispy_forms_filters import as_crispy_field
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import QuerySet
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

# from accounts.models import InvestorUser
from users.models import InvestorUser
from django.views.decorators.http import require_http_methods

from investment.forms import InvestmentsHistoryForm
from investment.models import Investment

from service.config import settings
from service.util import data_management, web_actions

from rest_framework import generics
from .serializers import investmentSerializer
from rest_framework.decorators import api_view
from rest_framework import status

# Investment
@login_required
@api_view(['GET'])
def investments_list_view(request):
    is_form_filled: bool = _check_if_preferences_form_is_filled(request)
    if is_form_filled:
        investor_user: InvestorUser = get_object_or_404(InvestorUser, user=request.user)
        # just an example, need to sort out authentication
        # investor_user = InvestorUser.objects.get(id=5)
        investments = list(Investment.objects.filter(investor_user=investor_user, mode=Investment.Mode.USER).values())
        return JsonResponse(status=status.HTTP_200_OK, data=investments, safe=False)

@login_required
@api_view(["POST"])
def add_investment(request):
    is_form_filled: bool = _check_if_preferences_form_is_filled(request)
    if is_form_filled is False:
        raise Http404
    # investments: QuerySet[Investment] = _investments_list_view(request)
    if request.method == 'POST':
        amount: int = int(request.headers.get('amount', -1))
        if amount > 0:
            investor_user: InvestorUser = get_object_or_404(InvestorUser, user=request.user)
            # just an example, need to sort out authentication
            # investor_user = InvestorUser.objects.get(id=5)
            Investment.objects.create(investor_user=investor_user, amount=amount,
                                      stocks_collection_number=investor_user.stocks_collection_number)
            investor_user.total_investment_amount += amount
            investor_user.save()
            # save report according to a new investment
            stocks_weights = investor_user.stocks_weights
            stocks_symbols = investor_user.stocks_symbols

            # Save image
            data_management.view_investment_report(str(request.user.id), amount, stocks_weights, stocks_symbols)
            investments = list(
                Investment.objects.filter(investor_user=investor_user, mode=Investment.Mode.USER).values())
            investments.insert(0, ('new invetsment is of amount : ', amount))
            return JsonResponse(status=status.HTTP_200_OK, data=investments, safe=False)
        else:
            raise ValueError('Invalid amount value')
    else:
        raise BadRequest

# Investment Portfolio
# @login_required
def profile_portfolio(request):
    is_form_filled: bool = _check_if_preferences_form_is_filled(request)
    context = {
        'user': request.user,
        'is_form_filled': is_form_filled,
        'title': 'Profile Portfolio',

    }
    return render(request, 'investment/profile_portfolio.html', context=context)


@login_required
def _check_if_preferences_form_is_filled(request):
    is_form_filled = True
    try:
        try:
            get_object_or_404(InvestorUser, user=request.user)
        except Exception as e:
            print('error in method')
    except Http404:
        is_form_filled = False
    return is_form_filled


# why a render is needed to check_positive_number?
def check_positive_number(request):
    form = InvestmentsHistoryForm(request.GET)
    context = {
        'field': as_crispy_field(form['amount']),
        'valid': not form['amount'].errors
    }
    return render(request, 'partials/field.html', context)
