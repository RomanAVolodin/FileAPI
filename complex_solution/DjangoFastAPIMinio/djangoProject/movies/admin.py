from django.contrib import admin

from movies.models import FilmWork


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'type',
        'creation_date',
        'rating',
    )

    list_filter = ('type',)

    search_fields = (
        'title',
        'description',
    )
