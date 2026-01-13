from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Category(models.Model):
    """Categories for volunteer opportunities."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class VolunteerOpportunity(models.Model):
    """Volunteer opportunities that volunteers can sign up for."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='opportunities'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Volunteer Opportunities"
        ordering = ['date', 'title']

    def __str__(self):
        return f"{self.title} - {self.date}"

    @property
    def volunteer_count(self):
        return self.volunteers.count()


def validate_age(value):
    """Validate that volunteer is at least 18 years old."""
    if value < 18:
        raise ValidationError('Volunteers must be at least 18 years old.')


class Volunteer(models.Model):
    """Volunteers who sign up for opportunities."""
    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField(validators=[MinValueValidator(18), validate_age])
    expertise = models.TextField(help_text="Describe your skills and expertise")
    opportunity = models.ForeignKey(
        VolunteerOpportunity,
        on_delete=models.CASCADE,
        related_name='volunteers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.opportunity.title}"