from django.core.management.base import BaseCommand
from firstblog.models import BlogPost, Category, CustomUser  # Replace 'main' with your app name
import random

class Command(BaseCommand):
    help = 'Create 10 sample blog posts for testing'

    def handle(self, *args, **options):
        # Get or create a staff user to be the author
        try:
            user = CustomUser.objects.filter(is_staff=True).first()
            if not user:
                self.stdout.write(self.style.ERROR('No staff user found. Please create a staff user first.'))
                return
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR('No staff user found. Please create a staff user first.'))
            return
        
        # Get or create categories
        categories = []
        category_names = ['Technology', 'Science', 'Travel', 'Food', 'Lifestyle']
        
        for name in category_names:
            category, created = Category.objects.get_or_create(name=name)
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))
        
        # Sample posts data
        sample_posts = [
            {
                'title': 'The Future of Artificial Intelligence in 2024',
                'post': '''Artificial intelligence continues to transform industries at an unprecedented pace. From machine learning algorithms to natural language processing, AI is revolutionizing how we work and live.

In this comprehensive overview, we explore the latest trends in AI development, including the rise of generative AI, ethical considerations, and practical applications across various sectors.

Key points covered:
- Current state of AI technology
- Ethical implications and challenges
- Future predictions and developments
- How businesses can leverage AI effectively''',
                'view_count': 1250
            },
            {
                'title': 'Sustainable Living: Practical Tips for Everyday Life',
                'post': '''Adopting a sustainable lifestyle doesn\'t have to be complicated or expensive. In this guide, we share practical tips that anyone can implement to reduce their environmental footprint.

From simple changes in daily habits to more significant lifestyle adjustments, discover how you can contribute to a healthier planet while often saving money in the process.

Topics include:
- Reducing plastic waste
- Energy conservation at home
- Sustainable food choices
- Eco-friendly transportation options''',
                'view_count': 890
            },
            {
                'title': 'Mastering Django: Best Practices for Web Development',
                'post': '''Django remains one of the most popular Python web frameworks for good reason. Its "batteries-included" philosophy and robust security features make it ideal for building scalable web applications.

This post covers essential Django best practices that every developer should know, from project structure and settings management to deployment considerations.

We\'ll discuss:
- Project organization patterns
- Security best practices
- Performance optimization
- Deployment strategies
- Testing methodologies''',
                'view_count': 2100
            },
            {
                'title': 'Healthy Eating on a Busy Schedule',
                'post': '''Maintaining a healthy diet can be challenging when you\'re constantly on the go. This guide provides time-saving strategies and meal prep ideas that make healthy eating achievable even with the busiest schedules.

Learn how to:
- Plan meals efficiently
- Prepare healthy snacks
- Make quick nutritious meals
- Stay consistent with your goals''',
                'view_count': 760
            },
            {
                'title': 'Top Travel Destinations for Digital Nomads',
                'post': '''The rise of remote work has created new opportunities for location-independent professionals. Discover the best cities and countries for digital nomads in 2024, considering factors like cost of living, internet connectivity, and community.

Featured destinations include:
- Bali, Indonesia
- Lisbon, Portugal
- Medellín, Colombia
- Chiang Mai, Thailand
- Mexico City, Mexico''',
                'view_count': 1540
            },
            {
                'title': 'Machine Learning Fundamentals for Beginners',
                'post': '''Machine learning can seem intimidating, but understanding the basics is more accessible than you might think. This beginner-friendly introduction breaks down core concepts without overwhelming technical jargon.

We cover:
- What machine learning actually is
- Different types of ML algorithms
- Real-world applications
- Getting started with your first project
- Recommended learning resources''',
                'view_count': 980
            },
            {
                'title': 'Urban Gardening: Growing Food in Small Spaces',
                'post': '''You don\'t need a large backyard to grow your own food. Urban gardening techniques allow you to cultivate fresh produce even in apartments and small homes.

This comprehensive guide covers:
- Container gardening basics
- Best plants for small spaces
- Vertical gardening techniques
- Indoor growing solutions
- Pest management in confined spaces''',
                'view_count': 670
            },
            {
                'title': 'Web Development Trends Shaping 2024',
                'post': '''The web development landscape continues to evolve rapidly. Stay ahead of the curve by understanding the technologies and approaches that are gaining traction this year.

Key trends include:
- Serverless architecture adoption
- Jamstack methodology
- Web3 and blockchain integration
- Progressive Web Apps (PWAs)
- AI-powered development tools''',
                'view_count': 1320
            },
            {
                'title': 'Mindfulness and Mental Health in the Digital Age',
                'post': '''In our always-connected world, maintaining mental wellbeing requires intentional practice. Explore mindfulness techniques and digital wellness strategies that can help you find balance.

Topics covered:
- Digital detox strategies
- Meditation for beginners
- Managing information overload
- Building healthy tech habits
- Creating boundaries with devices''',
                'view_count': 540
            },
            {
                'title': 'Renewable Energy Solutions for Homeowners',
                'post': '''Transitioning to renewable energy is becoming increasingly accessible for homeowners. This guide examines the practical options available today, from solar panels to geothermal systems.

We discuss:
- Solar power installation considerations
- Wind energy for residential use
- Geothermal heating and cooling
- Government incentives and rebates
- Calculating return on investment''',
                'view_count': 830
            }
        ]

        # Create posts
        for i, post_data in enumerate(sample_posts, 1):
            try:
                post = BlogPost.objects.create(
                    title=post_data['title'],
                    post=post_data['post'],
                    author=user,
                    category=random.choice(categories),
                    view_count=post_data['view_count']
                )
                self.stdout.write(self.style.SUCCESS(f'Created post #{i}: {post.title}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating post #{i}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully created 10 blog posts!'))