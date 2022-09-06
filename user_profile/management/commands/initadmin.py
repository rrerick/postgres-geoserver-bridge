from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
class Command(BaseCommand):

    def handle(self, *args, **options):
        if User.objects.count() == 0:
            username = 'admin'
            password = 'admin'
            print('Creating account for %s' % (username))
            admin = User.objects.create_user(username=username, password=password)
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
        else:
            print('Admin accounts can only be initialized if no Accounts exist')