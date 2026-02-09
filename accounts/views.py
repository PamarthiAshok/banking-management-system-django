from django.shortcuts import render, redirect
from .forms import AccountRegistrationForm
from .models import BankAccount, Transaction
from django.core.mail import send_mail
from django.conf import settings
import random
from .utils import hash_pin,verify_pin
import time
from decimal import Decimal
from django.db import transaction


# ---------------- HOME ----------------
def home_page(request):
    latest_account = BankAccount.objects.order_by('-created_at').first()

    return render(request, 'home_page.html', {
        'latest_account': latest_account
    })



# ---------------- CREATE ACCOUNT ----------------
def create_account(request):
    if request.method == 'POST':
        form = AccountRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            bank_account = form.save()

            send_mail(
                subject="Thank You for Creating an Account in FinTrust Bank",
                message=(
                    f"Dear {bank_account.full_name},\n\n"
                    f"Your account has been created successfully.\n"
                    f"Your Account Number is: {bank_account.display_account_number()}\n\n"
                    f"Thank you for choosing FinTrust Bank."
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[bank_account.email],
                fail_silently=True
            )

            return redirect('thankyou')
    else:
        form = AccountRegistrationForm()

    return render(request, 'create_account.html', {'form': form})


def thank_you(request):
    return render(request, 'thank_you.html')


# ---------------- PIN GENERATION ----------------
def pin_generation(request):
    message = ""

    if request.method == "POST":
        display_account_number = request.POST.get('account_number')
        mobile_number = request.POST.get('phone_number')

        if not display_account_number or not display_account_number.startswith("123"):
            message = "Invalid Account Number"
            return render(request, 'pin_generation.html', {'message': message})

        try:
            raw_account_number = int(display_account_number[3:])
            account = BankAccount.objects.get(account_number=raw_account_number)
        except:
            message = "Invalid Account Number"
            return render(request, 'pin_generation.html', {'message': message})

        if account.phone_number.strip() != mobile_number.strip():
            message = "Registered Mobile Number is Incorrect"
            return render(request, 'pin_generation.html', {'message': message})

        otp = random.randint(100000, 999999)
        request.session['otp'] = otp
        request.session['otp_created_at'] = int(time.time())
        request.session['account_number'] = account.account_number

        send_mail(
            subject="Your FinTrust Bank OTP",
            message=f"Your OTP for PIN generation is {otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[account.email],
            fail_silently=True
        )

        return redirect('validate_otp')

    return render(request, 'pin_generation.html', {'message': message})


# ---------------- VALIDATE OTP ----------------
def validate_otp(request):
    message = ""
    OTP_EXPIRY_SECONDS = 180

    if request.method == "POST":
        stored_otp = request.session.get('otp')
        otp_created_at = request.session.get('otp_created_at')
        account_number = request.session.get('account_number')

        entered_otp = request.POST.get('entered_otp')
        new_pin = request.POST.get('new_pin')
        confirm_pin = request.POST.get('confirm_pin')

        if not stored_otp or not otp_created_at or not account_number:
            message = "Session expired. Please generate OTP again."
            return render(request, 'validate_otp.html', {'message': message})

        # OTP Expiry check
        if int(time.time()) - otp_created_at > OTP_EXPIRY_SECONDS:
            del request.session['otp']
            del request.session['otp_created_at']
            del request.session['account_number']
            message = "OTP expired. Please generate a new OTP."
            return render(request, 'validate_otp.html', {'message': message})

        if int(stored_otp) != int(entered_otp):
            message = "Invalid OTP"
            return render(request, 'validate_otp.html', {'message': message})

        if new_pin != confirm_pin:
            message = "PIN does not match"
            return render(request, 'validate_otp.html', {'message': message})

        account = BankAccount.objects.get(account_number=account_number)
        account.transaction_pin = hash_pin(new_pin)
        account.save()

        del request.session['otp']
        del request.session['otp_created_at']
        del request.session['account_number']

        return redirect('home')

    return render(request, 'validate_otp.html', {'message': message})


# ---------------- RESEND OTP ----------------
def resend_otp(request):
    account_number = request.session.get('account_number')
    if not account_number:
        return redirect('pin_generation')

    account = BankAccount.objects.get(account_number=account_number)

    otp = random.randint(100000, 999999)
    request.session['otp'] = otp
    request.session['otp_created_at'] = int(time.time())

    send_mail(
        subject="Your FinTrust Bank OTP (Resent)",
        message=f"Your new OTP is {otp}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[account.email],
        fail_silently=True
    )

    return render(request, 'validate_otp.html', {'message': "New OTP sent to your email"})


# ---------------- CHECK BALANCE ----------------
def check_balance(request):
    message = ""
    balance = None

    if request.method == "POST":
        display_account_number = request.POST.get('account_number')
        entered_pin = request.POST.get('transaction_pin')

        if not display_account_number or not display_account_number.startswith("123"):
            message = "Invalid Account Number"
            return render(request, 'check_balance.html', {'message': message})

        try:
            raw_account_number = int(display_account_number[3:])
            account = BankAccount.objects.get(account_number=raw_account_number)
        except:
            message = "Account not found"
            return render(request, 'check_balance.html', {'message': message})

        #PIN Verification
        if not verify_pin(account.transaction_pin, entered_pin.strip()):
            message = "Incorrect PIN"
            return render(request, 'check_balance.html', {'message': message})

        balance = account.account_balance
        request.session['authenticated_account'] = account.account_number


    return render(request, 'check_balance.html', {'message': message, 'balance': balance})


# ---------------- DEPOSIT ----------------
def deposit(request):
    message = ""
    success = ""

    if request.method == "POST":
        display_account_number = request.POST.get('account_number')
        entered_pin = request.POST.get('transaction_pin')
        deposit_amount = request.POST.get('deposit_amount')

        if not display_account_number or not display_account_number.startswith("123"):
            message = "Invalid Account Number"
            return render(request, 'deposit.html', {'message': message})

        try:
            raw_account_number = int(display_account_number[3:])
            account = BankAccount.objects.get(account_number=raw_account_number)
        except:
            message = "Account not found"
            return render(request, 'deposit.html', {'message': message})

        # PIN verification
        if not verify_pin(account.transaction_pin, entered_pin.strip()):
            message = "Incorrect PIN"
            return render(request, 'deposit.html', {'message': message})

        try:
            deposit_amount = Decimal(deposit_amount)
            if deposit_amount <= 0:
                raise ValueError
        except:
            message = "Invalid deposit amount"
            return render(request, 'deposit.html', {'message': message})

        with transaction.atomic():
            account.account_balance += deposit_amount
            account.save()

            Transaction.objects.create(
                account=account,
                transaction_type="DEPOSIT",
                amount=deposit_amount,
                balance_after_transaction=account.account_balance,
                description="Cash deposit"
            )

        success = f"₹{deposit_amount} deposited successfully"

    return render(request, 'deposit.html', {'message': message, 'success': success})

# ---------------- WITHDRAWAL ----------------
def withdrawal(request):
    message = ""
    success = ""

    if request.method == "POST":
        display_account_number = request.POST.get('account_number')
        entered_pin = request.POST.get('transaction_pin')
        withdrawal_amount = request.POST.get('withdrawal_amount')

        if not display_account_number or not display_account_number.startswith("123"):
            message = "Invalid Account Number"
            return render(request, 'withdrawal.html', {'message': message})

        try:
            raw_account_number = int(display_account_number[3:])
            account = BankAccount.objects.get(account_number=raw_account_number)
        except:
            message = "Account not found"
            return render(request, 'withdrawal.html', {'message': message})

        # ✅ PIN verification
        if not verify_pin(account.transaction_pin, entered_pin.strip()):
            message = "Incorrect PIN"
            return render(request, 'withdrawal.html', {'message': message})

        try:
            withdrawal_amount = Decimal(withdrawal_amount)
            if withdrawal_amount <= 0:
                raise ValueError
        except:
            message = "Invalid withdrawal amount"
            return render(request, 'withdrawal.html', {'message': message})

        if withdrawal_amount > account.account_balance:
            message = "Insufficient balance"
            return render(request, 'withdrawal.html', {'message': message})

        with transaction.atomic():
            account.account_balance -= withdrawal_amount
            account.save()

            Transaction.objects.create(
                account=account,
                transaction_type='WITHDRAW',
                amount=withdrawal_amount,
                balance_after_transaction=account.account_balance,
                description="Cash withdrawal"
            )

        success = f"₹{withdrawal_amount} withdrawn successfully. Available balance: ₹{account.account_balance}"

    return render(request, 'withdrawal.html', {'message': message, 'success': success})


# ---------------- ACCOUNT TRANSFER ----------------
def account_transfer(request):
    message = ""
    success = ""

    if request.method == "POST":
        sender_display = request.POST.get('account_number_sender')
        receiver_display = request.POST.get('account_number_reciver')
        entered_pin = request.POST.get('transaction_pin')
        transfer_amount = request.POST.get('transfer_amount')

        if not sender_display or not receiver_display or not sender_display.startswith('123') or not receiver_display.startswith('123'):
            message = "Invalid account number format"
            return render(request, 'account_transfer.html', {'message': message})

        try:
            sender = BankAccount.objects.get(account_number=int(sender_display[3:]))
            receiver = BankAccount.objects.get(account_number=int(receiver_display[3:]))
        except:
            message = "One or both accounts not found"
            return render(request, 'account_transfer.html', {'message': message})

        if sender.account_number == receiver.account_number:
            message = "Cannot transfer to same account"
            return render(request, 'account_transfer.html', {'message': message})

        # PIN CHECK (Sender PIN)
        if not verify_pin(sender.transaction_pin, entered_pin.strip()):
            message = "Incorrect PIN"
            return render(request, 'account_transfer.html', {'message': message})

        try:
            transfer_amount = Decimal(transfer_amount)
            if transfer_amount <= 0:
                raise ValueError
        except:
            message = "Invalid transfer amount"
            return render(request, 'account_transfer.html', {'message': message})

        if transfer_amount > sender.account_balance:
            message = "Insufficient balance"
            return render(request, 'account_transfer.html', {'message': message})

        with transaction.atomic():
            sender.account_balance -= transfer_amount
            receiver.account_balance += transfer_amount
            sender.save()
            receiver.save()

            Transaction.objects.create(
                account=sender,
                transaction_type='TRANSFER_SENT',
                amount=transfer_amount,
                balance_after_transaction=sender.account_balance,
                description=f"Transferred to {receiver.display_account_number()}"
            )

            Transaction.objects.create(
                account=receiver,
                transaction_type='TRANSFER_RECEIVED',
                amount=transfer_amount,
                balance_after_transaction=receiver.account_balance,
                description=f"Received from {sender.display_account_number()}"
            )

        success = f"₹{transfer_amount} transferred successfully. Available balance: ₹{sender.account_balance}"

    return render(request, 'account_transfer.html', {'message': message, 'success': success})

def transaction_history(request):
    message = ""
    transactions = None

    # get logged-in account from session
    account_number = request.session.get('authenticated_account')

    # if user directly opened page
    if not account_number:
        message = "Session expired. Please check balance again."
        return render(request, 'transaction_history.html', {'message': message})

    try:
        account = BankAccount.objects.get(account_number=account_number)
    except BankAccount.DoesNotExist:
        message = "Account not found"
        return render(request, 'transaction_history.html', {'message': message})

    # last 10 transactions
    transactions = Transaction.objects.filter(
        account=account
    ).order_by('-created_at')[:10]

    return render(request, 'transaction_history.html', {
        'transactions': transactions,
        'message': message
    })
