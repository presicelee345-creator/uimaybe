import hashlib
from django.core.management.base import BaseCommand
from api.models import User


class Command(BaseCommand):
    help = 'Create default admin account'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(email='admin@nc100bw.org').exists():
            User.objects.create(
                email='admin@nc100bw.org',
                password=hashlib.sha256('Admin@1234'.encode()).hexdigest(),
                first_name='Admin',
                last_name='User',
                role='admin',
            )
            self.stdout.write('✅ Default admin created: admin@nc100bw.org / Admin@1234')
        else:
            self.stdout.write('Admin already exists.')
