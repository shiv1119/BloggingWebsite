from polymorphic import PolymorphicModel, PolymorphicManager

from django.core.exceptions import ObjectDoesNotExist


class ConfigurationManager(PolymorphicManager):
    def get(self, *args, **kwargs):
        if self.model is Configuration:
            return super(ConfigurationManager, self).get(*args, **kwargs)
        else:
            assert not args and not kwargs
            try:
                return super(ConfigurationManager, self).get()
            except ObjectDoesNotExist:
                return self.model()


class Configuration(PolymorphicModel):
    admin_class = 'configuration.admin.ConfigurationAdmin'
    description = "Configuration"

    objects = ConfigurationManager()

    class Meta(object):
        verbose_name_plural = 'Configuration'
        unique_together = (
            ("polymorphic_ctype",),
        )

    def __unicode__(self):
        return self._meta.verbose_name.capitalize()

    def get_description(self):
        return self.description

    @classmethod
    def get_admin_class(class_):
        return class_.admin_class

    get_description.short_description = "Description"
