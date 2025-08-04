from django.db import models
from django.utils.text import slugify
from myapp.models import SignUp

# Create your models here.

class Financial_news(models.Model):
    News_id = models.AutoField(primary_key=True)
    Title = models.CharField(max_length=250)
    Slug = models.SlugField(unique=True, blank=True)
    Date_publish = models.DateField()
    Content = models.TextField()
    Summary = models.TextField(blank=True)
    Added_by = models.ForeignKey(SignUp, on_delete=models.SET_NULL, null = True, db_column='added_by')
    Active = models.BooleanField(default=True)
    Added_on = models.DateTimeField(auto_now_add=True)
    Thumbnail = models.ImageField(upload_to='newsletter_thumb/', blank=True)

    class Meta:
        db_table = 'Financial_news'

    def __str__(self):
        return str(self.Added_by)

    def save(self, *args, **kwargs):
        if not self.Slug:
            self.Slug = slugify(f"{self.Title}-{self.Date_publish}")
        super().save(*args, **kwargs)