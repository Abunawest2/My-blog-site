from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(read=False).count()
        recent_notifications = request.user.notifications.order_by('-timestamp')[:5]
        return {
            'unread_notification_count': unread_count,
            'recent_notifications': recent_notifications
        }
    return {}
