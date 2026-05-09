from django.contrib import admin

from .models import Problem, ProblemExample, ProblemStarterCode, ProblemTag, ProblemTestCase


class ProblemExampleInline(admin.TabularInline):
    model = ProblemExample
    extra = 1


class ProblemStarterCodeInline(admin.TabularInline):
    model = ProblemStarterCode
    extra = 1


class ProblemTestCaseInline(admin.TabularInline):
    model = ProblemTestCase
    extra = 1


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("title", "difficulty", "is_published", "source_name")
    list_filter = ("difficulty", "is_published", "source_name")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "slug")
    filter_horizontal = ("tags",)
    inlines = [ProblemExampleInline, ProblemStarterCodeInline, ProblemTestCaseInline]


@admin.register(ProblemTag)
class ProblemTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
