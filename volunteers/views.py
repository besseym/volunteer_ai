import csv
import json
from io import BytesIO
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import Category, VolunteerOpportunity, Volunteer
from .forms import VolunteerOpportunityForm, VolunteerForm, OpportunityFilterForm


def dashboard(request):
    """Dashboard view with summary statistics."""
    today = timezone.now().date()

    # Get statistics
    total_opportunities = VolunteerOpportunity.objects.count()
    upcoming_opportunities = VolunteerOpportunity.objects.filter(date__gte=today).count()
    total_volunteers = Volunteer.objects.count()

    # Get category breakdown
    categories = Category.objects.annotate(
        opportunity_count=Count('opportunities'),
        volunteer_count=Count('opportunities__volunteers')
    )

    # Recent opportunities
    recent_opportunities = VolunteerOpportunity.objects.filter(
        date__gte=today
    ).select_related('category').prefetch_related('volunteers')[:5]

    # Recent signups
    recent_volunteers = Volunteer.objects.select_related(
        'opportunity', 'opportunity__category'
    )[:5]

    context = {
        'total_opportunities': total_opportunities,
        'upcoming_opportunities': upcoming_opportunities,
        'total_volunteers': total_volunteers,
        'categories': categories,
        'recent_opportunities': recent_opportunities,
        'recent_volunteers': recent_volunteers,
    }
    return render(request, 'volunteers/dashboard.html', context)


def opportunity_list(request):
    """List all volunteer opportunities with filtering."""
    form = OpportunityFilterForm(request.GET)
    opportunities = VolunteerOpportunity.objects.select_related('category').prefetch_related('volunteers')

    if form.is_valid():
        if form.cleaned_data.get('category'):
            opportunities = opportunities.filter(category=form.cleaned_data['category'])
        if form.cleaned_data.get('date_from'):
            opportunities = opportunities.filter(date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            opportunities = opportunities.filter(date__lte=form.cleaned_data['date_to'])
        if form.cleaned_data.get('search'):
            search_term = form.cleaned_data['search']
            opportunities = opportunities.filter(
                Q(title__icontains=search_term) | Q(description__icontains=search_term)
            )

    categories = Category.objects.all()

    context = {
        'opportunities': opportunities,
        'form': form,
        'categories': categories,
    }
    return render(request, 'volunteers/opportunity_list.html', context)


def opportunity_detail(request, pk):
    """View details of a specific opportunity."""
    opportunity = get_object_or_404(
        VolunteerOpportunity.objects.select_related('category').prefetch_related('volunteers'),
        pk=pk
    )
    context = {
        'opportunity': opportunity,
    }
    return render(request, 'volunteers/opportunity_detail.html', context)


def opportunity_create(request):
    """Create a new volunteer opportunity."""
    if request.method == 'POST':
        form = VolunteerOpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.save()
            messages.success(request, f'Opportunity "{opportunity.title}" created successfully!')
            return redirect('volunteers:opportunity_list')
    else:
        form = VolunteerOpportunityForm()

    context = {
        'form': form,
        'title': 'Add New Opportunity',
        'button_text': 'Create Opportunity',
    }
    return render(request, 'volunteers/opportunity_form.html', context)


def opportunity_edit(request, pk):
    """Edit an existing volunteer opportunity."""
    opportunity = get_object_or_404(VolunteerOpportunity, pk=pk)

    if request.method == 'POST':
        form = VolunteerOpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            opportunity = form.save()
            messages.success(request, f'Opportunity "{opportunity.title}" updated successfully!')
            return redirect('volunteers:opportunity_list')
    else:
        form = VolunteerOpportunityForm(instance=opportunity)

    context = {
        'form': form,
        'opportunity': opportunity,
        'title': 'Edit Opportunity',
        'button_text': 'Update Opportunity',
    }
    return render(request, 'volunteers/opportunity_form.html', context)


def opportunity_delete(request, pk):
    """Delete a volunteer opportunity."""
    opportunity = get_object_or_404(VolunteerOpportunity, pk=pk)

    if request.method == 'POST':
        title = opportunity.title
        opportunity.delete()
        messages.success(request, f'Opportunity "{title}" deleted successfully!')
        return redirect('volunteers:opportunity_list')

    context = {
        'opportunity': opportunity,
    }
    return render(request, 'volunteers/opportunity_confirm_delete.html', context)


def volunteer_signup(request, opportunity_id=None):
    """Sign up a volunteer for an opportunity."""
    initial = {}
    if opportunity_id:
        opportunity = get_object_or_404(VolunteerOpportunity, pk=opportunity_id)
        initial['opportunity'] = opportunity

    if request.method == 'POST':
        form = VolunteerForm(request.POST)
        if form.is_valid():
            volunteer = form.save()
            messages.success(
                request,
                f'Thank you {volunteer.name}! You have successfully signed up for "{volunteer.opportunity.title}".'
            )
            return redirect('volunteers:dashboard')
    else:
        form = VolunteerForm(initial=initial)

    opportunities = VolunteerOpportunity.objects.filter(
        date__gte=timezone.now().date()
    ).select_related('category')

    context = {
        'form': form,
        'opportunities': opportunities,
    }
    return render(request, 'volunteers/volunteer_signup.html', context)


def volunteer_list(request):
    """List all volunteers."""
    volunteers = Volunteer.objects.select_related('opportunity', 'opportunity__category')

    context = {
        'volunteers': volunteers,
    }
    return render(request, 'volunteers/volunteer_list.html', context)


def volunteer_delete(request, pk):
    """Delete a volunteer registration."""
    volunteer = get_object_or_404(Volunteer, pk=pk)

    if request.method == 'POST':
        name = volunteer.name
        volunteer.delete()
        messages.success(request, f'Volunteer registration for "{name}" deleted successfully!')
        return redirect('volunteers:volunteer_list')

    context = {
        'volunteer': volunteer,
    }
    return render(request, 'volunteers/volunteer_confirm_delete.html', context)


# API Views for React Components
def api_opportunities(request):
    """API endpoint for opportunities list with filtering."""
    opportunities = VolunteerOpportunity.objects.select_related('category').prefetch_related('volunteers')

    # Apply filters
    category_id = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')

    if category_id:
        opportunities = opportunities.filter(category_id=category_id)
    if date_from:
        opportunities = opportunities.filter(date__gte=date_from)
    if date_to:
        opportunities = opportunities.filter(date__lte=date_to)
    if search:
        opportunities = opportunities.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    data = [{
        'id': opp.id,
        'title': opp.title,
        'description': opp.description,
        'date': opp.date.isoformat(),
        'category': {
            'id': opp.category.id,
            'name': opp.category.name,
            'slug': opp.category.slug,
        },
        'volunteer_count': opp.volunteer_count,
    } for opp in opportunities]

    return JsonResponse({'opportunities': data})


def api_dashboard_stats(request):
    """API endpoint for dashboard statistics."""
    today = timezone.now().date()

    stats = {
        'total_opportunities': VolunteerOpportunity.objects.count(),
        'upcoming_opportunities': VolunteerOpportunity.objects.filter(date__gte=today).count(),
        'total_volunteers': Volunteer.objects.count(),
        'categories': list(Category.objects.annotate(
            opportunity_count=Count('opportunities'),
            volunteer_count=Count('opportunities__volunteers')
        ).values('id', 'name', 'slug', 'opportunity_count', 'volunteer_count')),
    }

    return JsonResponse(stats)


# ============================================
# Advanced Export System API Views
# ============================================

def _get_filtered_opportunities(request):
    """Helper function to get filtered opportunities based on request params."""
    opportunities = VolunteerOpportunity.objects.select_related('category').prefetch_related('volunteers')

    # Category filtering (supports multiple categories)
    categories = request.GET.getlist('categories[]') or request.GET.getlist('categories')
    if categories:
        opportunities = opportunities.filter(category_id__in=categories)

    # Date range filtering
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        opportunities = opportunities.filter(date__gte=date_from)
    if date_to:
        opportunities = opportunities.filter(date__lte=date_to)

    return opportunities


def api_categories(request):
    """API endpoint to get all categories for export filters."""
    categories = Category.objects.annotate(
        opportunity_count=Count('opportunities')
    ).values('id', 'name', 'slug', 'opportunity_count')

    return JsonResponse({'categories': list(categories)})


def api_export_preview(request):
    """API endpoint to preview export data with filters applied."""
    opportunities = _get_filtered_opportunities(request)

    data = [{
        'id': opp.id,
        'title': opp.title,
        'category': opp.category.name,
        'date': opp.date.strftime('%Y-%m-%d'),
        'description': opp.description[:100] + '...' if len(opp.description) > 100 else opp.description,
        'volunteer_count': opp.volunteer_count,
    } for opp in opportunities]

    return JsonResponse({
        'opportunities': data,
        'total_count': len(data),
        'total_volunteers': sum(opp.volunteer_count for opp in opportunities),
    })


def export_csv(request):
    """Export opportunities as CSV with filters."""
    opportunities = _get_filtered_opportunities(request)
    filename = request.GET.get('filename', 'volunteer_opportunities')

    # Ensure .csv extension
    if not filename.endswith('.csv'):
        filename += '.csv'

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Category', 'Date', 'Description', 'Number of Volunteers'])

    for opp in opportunities:
        writer.writerow([
            opp.title,
            opp.category.name,
            opp.date.strftime('%Y-%m-%d'),
            opp.description,
            opp.volunteer_count,
        ])

    return response


def export_json(request):
    """Export opportunities as JSON with filters."""
    opportunities = _get_filtered_opportunities(request)
    filename = request.GET.get('filename', 'volunteer_opportunities')

    # Ensure .json extension
    if not filename.endswith('.json'):
        filename += '.json'

    data = {
        'exported_at': datetime.now().isoformat(),
        'total_records': opportunities.count(),
        'opportunities': [{
            'title': opp.title,
            'category': opp.category.name,
            'date': opp.date.strftime('%Y-%m-%d'),
            'description': opp.description,
            'volunteer_count': opp.volunteer_count,
        } for opp in opportunities]
    }

    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


def export_pdf(request):
    """Export opportunities as PDF with filters."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    except ImportError:
        return JsonResponse({
            'error': 'PDF export requires reportlab. Install with: pip install reportlab'
        }, status=500)

    opportunities = _get_filtered_opportunities(request)
    filename = request.GET.get('filename', 'volunteer_opportunities')

    # Ensure .pdf extension
    if not filename.endswith('.pdf'):
        filename += '.pdf'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
    )
    elements.append(Paragraph('Volunteer Opportunities Export', title_style))
    elements.append(Paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', styles['Normal']))
    elements.append(Spacer(1, 20))

    # Table data
    table_data = [['Title', 'Category', 'Date', 'Volunteers', 'Description']]

    for opp in opportunities:
        desc = opp.description[:80] + '...' if len(opp.description) > 80 else opp.description
        table_data.append([
            opp.title,
            opp.category.name,
            opp.date.strftime('%Y-%m-%d'),
            str(opp.volunteer_count),
            desc,
        ])

    # Create table with styling
    col_widths = [1.5*inch, 1.2*inch, 1*inch, 0.8*inch, 4.5*inch]
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    elements.append(table)

    # Summary
    elements.append(Spacer(1, 20))
    summary = f'Total Records: {len(table_data) - 1} | Total Volunteers: {sum(opp.volunteer_count for opp in opportunities)}'
    elements.append(Paragraph(summary, styles['Normal']))

    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response