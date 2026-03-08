from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Creates default groups and permissions for the Clinic System'

    def handle(self, *args, **options):
        groups_data = {
            'Patient': [
             'view_appointment', 
        'add_appointment',
        'change_appointment',
        'delete_appointment',
        'view_consultationrecord',
    ],
    'Doctor': [
        'view_appointment', 
        'change_appointment', 
        'delete_appointment',
        'view_consultationrecord', 
        'add_consultationrecord',
        'change_consultationrecord',
    ],
    'Receptionist': [
        'add_user', 
        'view_user', 
        'add_appointment', 
        'change_appointment', 
        'view_appointment',
        'delete_appointment',
    ],
    'Admin': [],
}

        for group_name, permissions in groups_data.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            # Assign Permissions to the Group
            for perm_code in permissions:
                try:
                    # Django permissions are named: 'codename' ('add_appointment')
                    permission = Permission.objects.get(codename=perm_code)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Permission {perm_code} not found.'))

        self.stdout.write(self.style.SUCCESS('Successfully set up all groups and permissions.'))