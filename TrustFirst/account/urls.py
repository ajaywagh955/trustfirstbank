from django.urls import path
from .views import *
from . import views


urlpatterns = [
    path('',Index,name="index"),
    path('register/',Register,name="Register"),
    path('register_otp/',RegisterOTP,name="Register_otp"),
    path('register_all/',RegisterAll,name="register_all"),
    path('login/',Login,name="login"),
    path('login_otp/',LoginOTP,name="login_otp"),
    path('dashboard/',dashboard,name="dashboard"),
    path('dashboard_card/',DashboardCard,name="dashboard_card"),
    path('dashboard_view_card/',DashboardViewCard,name="dashboard_view_card"),
    path('dashboard_history/',DashboardHistory,name="dashboard_history"),
    path('dashboard_profile/',DashboardProfile,name="dashboard_profile"),
    path('dashboard_trasfer',DashboardTransfer,name="dashboard_transfer"),   
    path('dashboard_passbook/',DashboardPassbook,name="dashbaord_passbook"),
    path('dashboard_request_money/', DashboardRequestMoney, name="dashboard_request_money"),
    path('dashboard_send_money/',DashboardSendMoney,name="dashboard_send_money"),
    path('dashboard_total_balance/',DashboardTotalBalance,name="dashboard_total_balance"),
    path('dashboard_total_deposite/',DashboardTotalDeposite,name="dashboard_total_deposite"),
    path('dashboard_total_withdraw/',DashboardTotalWithdraw,name="dashboard_total_withdraw"),
    path('token/',token_send,name="token_send"),
    path('success',Suceess,name="success"),
    path('varify/<auth_token>',varify,name="varify"),
    path('error',error_page,name="error")
]
