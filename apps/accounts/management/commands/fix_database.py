"""
Django management command to fix database issues
Run with: python manage.py fix_database
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Fix database by running migrations and creating tables'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Fixing database...")
        
        try:
            # Run migrations
            self.stdout.write("📦 Running migrations...")
            call_command('migrate', verbosity=2, interactive=False)
            self.stdout.write(self.style.SUCCESS("✅ Migrations completed"))
            
            # Check tables
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                self.stdout.write(f"✅ Found {len(tables)} tables:")
                for table in tables:
                    self.stdout.write(f"   - {table[0]}")
            
            self.stdout.write(self.style.SUCCESS("🎉 Database fixed successfully!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
            raise
