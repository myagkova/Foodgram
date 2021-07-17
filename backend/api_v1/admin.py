from django.contrib import admin

from .models import CustomUser, Ingredient, Recipe, Tag


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class UserAdmin(admin.ModelAdmin):
    pass
