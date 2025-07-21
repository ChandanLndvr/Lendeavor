from rest_framework import serializers
from .models import JobDetails

class JobDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDetails
        fields = '__all__'

    def validate_Added_by(self, value):
        if not value.lower().endswith('@lendeavorusa.com'):
            raise serializers.ValidationError("You are not allowed to post a Job.")
        return value

    def validate_Email(self, value):
        if not value:
            raise serializers.ValidationError("An HR email is required.")
        return value