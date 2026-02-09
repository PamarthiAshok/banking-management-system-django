from django.db import models
from django.utils import timezone

class BankAccount(models.Model):
    GENDER_CHOICES=[
        ('MALE','Male'),
        ('FEMALE','Female'),
        ('OTHER','Other'),
    ]

    NOMINEE_RELATION_CHOICES=[
        ('FATHER','Father'),
        ('MOTHER','Mother'),
        ('SPOUSE','Spouse'),
        ('BROTHER','Brother'),
        ('SISTER','Sister'),
        ('OTHER','Other'),
    ]

    account_number=models.BigAutoField(primary_key=True)
    full_name=models.CharField(max_length=100)
    date_of_birth=models.DateField()
    phone_number=models.CharField(max_length=15,unique=True)
    email=models.EmailField(unique=True)
    aadhaar_number=models.CharField(max_length=12,unique=True)
    pan_number=models.CharField(max_length=10,unique=True)
    profile_photo=models.ImageField(upload_to='profile_photos/',null=True,blank=True)
    gender=models.CharField(max_length=10,choices=GENDER_CHOICES)
    address=models.TextField()
    state=models.CharField(max_length=50)
    account_balance=models.DecimalField(max_digits=12,decimal_places=2,default=1000.00)

    transaction_pin=models.CharField(max_length=128,blank=True)

    nominee_name=models.CharField(max_length=100)
    nominee_phone=models.CharField(max_length=10)
    nominee_relationship=models.CharField(max_length=20,choices=NOMINEE_RELATION_CHOICES)

    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def display_account_number(self):
        return f"123{self.account_number:08d}"
    def __str__(self):
        return self.display_account_number()
    
class Transaction(models.Model):
    TRANSACTION_TYPES=[
        ('DEPOSIT','Deposit'),
        ('WITHDRAW','Withdraw'),
        ('TRANSFER_SENT','Transfer Sent'),
        ('TRANSFER_RECEVIED','Transfer Received'),
    ]

    account=models.ForeignKey(BankAccount,on_delete=models.CASCADE)
    transaction_type=models.CharField(max_length=20,choices=TRANSACTION_TYPES)

    amount=models.DecimalField(max_digits=12,decimal_places=2)
    balance_after_transaction=models.DecimalField(max_digits=12,decimal_places=2)

    description=models.CharField(max_length=200,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.account.display_account_number()}-{self.transaction_type}-₹{self.amount}"