from django.contrib import admin
from django.db.models import Count
from rorapp.models import Senator, Title


# Inline table showing related game players
class TitleInline(admin.TabularInline):
    model = Title
    extra = 0


# Admin configuration for senators
@admin.register(Senator)
class SenatorAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "game",
        "faction",
        "name",
        "code",
        "generation",
        "death_step",
        "rank",
        "title_count",
    )
    search_fields = (
        "id",
        "game__id",
        "faction__id",
        "name",
        "code",
        "generation",
        "death_step__id",
        "rank",
    )
    inlines = [TitleInline]

    def title_count(self, obj):
        return obj.titles.annotate(num_titles=Count('id')).count()
