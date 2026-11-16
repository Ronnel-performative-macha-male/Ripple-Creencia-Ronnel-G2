from django.core.management.base import BaseCommand

from accounts.models import User

# TEST accounts only. Do not reuse these passwords anywhere else.
ACCOUNTS = [
    ("testmember", "testmember@example.com", "Member", "One", User.MEMBER, "Ripple#Member1"),
    ("testmember2", "testmember2@example.com", "Member", "Two", User.MEMBER, "Ripple#Member2"),
    ("testmoderator", "testmoderator@example.com", "Mod", "Tester", User.MODERATOR, "Ripple#Mod1"),
]


class Command(BaseCommand):
    help = "Create test accounts (one Moderator, two Members) for demos and grading."

    def handle(self, *args, **options):
        for username, email, first, last, role, password in ACCOUNTS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "first_name": first, "last_name": last, "role": role},
            )
            user.role = role
            user.is_staff = role == User.MODERATOR
            user.set_password(password)
            user.save()
            self.stdout.write(f"{'Created' if created else 'Updated'} {username} ({role})")
