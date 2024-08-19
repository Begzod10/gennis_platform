from django.core.management import get_commands
import django

django.setup()

print(get_commands())
