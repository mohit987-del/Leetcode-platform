import json
from pathlib import Path

from django.db import transaction

from apps.problems.models import Problem, ProblemExample, ProblemStarterCode, ProblemTag, ProblemTestCase


def load_problem_bundles(import_path):
    data = json.loads(Path(import_path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Import file must contain a list of problem bundles.")
    for bundle in data:
        import_problem_bundle(bundle)


@transaction.atomic
def import_problem_bundle(bundle):
    problem_data = bundle["problem"]
    source_data = bundle.get("source", {})
    lookup = {}
    if source_data.get("source_problem_id"):
        lookup["source_name"] = source_data.get("source_name", "import")
        lookup["source_problem_id"] = source_data["source_problem_id"]
    else:
        lookup["slug"] = problem_data["slug"]

    defaults = {
        "slug": problem_data["slug"],
        "title": problem_data["title"],
        "difficulty": problem_data["difficulty"],
        "statement_html": problem_data["statement_html"],
        "constraints_md": problem_data.get("constraints_md", ""),
        "is_published": True,
        "source_name": source_data.get("source_name", "import"),
        "source_url": source_data.get("source_url", ""),
    }
    problem, _ = Problem.objects.update_or_create(defaults=defaults, **lookup)

    tags = []
    for tag_value in bundle.get("tags", []):
        tag, _ = ProblemTag.objects.get_or_create(
            slug=tag_value.lower().replace(" ", "-"),
            defaults={"name": tag_value.title()},
        )
        tags.append(tag)
    problem.tags.set(tags)

    problem.examples.all().delete()
    for index, example in enumerate(bundle.get("examples", []), start=1):
        ProblemExample.objects.create(
            problem=problem,
            input_text=example["input_text"],
            output_text=example["output_text"],
            explanation=example.get("explanation", ""),
            order=index,
        )

    problem.starter_code.all().delete()
    for starter in bundle.get("starter_code", []):
        ProblemStarterCode.objects.create(
            problem=problem,
            language=starter["language"],
            template_code=starter["template_code"],
        )

    problem.test_cases.all().delete()
    for index, test_case in enumerate(bundle.get("public_test_cases", []), start=1):
        ProblemTestCase.objects.create(
            problem=problem,
            input_data=test_case["input_data"],
            expected_output=test_case["expected_output"],
            is_public=True,
            order=index,
            weight=test_case.get("weight", 1),
        )
    hidden_offset = len(bundle.get("public_test_cases", []))
    for index, test_case in enumerate(bundle.get("hidden_test_cases", []), start=1):
        ProblemTestCase.objects.create(
            problem=problem,
            input_data=test_case["input_data"],
            expected_output=test_case["expected_output"],
            is_public=False,
            order=hidden_offset + index,
            weight=test_case.get("weight", 1),
        )
    return problem
