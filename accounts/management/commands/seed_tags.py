from django.core.management.base import BaseCommand

from accounts.models import Tag

MOODS = ["Stressed", "Anxious", "Sad", "Overwhelmed", "Lonely", "Angry", "Tired", "Hopeful"]
INTERESTS = ["School", "Family", "Relationships", "Friends", "Work", "Gaming", "Music", "Health"]


class Command(BaseCommand):
    help = "Create the starter mood and interest tags."

    def handle(self, *args, **options):
        for name in MOODS:
            Tag.objects.get_or_create(name=name, defaults={"kind": Tag.MOOD})
        for name in INTERESTS:
            Tag.objects.get_or_create(name=name, defaults={"kind": Tag.INTEREST})
        self.stdout.write(self.style.SUCCESS("Tags seeded."))