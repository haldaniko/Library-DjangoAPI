from django.db import models
from django.core.validators import MinValueValidator


class CoverType(models.TextChoices):
    HARD = 'HARD', 'Hardcover'
    SOFT = 'SOFT', 'Softcover'


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=10,
        choices=CoverType.choices,
        default=CoverType.SOFT
    )
    inventory = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        unique_together = ('title', 'author')
