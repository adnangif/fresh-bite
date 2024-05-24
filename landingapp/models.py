from django.db import models

# Create your models here.


class CoveredCity(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    city_image = models.ImageField(upload_to='city_images/', null=True, blank=True)
    wiki_link = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name = 'Covered City'
        verbose_name_plural = 'Covered Cities'

    def __str__(self):
        return self.name
