from importlib import import_module
from django.contrib import admin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
)
from .models import Configuration


class ConfigurationAdmin(PolymorphicChildModelAdmin):
    base_model = Configuration

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ConfigurationParentAdmin(PolymorphicParentModelAdmin):
    base_model = Configuration
    list_display = ('__unicode__', 'get_description')
    actions = None
    polymorphic_list = True

    def get_child_models(self):
        if self.child_models is not None:
            return self.child_models

        done = set()
        self.child_models = tuple()
        remaining = set([self.base_model])

        while remaining:
            current = remaining.pop()
            if current in done:
                continue

            done.add(current)

            remaining |= set(s for s in current.__subclasses__())

            if current is Configuration:
                continue

            if current._meta.abstract:
                continue

            admin_class = current.get_admin_class()

            if isinstance(admin_class, basestring):
                admin_module, admin_class = admin_class.rsplit('.', 1)
                admin_class = getattr(import_module(admin_module), admin_class)

            if not issubclass(admin_class, ConfigurationAdmin):
                raise TypeError("admin_class must be a ConfigurationAdmin")

            self.child_models = self.child_models + ((current, admin_class),)

        self.child_models = tuple(sorted(self.child_models))

        return self.child_models

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, *args, **kwargs):
        for child, child_admin_class in self.child_models:
            if child.objects.all().count() < 1:
                child.objects.create()

        return super(ConfigurationParentAdmin,
                     self).changelist_view(*args, **kwargs)

admin.site.register(Configuration, ConfigurationParentAdmin)
