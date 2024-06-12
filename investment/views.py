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


# from chatgpt

# class investmentListCreate(generics.ListCreateAPIView):
#     queryset = Investment.objects.all()
#     serializer_class = investmentSerializer
#
#
# class investmentDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Investment.objects.all()
#     serializer_class = investmentSerializer

# from YouTube
# @api_view(['GET', 'POST'])
# def investment_list(request):
#     if request.method == 'GET':
#         investments = Investment.objects.all()
#         serializer = investmentSerializer(investments, many=True)
#         return JsonResponse(serializer.data, safe=False)
#
#     if request.method == 'POST':
#         serializer = investmentSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             # Return a response with the validation errors
#             return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT', 'DELETE'])
# def investment_detail(request, id_pk, format=None):
#
#     try:
#         investment = Investment.objects.get(pk=id_pk)
#     except Investment.DoesNotExist:
#         return JsonResponse(status=status.HTTP_404_NOT_FOUND, data=request.data)
#
#     if request.method == 'GET':
#         serializer = investmentSerializer(investment)
#         return JsonResponse(serializer.data)
#
#     elif request.method == 'PUT':
#         serializer = investmentSerializer(investment, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data)
#         return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         investment.delete()
#         return JsonResponse(status=status.HTTP_204_NO_CONTENT, data=request.data)


# Investment
@login_required
# @require_http_methods(["GET"])
@api_view(['GET'])
def investments_list_view(request):
    is_form_filled: bool = _check_if_preferences_form_is_filled(request)
    if is_form_filled:
        investor_user: InvestorUser = get_object_or_404(InvestorUser, user=request.user)
        # just an example, need to sort out authentication
        # investor_user = InvestorUser.objects.get(id=5)
        investments = list(Investment.objects.filter(investor_user=investor_user, mode=Investment.Mode.USER).values())
        print(investments)
        return JsonResponse(status=status.HTTP_200_OK, data=investments, safe=False)
#     else or try except??


@login_required
@api_view(["POST"])
def add_investment(request):
    print('11ds1')
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


            # do we want to send an email??

            # # send report to user in email
            # subject: str = 'Investment Report From RoboAdvisor'
            # message: str = (
            #     'Here is your investment report.\n'
            #     f'You have invested {amount} dollars.\n\n\n'
            #     'Sincerely yours,\n'
            #     'RoboAdvisor team'
            # )
            # recipient_list: list[str] = [request.user.email]
            # attachment_path: str = f'{settings.USER_IMAGES}{str(request.user.id)}/Investment Report.png'
            # web_actions.send_email(
            #     subject=subject, message=message, recipient_list=recipient_list, attachment_path=attachment_path
            # )

            # return redirect('my_investments_history')
            investments = list(
                Investment.objects.filter(investor_user=investor_user, mode=Investment.Mode.USER).values())
            investments.insert(0, ('new invetsment is of amount : ', amount))
            return JsonResponse(status=status.HTTP_200_OK, data=investments, safe=False)
        else:
            raise ValueError('Invalid amount value')
    else:
        raise BadRequest


# probably not needed, I think its just for the html view
# @require_http_methods(["GET"])
# def _investments_list_view(request) -> QuerySet[Investment]:
#     page = request.GET.get("page", None)
#     # Assuming you want to retrieve the single InvestorUser object for the current user
#     # investor_user = get_object_or_404(InvestorUser, user=request.user)
#
#     investor_user = InvestorUser.objects.get(id=5)
#
#     # Now, you can use the retrieved investor_user to filter the investments
#     investments = Investment.objects.filter(investor_user=investor_user, mode=Investment.Mode.USER)
#
#     if request.method == 'GET':
#         paginator = Paginator(investments, per_page=3)
#         try:
#             investments = paginator.page(page)
#         except PageNotAnInteger:
#             investments = paginator.page(1)
#         except EmptyPage:
#             investments = paginator.page(paginator.num_pages)
#     return investments


# Investment Portfolio

# I don't think this func is needed, is there a logical need for a func fo or app that will get a request that will
# just go to the homepage?
# @login_required
# def investment_main(request):
#     context = {
#         'title': 'Investments',
#     }
#     return render(request, 'investment/investments_main.html', context=context)


# shows the user portfolio. this doesnt take any data from the req too. not needed?
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
        print(2)
        try:
            get_object_or_404(InvestorUser, user=request.user)
        except Exception as e:
            print('error in method')
        print(3)
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
