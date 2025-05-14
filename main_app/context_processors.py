from .models import NotificationStudent, NotificationStaff

def notification_count(request):
    count = 0
    if request.user.is_authenticated:
        if hasattr(request.user, 'student'):
            count = NotificationStudent.objects.filter(student=request.user.student, read=False).count()
        elif hasattr(request.user, 'staff'):
            count = NotificationStaff.objects.filter(staff=request.user.staff, read=False).count()
    return {'notification_count': count}
