import datetime
import os
import smtplib
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ProfileForm, CustSearchForm, HostSearchForm
from .models import Profile, HostSearch, CustSearch
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from Eprint_admin.models import RatePerPage
from django.conf import settings
from django.utils import timezone

# Media Upload Server
media_upload_url = settings.EASY_PRINT_MEDIA_UPLOAD_URL
media_delete_url = "http://localhost:80/EP_delete_post.php"


# @background(schedule=10)
# def clean_stored_media(user_id):
#     print(f"Enter Clean {user_id}")
#     user = User.objects.get(pk=user_id)
#     now = timezone.now()
#     print_docs = PrintDocs.objects.filter(task_by=user, date_uploaded__lte=now - datetime.timedelta(days=6),
#                                           completed=True)
#     # Remove physical files
#     for doc in print_docs:
#         file_path = doc.document.name
#         file_name = str(file_path).replace('media/documents/', '')
#         # Remove from django storage
#         if os.path.isfile(file_path):
#             print(f"deleting: {file_path}")
#             os.remove(file_path)
#         # Remove from content delivery network[Apache Server]
#         print(f"php: {file_name}")
#         request_sender = requests.post(media_delete_url,
#                                        data={'safe_url': user.profile.hash_url.hex, 'fileToDelete': file_name})
#         if request_sender.status_code != 200:
#             print(f'Error deleting {file_name}')
#     # Not deleting from Database as permanent record needs to be maintained.
#
#
# @background(schedule=20)
# def mark_completed(user_id):
#     print("Enter Background mark")
#     run_queue = subprocess.run(["lpq"], encoding='utf-8', stdout=subprocess.PIPE)
#     output = run_queue.stdout
#
#     # Update the objects which aren't completed(to be marked as completed) and not in the print queue
#     s = [line.split() for line in output.split('\n')]
#     s = s[2:]
#     pending = []
#
#     for row in s:
#         try:
#             if len(row) >= 4 and int(row[1]) == user_id:
#                 pending.append(int(row[3]))
#         except ValueError:  # Someone else printed, hence row[3] may have a string of the user and we should ignore it
#             pass
#
#     user = User.objects.get(pk=user_id)
#     qset = PrintDocs.objects.filter(task_by=user, completed=False).exclude(id__in=pending)
#     doc_names = [doc.file_name for doc in qset]
#     # Print documents updated in log
#     print(doc_names)
#     # Update documents in database
#     PrintDocs.objects.filter(task_by=user, completed=False).exclude(id__in=pending).update(completed=True)
#     # Send email notification to user if document printed.
#     doc_names_str = ', '.join(doc_names)
#     if len(doc_names) > 0:
#         notify_user(user_id, doc_names_str)
#
#
# def notify_user(user_id, doc_names):
#     # Mark printed docs as completed
#     mark_completed(user_id)
#
#     user = User.objects.get(pk=user_id)
#     print('Notification, HERE I COME!!!')
#     print(user.email)
#     print(user)
#     mail_subject = 'EasyPrint: Document Printed Successfully'
#     body = 'Dear {}, \nYour document(s):{} has been printed and is ready for collection. Please collect it' \
#            ' from the Printer Room, Library, IIT Dharwad.' \
#            'Thank You for using EasyPrint services. \nEasyPrint, IIT Dharwad'.format(user.username, doc_names)
#     to_email = user.email
#     server = smtplib.SMTP_SSL("smtp.googlemail.com", 465)
#     server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
#     final_email = 'Subject: {} \n{}'.format(mail_subject, body)
#     server.sendmail(settings.EMAIL_HOST_USER, to_email, final_email)
#     print('Sent Notif')


def register(request):
    if request.user.is_authenticated:  # If user is logged in
        return redirect('baseApp-home')
    else:
        if request.method == 'POST':
            user_form = UserRegisterForm(request.POST)  # Populate form with instance submitted by user
            profile_form = ProfileForm()

            if user_form.is_valid():
                user = user_form.save(commit=False)

                user.is_active = False
                user.save()

                # Send account activation link to email
                current_site = get_current_site(request)
                body = render_to_string('Eprint_users/acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    'token': account_activation_token.make_token(user),
                })

                mail_subject = 'Activate your EasyPrint account.'
                to_email = user_form.cleaned_data.get('email')
                server = smtplib.SMTP_SSL("smtp.googlemail.com", 465)
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                final_email = 'Subject: {}{}'.format(mail_subject, body)
                server.sendmail(settings.EMAIL_HOST_USER, to_email, final_email)

                return render(request, 'ground/check_ack.html', {'activate': True})
        else:
            user_form = UserRegisterForm()
            profile_form = ProfileForm()

        return render(request, 'Eprint_users/register.html', {'user_form': user_form, 'profile_form': profile_form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # delete test
        # Launch Background to check if docs printed
        if check_faculty(user.email):
            user.profile.is_faculty = True
            user.profile.save()

        return render(request, 'ground/check_ack.html', {'valid_registration': True})
    else:
        return render(request, 'ground/check_ack.html', {'valid_registration': False})


# @login_required
# def collected(request):
#     if request.method == 'GET' and request.GET.get('confirm_doc') is not None:
#         doc = PrintDocs.objects.filter(pk=request.GET.get('confirm_doc')).first()
#         if doc.task_by.pk == request.user.pk:
#             if request.GET.get('confirm') is not None:
#                 PrintDocs.objects.filter(pk=doc.pk).update(collected=True)
#                 return redirect('users-history')
#             return render(request, 'Eprint_users/confirm_collected.html', {'doc_id': doc.pk})
#         else:
#             redirect('users-history')
#     return redirect('users-history')


@login_required
def pass_det(request):
    if request.method == 'POST':

        form = CustSearchForm(request.POST)
        if form.is_valid():
            ### GreenWheels
            data = form.save(commit=False)
            data.task_by = request.user

            data.save()
        return redirect('users-pass-search')

    else:
        form = CustSearchForm()

    return render(request, 'Eprint_users/pass_det.html', {'form': form})


@login_required
def pass_search(request):
    if request.method == 'POST':
        host = HostSearch.objects.filter(pk=request.POST.get('host_search_id')).first()
        cust_obj = CustSearch.objects.filter(task_by=request.user).order_by('-start_time').first()

        cust_obj.request_to = host
        cust_obj.save()

        return render(request, 'Eprint_users/pass_req.html', {'username': host.task_by.username})
    else:
        hst_searches = HostSearch.objects.all().order_by('-start_time')

    if CustSearch.objects.filter(task_by=request.user).order_by('-start_time').first().host_accept is True:
        # Start Trip
        pass

    return render(request, 'Eprint_users/pass_search.html', {'hosts': hst_searches})


@login_required
def profile(request):
    profile_form = ProfileForm(instance=request.user.profile)
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()

    return render(request, 'Eprint_users/profile.html', {'form': profile_form})


# @csrf_exempt
# def bill(request):
#     if request.method == 'POST':
#
#         username = request.POST.get('hidden')
#         unpaid = PrintDocs.objects.filter(task_by__username=username, completed=True, paid=False, is_confirmed=True)
#         amount_due = str(int(sum([i.price for i in unpaid]) * 100))
#
#         client = razorpay.Client(auth=(settings.API_KEY, settings.API_PASS))
#         client.set_app_details({"title": "PrinterFac", "version": "2.0"})
#
#         payment_id = request.POST.get("razorpay_payment_id")
#         client.payment.capture(payment_id, amount_due)
#         unpaid.update(paid=True)
#
#         return redirect('users-bill')
#
#     else:
#         unpaid = request.user.printdocs_set.filter(completed=True, paid=False, is_confirmed=True)
#         amount_due = int(sum([i.price for i in unpaid]) * 100)
#
#         return render(request, 'Eprint_users/bill.html',
#                       {'not_paid_tasks': unpaid, 'total_due': amount_due, 'total_due_rupee': amount_due / 100,
#                        'dict_username': request.user.username, 'api_key': settings.API_KEY})
#

@login_required
def host_det(request):
    if request.method == 'POST':

        form = HostSearchForm(request.POST)
        if form.is_valid():

            ### GreenWheels
            data = form.save(commit=False)
            data.task_by = request.user

            data.save()
        return redirect('users-host-search')

    else:
        form = HostSearchForm()

    return render(request, 'Eprint_users/host_det.html', {'form': form})


@login_required
def host_search(request):
    if request.method == 'POST':
        # Set the intended CustSearch object to true

        cust_srch = CustSearch.objects.filter(pk=int(request.POST.get("cust_search_id"))).first()
        cust_srch.host_accept = True
        cust_srch.save()

        CustSearch.objects.filter(host_accept=False).update(request_to=None)

        return render(request, 'Eprint_users/host_ack.html', {'username': cust_srch.task_by.username})
    else:
        hst_srch = HostSearch.objects.filter(task_by=request.user).order_by('-start_time').first()
        requests_pen = CustSearch.objects.filter(request_to=hst_srch)
        print("Cpming INn hot")

    return render(request, 'Eprint_users/host_search.html', {'reqs': requests_pen})


def check_faculty(email):
    try:
        int(email.split('@')[0])
    except ValueError:
        return True
    return False
