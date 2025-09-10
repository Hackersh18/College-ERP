import json
from datetime import datetime, timedelta
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum, Q
from django.utils import timezone

from .forms import *
from .models import *
import os
import requests
import re


def counsellor_home(request):
    """Counsellor Dashboard"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    
    # My Leads Statistics
    my_leads = Lead.objects.filter(assigned_counsellor=counsellor)
    total_leads = my_leads.count()
    new_leads = my_leads.filter(status='NEW').count()
    contacted_leads = my_leads.filter(status='CONTACTED').count()
    qualified_leads = my_leads.filter(status='QUALIFIED').count()
    closed_won = my_leads.filter(status='CLOSED_WON').count()
    
    # My Business Statistics
    my_businesses = Business.objects.filter(counsellor=counsellor)
    total_business_value = my_businesses.filter(status='ACTIVE').aggregate(
        total=Sum('value'))['total'] or 0
    pending_businesses = my_businesses.filter(status='PENDING').count()
    active_businesses = my_businesses.filter(status='ACTIVE').count()
    
    # Recent Activities
    recent_activities = LeadActivity.objects.filter(
        counsellor=counsellor
    ).select_related('lead').order_by('-completed_date')[:10]
    
    # Upcoming Follow-ups
    upcoming_followups = Lead.objects.filter(
        assigned_counsellor=counsellor,
        next_follow_up__isnull=False,
        next_follow_up__gte=timezone.now()
    ).order_by('next_follow_up')[:5]
    
    # Lead Status Distribution for Charts
    lead_status_data = {
        'NEW': new_leads,
        'CONTACTED': contacted_leads,
        'QUALIFIED': qualified_leads,
        'CLOSED_WON': closed_won,
    }
    
    # Monthly Performance
    current_month = timezone.now().replace(day=1)
    monthly_leads = my_leads.filter(created_at__gte=current_month).count()
    monthly_business = my_businesses.filter(
        created_at__gte=current_month, status='ACTIVE'
    ).aggregate(total=Sum('value'))['total'] or 0
    
    context = {
        'page_title': "Counsellor Dashboard",
        'counsellor': counsellor,
        'total_leads': total_leads,
        'new_leads': new_leads,
        'contacted_leads': contacted_leads,
        'qualified_leads': qualified_leads,
        'closed_won': closed_won,
        'total_business_value': total_business_value,
        'pending_businesses': pending_businesses,
        'active_businesses': active_businesses,
        'recent_activities': recent_activities,
        'upcoming_followups': upcoming_followups,
        'lead_status_data': lead_status_data,
        'monthly_leads': monthly_leads,
        'monthly_business': monthly_business,
    }
    return render(request, 'counsellor_template/home_content.html', context)


def my_leads(request):
    """View assigned leads"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    leads = Lead.objects.filter(assigned_counsellor=counsellor).select_related('source')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        leads = leads.filter(status=status_filter)
    
    context = {
        'leads': leads,
        'page_title': 'My Leads'
    }
    return render(request, 'counsellor_template/my_leads.html', context)


def lead_detail(request, lead_id):
    """View lead details and activities"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    lead = get_object_or_404(Lead, id=lead_id, assigned_counsellor=counsellor)
    activities = LeadActivity.objects.filter(lead=lead, counsellor=counsellor).order_by('-completed_date')
    
    context = {
        'lead': lead,
        'activities': activities,
        'page_title': f'Lead: {lead.first_name} {lead.last_name}'
    }
    return render(request, 'counsellor_template/lead_detail.html', context)


def add_lead_activity(request, lead_id):
    """Add activity for a lead"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    lead = get_object_or_404(Lead, id=lead_id, assigned_counsellor=counsellor)
    form = LeadActivityForm(request.POST or None)
    
    context = {
        'form': form,
        'lead': lead,
        'page_title': 'Add Activity'
    }
    
    if request.method == 'POST':
        if form.is_valid():
            try:
                activity = form.save(commit=False)
                activity.lead = lead
                activity.counsellor = counsellor
                activity.save()
                
                # Update lead status and last contact date
                lead.last_contact_date = timezone.now()
                lead.save()
                
                messages.success(request, "Activity added successfully!")
                return redirect(reverse('lead_detail', kwargs={'lead_id': lead_id}))
            except Exception as e:
                messages.error(request, f"Could not add activity: {str(e)}")
        else:
            messages.error(request, "Please fill the form properly!")
    
    return render(request, 'counsellor_template/add_lead_activity.html', context)


def update_lead_status(request, lead_id):
    """Update lead status"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    lead = get_object_or_404(Lead, id=lead_id, assigned_counsellor=counsellor)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Lead.LEAD_STATUS):
            lead.status = new_status
            lead.save()
            messages.success(request, f"Lead status updated to {new_status}")
        else:
            messages.error(request, "Invalid status")
    
    return redirect(reverse('lead_detail', kwargs={'lead_id': lead_id}))


def create_business(request, lead_id):
    """Create business from lead"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    lead = get_object_or_404(Lead, id=lead_id, assigned_counsellor=counsellor)
    form = BusinessForm(request.POST or None)
    
    context = {
        'form': form,
        'lead': lead,
        'page_title': 'Create Business'
    }
    
    if request.method == 'POST':
        if form.is_valid():
            try:
                business = form.save(commit=False)
                business.lead = lead
                business.counsellor = counsellor
                business.save()
                
                # Update lead status to CLOSED_WON
                lead.status = 'CLOSED_WON'
                lead.actual_value = business.value
                lead.save()
                
                messages.success(request, f"Business created successfully! Business ID: {business.business_id}")
                return redirect(reverse('my_businesses'))
            except Exception as e:
                messages.error(request, f"Could not create business: {str(e)}")
        else:
            messages.error(request, "Please fill the form properly!")
    
    return render(request, 'counsellor_template/create_business.html', context)


def my_businesses(request):
    """View my businesses"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    businesses = Business.objects.filter(counsellor=counsellor).select_related('lead')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        businesses = businesses.filter(status=status_filter)
    
    context = {
        'businesses': businesses,
        'page_title': 'My Businesses'
    }
    return render(request, 'counsellor_template/my_businesses.html', context)


def business_detail(request, business_id):
    """View business details"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    business = get_object_or_404(Business, id=business_id, counsellor=counsellor)
    
    context = {
        'business': business,
        'page_title': f'Business: {business.title}'
    }
    return render(request, 'counsellor_template/business_detail.html', context)


def update_business_status(request, business_id):
    """Update business status"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    business = get_object_or_404(Business, id=business_id, counsellor=counsellor)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Business.BUSINESS_STATUS):
            business.status = new_status
            business.save()
            messages.success(request, f"Business status updated to {new_status}")
        else:
            messages.error(request, "Invalid status")
    
    return redirect(reverse('business_detail', kwargs={'business_id': business_id}))


def request_lead_transfer(request, lead_id):
    """Request lead transfer to another counsellor"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    lead = get_object_or_404(Lead, id=lead_id, assigned_counsellor=counsellor)
    form = LeadTransferForm(request.POST or None)
    
    context = {
        'form': form,
        'lead': lead,
        'page_title': 'Request Lead Transfer'
    }
    
    if request.method == 'POST':
        if form.is_valid():
            try:
                transfer = form.save(commit=False)
                transfer.lead = lead
                transfer.from_counsellor = counsellor
                transfer.save()
                
                messages.success(request, "Transfer request submitted successfully!")
                return redirect(reverse('my_leads'))
            except Exception as e:
                messages.error(request, f"Could not submit transfer request: {str(e)}")
        else:
            messages.error(request, "Please fill the form properly!")
    
    return render(request, 'counsellor_template/request_lead_transfer.html', context)


def my_activities(request):
    """View my activities"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    activities = LeadActivity.objects.filter(counsellor=counsellor).select_related('lead').order_by('-completed_date')
    
    # Filter by activity type if provided
    activity_type = request.GET.get('activity_type')
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    
    context = {
        'activities': activities,
        'page_title': 'My Activities'
    }
    return render(request, 'counsellor_template/my_activities.html', context)


def counsellor_view_profile(request):
    """Counsellor profile view"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    
    # Performance statistics
    total_leads = counsellor.lead_set.count()
    total_business = counsellor.business_set.filter(status='ACTIVE').aggregate(
        total=Sum('value'))['total'] or 0
    try:
        conversion_rate = (counsellor.business_set.count() / total_leads * 100) if total_leads > 0 else 0
    except ZeroDivisionError:
        conversion_rate = 0
    
    context = {
        'counsellor': counsellor,
        'total_leads': total_leads,
        'total_business': total_business,
        'conversion_rate': conversion_rate,
        'page_title': 'My Profile'
    }
    return render(request, 'counsellor_template/counsellor_view_profile.html', context)


def counsellor_view_notifications(request):
    """View counsellor notifications"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    notifications = NotificationCounsellor.objects.filter(counsellor=counsellor).order_by('-created_at')
    
    # Mark notifications as read
    if request.method == 'POST':
        notifications.update(is_read=True)
        messages.success(request, "All notifications marked as read!")
    
    context = {
        'notifications': notifications,
        'page_title': 'Notifications'
    }
    return render(request, 'counsellor_template/counsellor_view_notifications.html', context)


def counsellor_fcmtoken(request):
    """Update FCM token for notifications"""
    if request.method == 'POST':
        token = request.POST.get('token')
        if token:
            request.user.fcm_token = token
            request.user.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


def get_my_analytics(request):
    """AJAX endpoint for counsellor analytics"""
    if request.method == 'GET':
        try:
            counsellor = get_object_or_404(Counsellor, admin=request.user)
            
            # Lead status distribution
            status_data = counsellor.lead_set.values('status').annotate(
                count=Count('id')
            ).values('status', 'count')
            
            # Monthly activity trend
            current_month = timezone.now().replace(day=1)
            monthly_activities = []
            for i in range(6):
                month_start = current_month - timedelta(days=30*i)
                month_end = month_start + timedelta(days=30)
                month_activities = counsellor.leadactivity_set.filter(
                    completed_date__gte=month_start,
                    completed_date__lt=month_end
                ).count()
                monthly_activities.append({
                    'month': month_start.strftime('%B'),
                    'activities': month_activities
                })
            
            return JsonResponse({
                'status_data': list(status_data),
                'monthly_activities': monthly_activities
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def schedule_follow_up(request, lead_id):
    """Schedule follow-up for a lead"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    lead = get_object_or_404(Lead, id=lead_id, assigned_counsellor=counsellor)
    
    if request.method == 'POST':
        follow_up_date = request.POST.get('follow_up_date')
        if follow_up_date:
            try:
                lead.next_follow_up = datetime.fromisoformat(follow_up_date.replace('Z', '+00:00'))
                lead.save()
                messages.success(request, "Follow-up scheduled successfully!")
            except Exception as e:
                messages.error(request, f"Could not schedule follow-up: {str(e)}")
        else:
            messages.error(request, "Please provide a valid date")
    
    return redirect(reverse('lead_detail', kwargs={'lead_id': lead_id}))


def evaluate_conversion_score(request, lead_id):
    """Call AI API to assign a conversion score (0-100) based on lead description/notes."""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    lead = get_object_or_404(Lead, id=lead_id, assigned_counsellor=counsellor)

    # Build input text for the model
    description_parts = [
        f"Name: {lead.first_name} {lead.last_name}",
        f"Company: {lead.company or '-'}",
        f"Position: {lead.position or '-'}",
        f"Industry: {lead.industry or '-'}",
        f"Status: {lead.status}",
        f"Priority: {lead.priority}",
        f"Expected Value: {lead.expected_value}",
        f"Notes: {lead.notes or '-'}",
    ]
    prompt = "\n".join(description_parts) + "\n\nReturn ONLY an integer from 0 to 100 representing the conversion probability."

    score = None
    error_message = None

    try:
        openai_key = os.environ.get('OPENAI_API_KEY')
        if openai_key:
            # Simple call to OpenAI's responses API (fallback to a basic prompt-completion style)
            headers = {
                'Authorization': f'Bearer {openai_key}',
                'Content-Type': 'application/json'
            }
            body = {
                'model': 'gpt-4o-mini',
                'input': f"You are a scoring function. Read the lead details and output ONLY an integer 0-100.\n\n{prompt}"
            }
            resp = requests.post('https://api.openai.com/v1/responses', headers=headers, json=body, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                text = (data.get('output_text') or '').strip()
                # Extract first integer 0-100
                import re
                m = re.search(r"\b(100|\d{1,2})\b", text)
                if m:
                    score = int(m.group(1))
        
        # Fallback heuristic if no key or failed to parse
        if score is None:
            # Simple heuristic: base on priority and status
            base = {
                'NEW': 30,
                'CONTACTED': 45,
                'QUALIFIED': 60,
                'PROPOSAL_SENT': 70,
                'NEGOTIATION': 80,
                'CLOSED_WON': 95,
                'CLOSED_LOST': 5,
                'TRANSFERRED': 40,
            }.get(lead.status, 40)
            priority_bonus = {
                'LOW': -5,
                'MEDIUM': 0,
                'HIGH': 5,
                'URGENT': 10,
            }.get(lead.priority, 0)
            score = max(0, min(100, base + priority_bonus))
    except Exception as e:
        error_message = str(e)

    if score is not None:
        lead.conversion_score = score
        lead.save()
        messages.success(request, f"Conversion score updated: {score}")
    else:
        messages.error(request, f"Could not evaluate score: {error_message or 'Unknown error'}")

    return redirect(reverse('lead_detail', kwargs={'lead_id': lead_id}))


def run_agentic_workflow(request, lead_id):
    """Agentic AI workflow: enrich → score → route (with reasoning)."""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    lead = get_object_or_404(Lead, id=lead_id, assigned_counsellor=counsellor)

    openai_key = os.environ.get('OPENAI_API_KEY')
    headers = {'Authorization': f'Bearer {openai_key}', 'Content-Type': 'application/json'} if openai_key else None

    # Agent 1: Enrich lead info (mock LinkedIn title via AI based on notes/company/position)
    try:
        enrichment_prompt = (
            "You are a data enricher. Given lead data, infer a likely LinkedIn-style job title.\n"
            "Return JSON with keys: job_title, notes. Keep it brief.\n\n"
            f"Company: {lead.company or '-'}\n"
            f"Existing Position: {lead.position or '-'}\n"
            f"Industry: {lead.industry or '-'}\n"
            f"Notes: {lead.notes or '-'}\n"
        )
        job_title = None
        enrichment_notes = None
        if headers:
            body = {'model': 'gpt-4o-mini', 'input': enrichment_prompt}
            r = requests.post('https://api.openai.com/v1/responses', headers=headers, json=body, timeout=20)
            if r.status_code == 200:
                txt = (r.json().get('output_text') or '').strip()
                m = re.search(r'job_title\s*[:\"]\s*([^\n\"]+)', txt, re.I)
                n = re.search(r'notes\s*[:\"]\s*([^\n]+)', txt, re.I)
                if m:
                    job_title = m.group(1).strip()[:150]
                if n:
                    enrichment_notes = n.group(1).strip()
        if not job_title:
            # Heuristic fallback
            job_title = lead.position or ('Head of ' + lead.industry if lead.industry else 'Decision Maker')
        if not enrichment_notes:
            enrichment_notes = 'Enriched via heuristic based on existing fields.'
        lead.enriched_job_title = job_title
        lead.enrichment_notes = enrichment_notes
        lead.save()
    except Exception as e:
        messages.warning(request, f"Enrichment failed; using fallback. {str(e)}")

    # Agent 2: Score lead (reuse evaluate logic)
    try:
        description_parts = [
            f"Company: {lead.company or '-'}",
            f"Position: {lead.position or '-'} | Enriched: {lead.enriched_job_title or '-'}",
            f"Industry: {lead.industry or '-'}",
            f"Status: {lead.status}",
            f"Priority: {lead.priority}",
            f"Expected Value: {lead.expected_value}",
            f"Notes: {lead.notes or '-'}",
        ]
        prompt = "\n".join(description_parts) + "\n\nReturn ONLY an integer 0-100 for conversion likelihood."
        score = None
        if headers:
            body = {'model': 'gpt-4o-mini', 'input': f"{prompt}"}
            r = requests.post('https://api.openai.com/v1/responses', headers=headers, json=body, timeout=20)
            if r.status_code == 200:
                txt = (r.json().get('output_text') or '').strip()
                m = re.search(r"\b(100|\d{1,2})\b", txt)
                if m:
                    score = int(m.group(1))
        if score is None:
            base = {
                'NEW': 30, 'CONTACTED': 45, 'QUALIFIED': 60,
                'PROPOSAL_SENT': 70, 'NEGOTIATION': 80,
                'CLOSED_WON': 95, 'CLOSED_LOST': 5, 'TRANSFERRED': 40,
            }.get(lead.status, 40)
            priority_bonus = {'LOW': -5, 'MEDIUM': 0, 'HIGH': 5, 'URGENT': 10}.get(lead.priority, 0)
            score = max(0, min(100, base + priority_bonus))
        lead.conversion_score = score
        lead.save()
    except Exception as e:
        messages.warning(request, f"Scoring failed; used fallback. {str(e)}")

    # Agent 3: Route lead with reasoning
    try:
        route_prompt = (
            "You are a sales router. Decide assignment path and explain briefly.\n"
            "Options: junior_sales, mid_sales, senior_sales, enterprise_team.\n"
            "Respond as: route=<option>\nreason=<one line>.\n\n"
            f"Score: {lead.conversion_score}\n"
            f"Expected Value: {lead.expected_value}\n"
            f"Job Title: {lead.enriched_job_title or lead.position or '-'}\n"
            f"Industry: {lead.industry or '-'}\n"
        )
        routed_to = None
        routing_reason = None
        if headers:
            body = {'model': 'gpt-4o-mini', 'input': route_prompt}
            r = requests.post('https://api.openai.com/v1/responses', headers=headers, json=body, timeout=20)
            if r.status_code == 200:
                txt = (r.json().get('output_text') or '').lower()
                m = re.search(r'route\s*=\s*(junior_sales|mid_sales|senior_sales|enterprise_team)', txt)
                n = re.search(r'reason\s*=\s*(.+)', txt)
                if m:
                    routed_to = m.group(1)
                if n:
                    routing_reason = n.group(1).strip()
        if not routed_to:
            # Heuristic: high value or score → senior/enterprise
            value = float(lead.expected_value or 0)
            score = lead.conversion_score or 0
            if value >= 500000 or score >= 80:
                routed_to = 'senior_sales'
            elif value >= 200000 or score >= 60:
                routed_to = 'mid_sales'
            else:
                routed_to = 'junior_sales'
        if not routing_reason:
            routing_reason = f"Assigned to {routed_to.replace('_', ' ')} based on score {lead.conversion_score} and value {lead.expected_value}."
        lead.routed_to = routed_to
        lead.routing_reason = routing_reason[:1000]
        lead.save()
        messages.success(request, f"Workflow complete. Routed to {routed_to.replace('_',' ')}.")
    except Exception as e:
        messages.error(request, f"Routing failed: {str(e)}")

    return redirect(reverse('lead_detail', kwargs={'lead_id': lead_id}))


def mark_lead_lost(request, lead_id):
    """Mark lead as lost"""
    counsellor = get_object_or_404(Counsellor, admin=request.user)
    lead = get_object_or_404(Lead, id=lead_id, assigned_counsellor=counsellor)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        lead.status = 'CLOSED_LOST'
        lead.notes += f"\n\nLost Reason: {reason}"
        lead.save()
        messages.success(request, "Lead marked as lost")
    
    return redirect(reverse('lead_detail', kwargs={'lead_id': lead_id}))
