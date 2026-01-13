from django.contrib import admin
from .models import Category, VolunteerOpportunity, Volunteer


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(VolunteerOpportunity)
class VolunteerOpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'date', 'volunteer_count', 'created_at']
    list_filter = ['category', 'date']
    search_fields = ['title', 'description']
    date_hierarchy = 'date'


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'opportunity', 'created_at']
    list_filter = ['opportunity__category', 'created_at']
    search_fields = ['name', 'expertise']
    raw_id_fields = ['opportunity']