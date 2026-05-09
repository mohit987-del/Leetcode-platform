from django.db import models
from django.urls import reverse


class ProblemTag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Problem(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    slug = models.SlugField(max_length=120, unique=True)
    title = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices)
    statement_html = models.TextField()
    constraints_md = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    source_name = models.CharField(max_length=100)
    source_url = models.URLField(blank=True)
    source_problem_id = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField(ProblemTag, related_name="problems", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["difficulty", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["source_name", "source_problem_id"],
                condition=~models.Q(source_problem_id=""),
                name="unique_source_problem_id_when_present",
            ),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("problems:detail", kwargs={"slug": self.slug})


class ProblemExample(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="examples")
    input_text = models.TextField()
    output_text = models.TextField()
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]


class ProblemStarterCode(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="starter_code")
    language = models.CharField(max_length=30)
    template_code = models.TextField()

    class Meta:
        unique_together = ("problem", "language")


class ProblemTestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="test_cases")
    input_data = models.TextField()
    expected_output = models.TextField()
    is_public = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)
    weight = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]
