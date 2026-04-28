from django.core.management.base import BaseCommand
from parties.models import Party, Competition


class Command(BaseCommand):
    help = 'Seed initial data'

    def handle(self, *args, **kwargs):
        parties_data = [
            {'name': 'Yulbars', 'color': '#4f8ef7', 'rating': 4.5, 'ball': 2850, 'desc': 'Kuchli va jasur'},
            {'name': 'Burgut', 'color': '#10b981', 'rating': 4.2, 'ball': 2600, 'desc': 'Tez va ziyrak'},
            {'name': 'Sher', 'color': '#f59e0b', 'rating': 4.0, 'ball': 2400, 'desc': 'Mard va dadil'},
            {'name': 'Qoplan', 'color': '#ec4899', 'rating': 3.8, 'ball': 2100, 'desc': 'Epchil va aqlli'},
        ]
        for pd in parties_data:
            Party.objects.get_or_create(name=pd['name'], defaults=pd)

        comps = [
            ('Matematika olimpiadasi', '🧮', '#4f8ef7'),
            ('Sport musobaqasi', '⚽', '#10b981'),
            ('Fan olimpiadasi', '🔬', '#8b5cf6'),
        ]
        for name, emoji, color in comps:
            Competition.objects.get_or_create(name=name, defaults={'emoji': emoji, 'color': color})

        self.stdout.write(self.style.SUCCESS('Seed data created successfully.'))
