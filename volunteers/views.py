from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
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