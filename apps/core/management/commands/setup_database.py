from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import sys


class Command(BaseCommand):
    help = 'Setup database with migrations'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Setting up database...')
        
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS('✅ Database connection successful'))
            
            # Run makemigrations
            self.stdout.write('📝 Creating migrations...')
            call_command('makemigrations', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✅ Migrations created'))
            
            # Run migrations
            self.stdout.write('📦 Applying migrations...')
            call_command('migrate', verbosity=2)
            self.stdout.write(self.style.SUCCESS('✅ Migrations applied successfully'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Database setup failed: {e}'))
            sys.exit(1)
