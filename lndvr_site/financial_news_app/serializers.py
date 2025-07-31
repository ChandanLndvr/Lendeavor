from rest_framework import serializers
from financial_news_app.models import Financial_news



class Financial_news_serializers(serializers.ModelSerializer):
    Date_publish = serializers.DateField(
        input_formats=['%Y-%m-%d'],  # Your form gives ISO format like '2025-07-01'
        format='%m-%d-%y'
    )

    class Meta:
        model = Financial_news
        fields = "__all__"