"""college_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib.auth import views as auth_views

from main_app.EditResultView import EditResultView

from . import hod_views, staff_views, student_views, views

urlpatterns = [
    path("", views.login_page, name='login_page'),
    path("get_attendance", views.get_attendance, name='get_attendance'),
    path("firebase-messaging-sw.js", views.showFirebaseJS, name='showFirebaseJS'),
    path("doLogin/", views.doLogin, name='user_login'),
    path("logout_user/", views.logout_user, name='user_logout'),
    path("admin/home/", hod_views.admin_home, name='admin_home'),
    path("staff/add", hod_views.add_staff, name='add_staff'),
    path("course/add", hod_views.add_course, name='add_course'),
    path("send_student_notification/", hod_views.send_student_notification,
         name='send_student_notification'),
    path("send_staff_notification/", hod_views.send_staff_notification,
         name='send_staff_notification'),
    path("add_session/", hod_views.add_session, name='add_session'),
    path("admin_notify_student", hod_views.admin_notify_student,
         name='admin_notify_student'),
    path("admin_notify_staff", hod_views.admin_notify_staff,
         name='admin_notify_staff'),
    path("admin_view_profile", hod_views.admin_view_profile,
         name='admin_view_profile'),
    path("check_email_availability", hod_views.check_email_availability,
         name="check_email_availability"),
    path("session/manage/", hod_views.manage_session, name='manage_session'),
    path("session/edit/<int:session_id>",
         hod_views.edit_session, name='edit_session'),
    path("student/view/feedback/", hod_views.student_feedback_message,
         name="student_feedback_message",),
    path("staff/view/feedback/", hod_views.staff_feedback_message,
         name="staff_feedback_message",),
    path("student/view/leave/", hod_views.view_student_leave,
         name="view_student_leave",),
    path("staff/view/leave/", hod_views.view_staff_leave, name="view_staff_leave",),
    path("attendance/view/", hod_views.admin_view_attendance,
         name="admin_view_attendance",),
    path("attendance/fetch/", hod_views.get_admin_attendance,
         name='get_admin_attendance'),
    path("student/add/", hod_views.add_student, name='add_student'),
    path("subject/add/", hod_views.add_subject, name='add_subject'),
    path("staff/manage/", hod_views.manage_staff, name='manage_staff'),
    path("student/manage/", hod_views.manage_student, name='manage_student'),
    path("student/import/", hod_views.import_students, name='import_students'),
    path("course/manage/", hod_views.manage_course, name='manage_course'),
    path("subject/manage/", hod_views.manage_subject, name='manage_subject'),
    path("staff/edit/<int:staff_id>", hod_views.edit_staff, name='edit_staff'),
    path("staff/delete/<int:staff_id>",
         hod_views.delete_staff, name='delete_staff'),

    path("course/delete/<int:course_id>",
         hod_views.delete_course, name='delete_course'),

    path("subject/delete/<int:subject_id>",
         hod_views.delete_subject, name='delete_subject'),

    path("session/delete/<int:session_id>",
         hod_views.delete_session, name='delete_session'),

    path("student/delete/<int:student_id>",
         hod_views.delete_student, name='delete_student'),
    path("student/edit/<int:student_id>",
         hod_views.edit_student, name='edit_student'),
    path("course/edit/<int:course_id>",
         hod_views.edit_course, name='edit_course'),
    path("subject/edit/<int:subject_id>",
         hod_views.edit_subject, name='edit_subject'),

    # Staff URL patterns
    path('staff_home', staff_views.staff_home, name='staff_home'),
    path('staff_take_attendance', staff_views.staff_take_attendance, name='staff_take_attendance'),
    path('get_students', staff_views.get_students, name='get_students'),
    path('save_attendance', staff_views.save_attendance, name='save_attendance'),
    path('staff_update_attendance', staff_views.staff_update_attendance, name='staff_update_attendance'),
    path('get_student_attendance', staff_views.get_student_attendance, name='get_student_attendance'),
    path('update_attendance', staff_views.update_attendance, name='update_attendance'),
    path('staff_apply_leave', staff_views.staff_apply_leave, name='staff_apply_leave'),
    path('staff_feedback', staff_views.staff_feedback, name='staff_feedback'),
    path('staff_view_profile', staff_views.staff_view_profile, name='staff_view_profile'),
    path('staff_fcmtoken', staff_views.staff_fcmtoken, name='staff_fcmtoken'),
    path('staff_view_notification', staff_views.staff_view_notification, name='staff_view_notification'),
    path('staff_add_result', staff_views.staff_add_result, name='staff_add_result'),
    path('staff_add_assignment', staff_views.staff_add_assignment, name='staff_add_assignment'),
    path('staff_add_note', staff_views.staff_add_note, name='staff_add_note'),
    path('staff_delete_assignment/<int:assignment_id>', staff_views.staff_delete_assignment, name='staff_delete_assignment'),
    path('staff_delete_note/<int:note_id>', staff_views.staff_delete_note, name='staff_delete_note'),

    # Student URL patterns
    path('student_home', student_views.student_home, name='student_home'),
    path('student_view_attendance', student_views.student_view_attendance, name='student_view_attendance'),
    path('student_apply_leave', student_views.student_apply_leave, name='student_apply_leave'),
    path('student_feedback', student_views.student_feedback, name='student_feedback'),
    path('student_view_profile', student_views.student_view_profile, name='student_view_profile'),
    path('student_fcmtoken', student_views.student_fcmtoken, name='student_fcmtoken'),
    path('student_view_notification', student_views.student_view_notification, name='student_view_notification'),
    path('student_view_result', student_views.student_view_result, name='student_view_result'),
    path('student_view_assignments', student_views.student_view_assignments, name='student_view_assignments'),
    path('student_view_notes', student_views.student_view_notes, name='student_view_notes'),
    path('student_view_fees', student_views.student_view_fees, name='student_view_fees'),
    path('student_fee_payments', student_views.student_fee_payments, name='student_fee_payments'),
    path('initiate_payment/<int:fee_id>', student_views.initiate_payment, name='initiate_payment'),
    path('payment_callback', student_views.payment_callback, name='payment_callback'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path("group_student_notification/", hod_views.group_student_notification, name="group_student_notification"),
    path("group_staff_notification/", hod_views.group_staff_notification, name="group_staff_notification"),
    path('student/notification/delete/<int:notification_id>/', views.delete_student_notification, name='delete_student_notification'),
    path('staff/notification/delete/<int:notification_id>/', views.delete_staff_notification, name='delete_staff_notification'),

    # Fee Management URLs
    path('manage-fee-categories/', hod_views.manage_fee_categories, name='manage_fee_categories'),
    path('add-fee-category/', hod_views.add_fee_category, name='add_fee_category'),
    path('manage-fees/', hod_views.manage_fees, name='manage_fees'),
    path('add-fee/', hod_views.add_fee, name='add_fee'),
    path('edit-fee/<int:fee_id>/', hod_views.edit_fee, name='edit_fee'),
    path('delete-fee/<int:fee_id>/', hod_views.delete_fee, name='delete_fee'),
    path('manage-fee-payments/', hod_views.manage_fee_payments, name='manage_fee_payments'),
    path('add-fee-payment/', hod_views.add_fee_payment, name='add_fee_payment'),
    path('view-fee-payment/<int:payment_id>/', hod_views.view_fee_payment, name='view_fee_payment'),
    path('print-fee-receipt/<int:payment_id>/', hod_views.print_fee_receipt, name='print_fee_receipt'),
]
