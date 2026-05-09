from django.core.management.base import BaseCommand

from apps.ingestion.services import load_problem_bundles


class Command(BaseCommand):
    help = "Import canonical problem bundles from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument("import_path", type=str)

    def handle(self, *args, **options):
        load_problem_bundles(options["import_path"])
        self.stdout.write(self.style.SUCCESS("Problems imported successfully."))
