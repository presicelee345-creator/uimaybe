import hashlib
from django.core.management.base import BaseCommand
from ncbw.models import User


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
            self.stdout.write(self.style.SUCCESS(
                '✅ Admin created — Email: admin@nc100bw.org  Password: Admin@1234'
            ))
        else:
            self.stdout.write('Admin already exists.')
