from rest_framework import serializers
from .models import AffiliateApplications

class AffiliateApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliateApplications
        fields = '__all__'
        read_only_fields = ['Affiliate_id', 'Submitted_at']

    def validate_Phone_no(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        return value

    def validate_Business_phone(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Business phone must contain only digits.")
        return value

    def validate_Terms_accepted(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the terms to apply.")
        return value
