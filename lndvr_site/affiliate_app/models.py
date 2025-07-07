from django.db import models

class AffiliateApplications(models.Model):
    Affiliate_id = models.CharField(max_length=10, primary_key=True)
    First_name = models.CharField(max_length=100)
    Last_name = models.CharField(max_length=100)
    Email = models.EmailField()
    Phone_no = models.CharField(max_length=20)
    Company = models.CharField(max_length=200, blank=True)
    Title = models.CharField(max_length=100, blank=True)
    Website = models.URLField(blank=True)
    Business_phone = models.CharField(max_length=20, blank=True)
    Is_payment = models.CharField(max_length=10)
    Is_influencer = models.CharField(max_length=10)
    Terms_accepted = models.BooleanField(default=False)
    Submitted_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.Affiliate_id:
            last_appln = AffiliateApplications.objects.order_by('-Affiliate_id').first()
            if last_appln and last_appln.Affiliate_id.startswith('AF'):
                last_num = int(last_appln.Affiliate_id[2:])
                next_num = last_num + 1
            else:
                next_num = 101
            self.Affiliate_id = f'AF{next_num}'
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'Affiliate_applications'

    def __str__(self):
        return f"{self.First_name} {self.Last_name}"
