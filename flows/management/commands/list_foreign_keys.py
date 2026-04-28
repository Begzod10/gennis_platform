from django.core.management.base import BaseCommand
from django.db import models
from django.apps import apps

class Command(BaseCommand):
    help = 'Lists all foreign key relationships in the project'

    def handle(self, *args, **kwargs):
        all_models = [model for model in apps.get_models()]

        for model in all_models:
            model_name = model.__name__
            foreign_keys = [field for field in model._meta.get_fields() if isinstance(field, models.ForeignKey)]

            if foreign_keys:
                self.stdout.write(f"Model: {model_name}")
                for field in foreign_keys:
                    related_model = field.related_model.__name__
                    self.stdout.write(f"  ForeignKey: {field.name} -> {related_model}")
            else:
                self.stdout.write(f"Model: {model_name} (No ForeignKey relationships)")

            self.stdout.write("\n")
