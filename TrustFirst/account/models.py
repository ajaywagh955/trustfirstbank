from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from .utils import generate_card_number, generate_cvv
import uuid

# Create your models here.


class UserProfile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100,default="")
    is_varified = models.BooleanField(default=False)
    mobile_number = models.CharField(max_length=20)
    Full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField(default="")
    Gender = (
        ('Male','Male'),
        ('Female','Female'),
        ('Prefer_Not_Say', "Prefer Not Say")
    )
    gender = models.CharField(max_length=30,choices=Gender)
    address = models.CharField(max_length=250)
    zip = models.CharField(max_length=10)
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    

    def __str__(self):
        return f"Username :- {self.user.username}   --------  Mobile Number :- {self.mobile_number} ---------- Account Number :- {self.account_number}  ----------- Balance :- {self.balance}"
    
class ATMCard(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    card_number = models.BigIntegerField(unique=True)
    expiration_date = models.DateField()
    cvv = models.PositiveIntegerField()
    user_name = models.CharField(max_length=255,default="")

    def create_with_expiration_and_cvv(self):
        self.card_number = generate_card_number()
        self.expiration_date = timezone.now() + timedelta(days=5 * 365)
        self.cvv = generate_cvv()
        self.user_name = self.user.Full_name 
        self.save()

    @classmethod
    def create_for_user(cls, user_profile):
        atm_card = cls(user=user_profile)
        atm_card.create_with_expiration_and_cvv()
        return atm_card

    def __str__(self):
        return f"Card Number :- {self.card_number} , Username :- {self.user_name}"



class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('Withdraw', 'Withdraw'),
        ('Deposit', 'Deposit'),
    )

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Username : {self.user_profile.user.username}  ----------  Transaction ID: {self.transaction_id}  ------ Type: {self.transaction_type} ------- Amount: {self.amount}"
    
    
