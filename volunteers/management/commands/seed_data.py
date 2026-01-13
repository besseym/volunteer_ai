from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from volunteers.models import Category, VolunteerOpportunity, Volunteer


class Command(BaseCommand):
    help = 'Seeds the database with sample volunteer opportunities and volunteers'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Get categories
        tutoring = Category.objects.get(slug='tutoring')
        food_prep = Category.objects.get(slug='food-prep')
        senior_support = Category.objects.get(slug='senior-support')
        sports = Category.objects.get(slug='sports')
        other = Category.objects.get(slug='other')

        today = timezone.now().date()

        # Create sample opportunities
        opportunities_data = [
            {
                'title': 'Math Tutoring for High School Students',
                'description': 'Help high school students with algebra, geometry, and calculus. No teaching experience required, just a passion for math and helping others succeed. Sessions are held at the local library.',
                'date': today + timedelta(days=7),
                'category': tutoring,
            },
            {
                'title': 'Community Food Bank Meal Prep',
                'description': 'Join us in preparing nutritious meals for families in need. We will be cooking and packaging meals for distribution. All skill levels welcome - training provided on site.',
                'date': today + timedelta(days=3),
                'category': food_prep,
            },
            {
                'title': 'Senior Center Companion Visit',
                'description': 'Spend quality time with seniors at the Sunshine Senior Center. Activities include playing board games, reading, or simply having friendly conversations. Make a difference in someone\'s day!',
                'date': today + timedelta(days=5),
                'category': senior_support,
            },
            {
                'title': 'Youth Soccer Coaching Assistant',
                'description': 'Help coach our under-12 soccer team during Saturday morning practices. Previous soccer experience preferred but not required. Great opportunity for sports enthusiasts!',
                'date': today + timedelta(days=10),
                'category': sports,
            },
            {
                'title': 'Beach Cleanup Day',
                'description': 'Join our environmental initiative to clean up Sunset Beach. We provide all cleaning supplies and refreshments. Great outdoor activity for nature lovers!',
                'date': today + timedelta(days=14),
                'category': other,
            },
            {
                'title': 'ESL Conversation Practice',
                'description': 'Help non-native English speakers practice their conversation skills. Meet with small groups to discuss everyday topics and help build confidence in English communication.',
                'date': today + timedelta(days=8),
                'category': tutoring,
            },
            {
                'title': 'Soup Kitchen Weekend Service',
                'description': 'Serve meals to community members at our downtown soup kitchen. Shifts include food preparation, serving, and cleanup. A rewarding way to give back to the community.',
                'date': today + timedelta(days=2),
                'category': food_prep,
            },
            {
                'title': 'Senior Technology Workshop',
                'description': 'Teach seniors how to use smartphones, tablets, and computers. Topics include video calling family, sending emails, and online safety. Patience and tech-savviness needed!',
                'date': today + timedelta(days=12),
                'category': senior_support,
            },
        ]

        created_opportunities = []
        for opp_data in opportunities_data:
            opp, created = VolunteerOpportunity.objects.get_or_create(
                title=opp_data['title'],
                defaults=opp_data
            )
            created_opportunities.append(opp)
            if created:
                self.stdout.write(f'  Created opportunity: {opp.title}')
            else:
                self.stdout.write(f'  Opportunity exists: {opp.title}')

        # Create sample volunteers
        volunteers_data = [
            {
                'name': 'Sarah Johnson',
                'age': 28,
                'expertise': 'I have a degree in Mathematics and 3 years of tutoring experience. I love helping students understand complex concepts.',
                'opportunity': created_opportunities[0],
            },
            {
                'name': 'Michael Chen',
                'age': 35,
                'expertise': 'Professional chef with 10 years experience. Passionate about community service and teaching others cooking skills.',
                'opportunity': created_opportunities[1],
            },
            {
                'name': 'Emily Rodriguez',
                'age': 22,
                'expertise': 'Nursing student with experience in elderly care. I enjoy spending time with seniors and hearing their stories.',
                'opportunity': created_opportunities[2],
            },
            {
                'name': 'James Wilson',
                'age': 45,
                'expertise': 'Former college soccer player and youth coach. I have coached kids for 5 years and love the sport.',
                'opportunity': created_opportunities[3],
            },
            {
                'name': 'Lisa Thompson',
                'age': 31,
                'expertise': 'Environmental scientist passionate about ocean conservation. Organized several community cleanup events.',
                'opportunity': created_opportunities[4],
            },
            {
                'name': 'David Kim',
                'age': 26,
                'expertise': 'Computer Science graduate fluent in English and Korean. Experience teaching ESL to immigrant families.',
                'opportunity': created_opportunities[5],
            },
        ]

        for vol_data in volunteers_data:
            vol, created = Volunteer.objects.get_or_create(
                name=vol_data['name'],
                opportunity=vol_data['opportunity'],
                defaults=vol_data
            )
            if created:
                self.stdout.write(f'  Created volunteer: {vol.name}')
            else:
                self.stdout.write(f'  Volunteer exists: {vol.name}')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))