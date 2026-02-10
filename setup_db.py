#!/usr/bin/env python
"""
Helper script to setup the database migrations
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

# Delete existing migration files (except __init__.py)
migrations_to_remove = [
    'budgets/migrations/0001_initial.py',
    'transactions/migrations/0001_initial.py',
]

base_path = os.path.dirname(__file__)
for mig_file in migrations_to_remove:
    full_path = os.path.join(base_path, mig_file)
    if os.path.exists(full_path):
        os.remove(full_path)
        print(f"Removed {mig_file}")

# Create fresh migrations
print("\nCreating fresh migrations...")
try:
    call_command('makemigrations', interactive=False)
    print("✓ Migrations created successfully")
except Exception as e:
    print(f"✗ Error creating migrations: {e}")
    sys.exit(1)

# Apply migrations
print("\nApplying migrations...")
try:
    call_command('migrate')
    print("✓ Migrations applied successfully")
except Exception as e:
    print(f"✗ Error applying migrations: {e}")
    sys.exit(1)

print("\n✓ Database setup complete!")
