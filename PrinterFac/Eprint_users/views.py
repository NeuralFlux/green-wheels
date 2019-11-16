import datetime
import os
import random
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
def host_det(request):
    if request.method == 'POST':

        form = HostSearchForm(request.POST)
        if form.is_valid():
            if request.user.profile.aadhar_verified is not True or request.user.profile.license_verified is not True:
                form.add_error('source_point', "Documents not Verified. Please Try again after getting them verified.")
                return render(request, 'Eprint_users/host_det.html', {'form': form})

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

        cust_srch = CustSearch.objects.filter(pk=int(request.POST.get("cust_search_id")), completed=False).first()
        cust_srch.host_accept = True
        cust_srch.save()

        CustSearch.objects.filter(host_accept=False).update(request_to=None)

        return render(request, 'Eprint_users/host_ack.html', {'username': cust_srch.task_by.username})
    else:
        hst_srch = HostSearch.objects.filter(task_by=request.user).order_by('-start_time').first()
        requests_pen = CustSearch.objects.filter(request_to=hst_srch, host_accept=False, completed=False)

    return render(request, 'Eprint_users/host_search.html', {'reqs': requests_pen})


@login_required
def pass_det(request):
    if request.method == 'POST':

        form = CustSearchForm(request.POST)
        if form.is_valid():
            if request.user.profile.aadhar_verified is not True:
                form.add_error('pickup_loc', "Aadhar not Verified. Please Try again after getting it verified.")
                return render(request, 'Eprint_users/pass_det.html', {'form': form})

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
    cust_obj = CustSearch.objects.filter(task_by=request.user).order_by('-start_time').first()
    if request.method == 'POST':
        host = HostSearch.objects.filter(pk=request.POST.get('host_search_id')).first()
        cust_obj = CustSearch.objects.filter(task_by=request.user).order_by('-start_time').first()

        cust_obj.request_to = host
        cust_obj.save()

        return render(request, 'Eprint_users/pass_req.html', {'username': host.task_by.username})
    else:
        hst_searches = HostSearch.objects.all().order_by('-start_time')

    if cust_obj.host_accept is True:
        return redirect('users-trip')

    return render(request, 'Eprint_users/pass_search.html', {'hosts': hst_searches})


@login_required
def trip(request):
    if request.method == "POST":
        if request.POST.get("cust_end_id") is not None:  # Customer Trip Complete
            cust_search = CustSearch.objects.filter(pk=request.POST.get("cust_end_id")).first()

            cust_search.completed = True
            cust_search.save()

            # Calculate Deduction from Account
            money = random.randint(30, 60)
            cust_search.charge = money
            cust_search.save()

            cust_prof = cust_search.task_by.profile
            cust_prof.wallet = float(cust_prof.wallet) - money
            cust_prof.save()

            return render(request, 'Eprint_users/trip_end.html', {'money': money, 'bal': cust_prof.wallet})
        elif request.POST.get("cust_end_id") is None and request.POST.get("host_rating") is None and request.POST.get(
                "cust_rating1") is None:  # Host Trip Complete
            host_search = HostSearch.objects.filter(task_by__pk=request.user.pk).order_by('-start_time').first()

            host_search.completed = True
            host_search.save()

            # Calculate Deduction from Account
            money = random.randint(30, 60)
            host_search.charge = money
            host_search.save()

            host_prof = host_search.task_by.profile
            host_prof.wallet = float(host_prof.wallet) - money
            host_prof.save()

            return render(request, 'Eprint_users/trip_end.html', {'money_host': money, 'bal': host_prof.wallet})
        elif request.POST.get("cust_end_id") is None and request.POST.get("host_rating") is not None:  # Customer Review
            cust_search = CustSearch.objects.filter(task_by__pk=request.user.pk, completed=True).first()
            host = cust_search.request_to.task_by.profile

            cust_search.rating = int(request.POST.get("host_rating"))
            cust_search.save()

            host.rating = (float(host.rating) + int(request.POST.get("host_rating"))) / 2
            host.save()

            return render(request, 'Eprint_users/trip_end.html')
        elif request.POST.get("cust_end_id") is None and request.POST.get("cust_rating1") is not None:  # Host Review
            host_search = HostSearch.objects.filter(task_by__pk=request.user.pk, completed=True).first()
            cust_searches = CustSearch.objects.filter(request_to=host_search, completed=True)
            num_custs = cust_searches.count()

            if num_custs > 1:
                host_search.rating1 = int(request.POST.get("cust_rating1"))
                host_search.save()

                c1 = cust_searches.first().task_by.profile
                c1.rating = (float(c1.rating) + int(request.POST.get("cust_rating1"))) / 2
                c1.save()

                host_search.rating2 = int(request.POST.get("cust_rating2"))
                host_search.save()

                c2 = cust_searches.last().task_by.profile
                c2.rating = (float(c2.rating) + int(request.POST.get("cust_rating2"))) / 2
                c2.save()
            else:
                host_search.rating1 = int(request.POST.get("cust_rating1"))
                host_search.save()

                c1 = cust_searches.first().task_by.profile
                c1.rating = (float(c1.rating) + int(request.POST.get("cust_rating1"))) / 2
                c1.save()
            return render(request, 'Eprint_users/trip_end.html')

    hst_search = HostSearch.objects.filter().order_by('-start_time').first()
    cust_searches = CustSearch.objects.filter(request_to__pk=hst_search.pk, completed=False)

    reln = {}
    reln['host'] = hst_search
    if cust_searches.count() > 0:
        reln['custs'] = cust_searches

    return render(request, 'Eprint_users/trip.html', reln)


@login_required
def trip_hist(request):
    hst_search = HostSearch.objects.filter(task_by=request.user).order_by('-start_time').first()
    cust_search = CustSearch.objects.filter(task_by=request.user).order_by('-start_time').first()

    reln = {}
    if hst_search is not None:
        reln['host'] = hst_search
    if cust_search is not None:
        reln['cust'] = cust_search

    return render(request, 'Eprint_users/trip_history.html', reln)


@login_required
def profile(request):
    prof = Profile.objects.filter(pk=request.user.pk).first()
    return render(request, 'Eprint_users/profile.html', {'profile': prof, 'rating': int(prof.rating * 20)})
