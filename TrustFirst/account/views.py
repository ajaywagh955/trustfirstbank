from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from .models import *
import uuid
import random
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail


# Now
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
from django.utils import timezone
from .utils import generate_card_number, generate_cvv
from django.utils.dateparse import parse_date
from django.template.loader import render_to_string
from django.utils.html import strip_tags





# Create your views here.


def Index(request):
    return render(request,'account/index.html')





def Register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        full_name = request.POST.get('Full_name')
        mobile_number = request.POST.get('mobile_number')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        zip_code = request.POST.get('zip_code')

        # account_number = str(uuid.uuid4().hex)[:10]
        account_number = random.randint(1000000000, 9999999999)
        

        if password == confirm_password:
            if not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists():
                messages.success(request, "Username or email is taken")
                user = User.objects.create_user(username=username, password=password, email=email)
                user.first_name = full_name
                user.save()

                auth_token = str(uuid.uuid4())
                UserProfile.objects.create(
                    user=user,
                    Full_name=full_name,
                    mobile_number=mobile_number,
                    date_of_birth=date_of_birth,
                    gender=gender,
                    address=address,
                    zip=zip_code,
                    account_number=account_number,
                    auth_token = auth_token
                )
                
                send_mail_after_registration(email,auth_token)
                return redirect('token_send')
            else:
                # If username or email already exists, show an error message or handle it accordingly
                return render(request, 'account/account/index.html', {'error_message': 'Username or email already exists.'})

    return render(request, 'account/account/index.html')




def Suceess(request):
    return render(request,'account/account/success.html')


def token_send(request):
    return render(request,'account/account/token_send.html')


def varify(request,auth_token):
    try:
        profile_obj = UserProfile.objects.filter(auth_token=auth_token).first()


        if profile_obj:
            if profile_obj.is_varified:
                messages.success(request, "Your account is already varified")
                # error_message = "Your account is already varified varified"
                return redirect('/login')

            # if profile_obj.is_varified:
            #     messages.success(request, "Your account is already varified varified")
            #     # error_message = "Your account is not varified please check your mail"
            #     return redirect('/login')

            profile_obj.is_varified = True
            profile_obj.save()
            messages.success(request, "Your account has been varified")
            # error_message = "Invalid username or password."
            return redirect('/login')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)
        

def varify(request, auth_token):
    try:    
        profile_obj = UserProfile.objects.filter(auth_token=auth_token).first()


        if profile_obj:
            if profile_obj.is_varified:
                messages.success(request, "Your account is already verified.")
                return redirect('/login')

            profile_obj.is_varified = True
            profile_obj.save()
            messages.success(request, "Your account has been verified.")
            return redirect('/login')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)
        return redirect('login')
    





def error_page(request):
    return render(request,'account/account/error.html')

def send_mail_after_registration(email,token):
    subject = 'Please varify Your Account For Enjoy the TrustFirst Banking Service'
    message = f"Hii Click on the link to varify your account http://127.0.0.1:8000/varify/{token}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject,message,email_from,recipient_list)
    


# Register Functions


def RegisterAll(request):
    return render(request, 'account/account/all_details.html')

def RegisterOTP(request):
    return render(request, 'account/account/otp.html')



# Login Functions

def Login(request):
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=username).first()
        if user_obj is None:
            messages.success(request, "User Not Found")
            return redirect('login')

        profile_obj = UserProfile.objects.filter(user=user_obj).first()

        if not profile_obj.is_varified:
            messages.success(request, "Your account is not varified please check your email")

            return redirect('login')

        user = authenticate(username=username,password=password)
        if user is None:
            messages.success(request, "Wrong Password")
            return redirect('login')

        login(request,user)
        return redirect('dashboard')


    else:
        return render(request, 'account/login/login.html')




    

def LoginOTP(request):
    return render(request, 'account/login/otp.html')




# Main Dashboard Functions




@login_required(login_url='login')
def dashboard(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('login')

    user_profile = UserProfile.objects.get(user=request.user)
    transactions = Transaction.objects.filter(user_profile=user_profile).order_by('-transaction_time')[:4]
        

    return render(request, 'account/dashboard/index.html', {'user_profile': user_profile,'transactions': transactions})


def generate_card_number():
    min_card_number = 10 ** 15
    max_card_number = (10 ** 16) - 1
    return random.randint(min_card_number, max_card_number)

def generate_cvv():
    return random.randint(100, 999)



def send_atm_card_email(user_email, card_number, expiration_date, cvv):
    subject = "Your ATM Card Details"
    context = {
        "card_number": card_number,
        "expiration_date": expiration_date,
        "cvv": cvv,
    }
    html_message = render_to_string("account/dashboard/email/atm_card_details.html", context)
    plain_message = strip_tags(html_message)

    send_mail(subject, plain_message, DEFAULT_FROM_EMAIL, [user_email], html_message=html_message)



@login_required
def DashboardCard(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == "POST":
        # Check if the user already has an ATM card
        if ATMCard.objects.filter(user=user_profile).exists():
            messages.error(request, "You already have an ATM card.")
            return redirect('dashboard_view_card')

        # Create an ATM card instance with an expiration date and CVV for the user
        atm_card = ATMCard(user=user_profile)
        atm_card.create_with_expiration_and_cvv()  # Generate card details and save the instance

        # Send the ATM card information email
        send_atm_card_email(request.user.email, atm_card.card_number, atm_card.expiration_date, atm_card.cvv)

        messages.success(request, "Your ATM card has been generated successfully.")
        return redirect('dashboard_view_card')  # Redirect to dashboard_view_card page

    return render(request, 'account/dashboard/card.html')
    # return render(request, 'account/dashboard/card.html')
    
    
    
@login_required
def DashboardViewCard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    try:
        atm_card = ATMCard.objects.get(user=user_profile)
    except ATMCard.DoesNotExist:
        atm_card = None

    return render(request, 'account/dashboard/view_card.html', {'atm_card': atm_card})
    # return render(request, 'account/dashboard/view_card.html')






# def DashboardHistory(request):
#     return render(request, 'account/dashboard/history.html')


@login_required(login_url='login')
def DashboardHistory(request):
    user_profile = UserProfile.objects.get(user=request.user)
    transactions = Transaction.objects.filter(user_profile=user_profile)
    

    return render(request, 'account/dashboard/history.html', {'transactions': transactions})




@login_required(login_url='login')
def DashboardProfile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('login`')

    return render(request, 'account/dashboard/profile.html',{'user_profile': user_profile})

def DashboardTransfer(request):
    return render(request, 'account/dashboard/transfer.html')




# Dashboard Show_Menu Functions 



@login_required(login_url='login')
def DashboardPassbook(request):
    user_profile = UserProfile.objects.get(user=request.user)

    # Get the start and end date from the user's input
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Parse the dates if provided, else set default date range
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    # Filter transactions based on the date range and user_profile
    transactions = Transaction.objects.filter(user_profile=user_profile)
    if start_date:
        transactions = transactions.filter(transaction_time__gte=start_date)
    if end_date:
        transactions = transactions.filter(transaction_time__lte=end_date)

    # Retrieve only the latest 4 transactions
    transactions = transactions.order_by('-transaction_time')[:4]

    return render(request, 'account/dashboard/show_menu/passbook.html', {
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
    })
    # return render(request, 'account/dashboard/show_menu/passbook.html')``














def send_mail_after_send_money(email, subject, message):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    
    




@login_required(login_url='login')
def DashboardSendMoney(request):
    if request.method == "POST":
        sender_user = request.user
        receiver_account_number = request.POST.get('receiver_account_number')
        amount = Decimal(request.POST.get('amount'))

        # Find the sender and receiver user profiles
        try:
            sender_profile = UserProfile.objects.select_for_update().get(user=sender_user)
            receiver_profile = UserProfile.objects.select_for_update().get(account_number=receiver_account_number)

            if receiver_account_number == sender_profile.account_number:
                messages.error(request, "You can't send money to yourself.")
                return redirect('dashboard_send_money')
                
        except ObjectDoesNotExist:
            messages.error(request, "Receiver account number not found.")
            return redirect('dashboard_send_money')

        # Check if the sender has enough balance
        if sender_profile.balance < amount:
            messages.error(request, "Insufficient balance to send money.")
            return redirect('dashboard_send_money')
        
        # Perform the money transfer and update balances
        sender_profile.balance -= amount
        sender_profile.save()
        receiver_profile.balance += amount
        receiver_profile.save()


        # Create a Transaction record for the sender (withdrawal)
        transaction_obj_sender = Transaction.objects.create(
            user_profile=sender_profile,
            transaction_type='Withdraw',
            amount=amount,
        )

        # Create a Transaction record for the receiver (deposit)
        transaction_obj_receiver = Transaction.objects.create(
            user_profile=receiver_profile,
            transaction_type='Deposit',
            amount=amount,
        )

        # ... (rest of the code)


        
        # Get the current time and date
        transaction_time = timezone.now()

        # Prepare transaction details for the email
        sender_name = sender_user.get_full_name()
        receiver_name = receiver_profile.Full_name
        receiver_account_number = receiver_profile.account_number

         # Prepare messages for sender and receiver emails
        message_sender = (
            f"Transaction Details\n\n"
            f"Hello {sender_name},  Amount: ₹{amount} is Debited From Your Account See All the d-Details Below \n\n"
            f"Transaction ID: {transaction_obj_sender.transaction_id}\n"
            f"Amount: ₹{amount}\n"
            f"Transaction Time: {transaction_time}\n"
            f"Receiver Name: {receiver_name}\n"
            f"Receiver Account Number: {receiver_account_number}\n"
            f"Your available balance is ₹{sender_profile.balance}\n\n"
            f"Thank you for your transaction."
        )




        message_receiver = (
            f"Transaction Details\n\n"
            f"Hello {receiver_name},  Amount: ₹{amount} is Credited in Your Account See all the details below \n\n"
            f"Transaction ID: {transaction_obj_receiver.transaction_id}\n"
            f"Amount: ₹{amount}\n"
            f"Transaction Time: {transaction_time}\n"
            f"Sender Name: {sender_name}\n"
            f"Sender Account Number: {sender_profile.account_number}\n"
            f"Your current balance is ₹{receiver_profile.balance}\n\n"
            f"Thank you for your transaction."
        )

        # Send transaction-related emails to sender and receiver
        send_mail_after_send_money(sender_user.email, "Transaction Details", message_sender)
        send_mail_after_send_money(receiver_profile.user.email, "Transaction Details", message_receiver)

        messages.success(request, f"Successfully sent ₹{amount} to account number {receiver_account_number}.")
        return redirect('dashboard_total_balance')
    
    return render(request, 'account/dashboard/show_menu/send_money.html')









@login_required(login_url='login')
def DashboardTotalBalance(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        balance = user_profile.balance
    except UserProfile.DoesNotExist:
        # Handle the case when the user profile does not exist
        balance = 0  # Default balance if the profile is not found
        
    context = {
        'balance': balance
    }
    
    return render(request, 'account/dashboard/show_menu/total_balance.html',context)


@login_required
def DashboardTotalDeposite(request):
    user_profile = UserProfile.objects.get(user=request.user)
    deposit_transactions = Transaction.objects.filter(user_profile=user_profile, transaction_type='Deposit')
    return render(request, 'account/dashboard/show_menu/total_deposite.html', {'deposit_transactions': deposit_transactions}) 
    # return render(request, 'account/dashboard/show_menu/total_deposite.html')












@login_required(login_url='login')
def DashboardRequestMoney(request):
    if request.method == "POST":
        receiver_user = request.user
        amount = Decimal(request.POST.get('amount'))

        # Find the receiver user profile
        receiver_profile = UserProfile.objects.get(user=receiver_user)

        # Update the receiver's balance
        receiver_profile.balance += amount
        receiver_profile.save()

        # # Create a Transaction record for the deposit
        # transaction_obj = Transaction.objects.create(
        #     user_profile=receiver_profile,
        #     transaction_type='Deposit',
        #     amount=amount,
        # )
        # transaction_obj.save()

        # Create a Transaction record for the receiver (deposit)
        transaction_obj_receiver = Transaction.objects.create(
            user_profile=receiver_profile,
            transaction_type='Deposit',
            amount=amount,
        )


        # Get the current time and date
        transaction_time = timezone.now()

        # Fetch the current balance for the receiver
        receiver_balance = receiver_profile.balance

        # Prepare transaction details for the email
        # Prepare transaction details for the email
        receiver_name = receiver_user.get_full_name()
        receiver_account_number = receiver_profile.account_number


        # Prepare the deposit-related email message
        message_receiver = (
            f"Transaction Details\n\n"
            f"Hello {receiver_name},  Amount: ₹{amount} Deposite in Your Account, See All the Details below\n\n"
            f"Transaction ID: {transaction_obj_receiver.transaction_id}\n"  # Transaction ID for receiver
            f"Amount: ₹{amount}\n"
            f"Transaction Time: {transaction_time}\n"
            f"Receiver Name: {receiver_name}\n"
            f"Receiver Account Number: {receiver_account_number}\n"
            f"Your current balance is ₹{receiver_balance}\n\n"
            f"Thank you for your deposit."
        )

        # Send the deposit-related email to the receiver
        send_mail_after_send_money(receiver_user.email, "Transaction Details", message_receiver)

        messages.success(request, f"Successfully deposited ₹{amount} to your account.")
        return redirect('dashboard_total_balance')

    return render(request, 'account/dashboard/show_menu/request_money.html')















@login_required(login_url='login')
def DashboardTotalWithdraw(request):
    user_profile = UserProfile.objects.get(user=request.user)
    withdraw_transactions = Transaction.objects.filter(user_profile=user_profile, transaction_type='Withdraw')
    return render(request, 'account/dashboard/show_menu/total_withdraw.html', {'withdraw_transactions': withdraw_transactions})

    # return render(request, 'account/dashboard/show_menu/total_withdraw.html')










