from .models import Notification
from users.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from billing.tasks import check_unpaid_bills
from celery import shared_task

# Create your views here.
def create_message(user_ids, body):
    try:
        users = User.objects.filter(id__in=user_ids)
        for user in users:
            Notification.objects.create(
                user=user,
                body=body,
                created_at=timezone.now(),
                read_at=None
            )
    except Exception as e:
        print(f"An error occurred: {e}")
        
 
@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user, read_at__isnull=True)
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, user=request.user, id=notification_id)
    notification.read_at = timezone.now()
    notification.save()
    return redirect('notifications:notification_list')


@shared_task
def bill_notification():
    users = User.objects.all()
    try:
        for user in users:
            unpaid_bills_exists = check_unpaid_bills(user.id)
            if unpaid_bills_exists:
                Notification.object.create(
                    user=user,
                    body='You have unpaid bills, pls check and pay before to due date to avoid any penalties',
                    created_at=timezone.now(),
                    read_at=None
                )
    except Exception as e:
        return f"error: {e}"