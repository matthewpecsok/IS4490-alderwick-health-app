import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from clinic.models import Patient
from clinic.seed import reset_database, seed_database


class Command(BaseCommand):
    help = "Load the synthetic Alderwick Family Health practice: providers, patients, schedules, messages, and accounts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete ALL existing data, audit history, and user accounts before seeding.",
        )
        parser.add_argument(
            "--as-of",
            help="Generate dates relative to this local date-time (YYYY-MM-DDTHH:MM) instead of now.",
        )

    def handle(self, *args, **options):
        if Patient.objects.exists():
            if not options["reset"]:
                raise CommandError("The database already has data. Re-run with --reset to start over.")
            reset_database()
            self.stdout.write("Existing data removed.")

        now = None
        if options["as_of"]:
            try:
                naive = datetime.datetime.fromisoformat(options["as_of"])
            except ValueError as exc:
                raise CommandError(f"Could not parse --as-of: {exc}") from exc
            now = timezone.make_aware(naive) if timezone.is_naive(naive) else naive

        summary = seed_database(now=now, log=self.stdout.write)
        self.stdout.write(self.style.SUCCESS("Alderwick demo data loaded:"))
        for key, value in summary.items():
            self.stdout.write(f"  {key.replace('_', ' ')}: {value}")
        self.stdout.write("Sign-in details are in USER-GUIDE.md.")
