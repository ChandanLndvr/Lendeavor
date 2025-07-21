from rest_framework import serializers
from .models import UserApplications
from .models import SignUp
from datetime import datetime
from .models import JobApplications, JobDetails

#--------------------- signup ----------------------

class SignUpSerializer(serializers.ModelSerializer):
    # These fields are write-only and used for password confirmation
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = SignUp
        # Include all required fields plus the two password fields for validation
        fields = ['First_name', 'Last_name', 'User_type', 'Email', 'password1', 'password2']

    def validate(self, data):
        # Ensure the two passwords match before creating the user
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        # Remove password2 since it is only for validation and not needed for creation
        validated_data.pop('password2')
        # Extract password1 to hash it properly
        password = validated_data.pop('password1')
        # Create a new SignUp instance with remaining validated data
        user = SignUp(**validated_data)
        # Use model method to hash the password
        user.set_password(password)
        # Save the user instance to the database
        user.save()
        return user

#----------------------- Apply method, user application -----------------------------

class UserApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserApplications
        fields = '__all__'

    def validate_Business_name(self, value):
        if not value:
            raise serializers.ValidationError("Legal name of business is required.")
        return value

    def validate_Doing_business_as(self, value):
        return value.strip() if value else value

    def validate_Business_address(self, value):
        if not value:
            raise serializers.ValidationError("Business address is required.")
        return value

    def validate_Industry(self, value):
        if not value:
            raise serializers.ValidationError("Industry is required.")
        return value

    def validate_Tax_ID(self, value):
        # Expecting pattern: "12-3456789" (10 characters with dash)
        if value:
            stripped = value.replace("-", "")
            if len(stripped) != 9 or not stripped.isdigit():
                raise serializers.ValidationError("Tax ID must be in the format 12-3456789.")
        else:
            raise serializers.ValidationError("Tax ID is required.")
        return value

    def validate_Entity(self, value):
        allowed = ['llc', 'corporation', 'sole_proprietor', 'partnership']
        if value.lower() not in allowed:
            raise serializers.ValidationError(f"Entity must be one of {', '.join(allowed)}.")
        return value.lower()

    def validate_Business_Start_date(self, value):
        if value:
            try:
                datetime.strptime(value, "%Y-%m")
            except ValueError:
                raise serializers.ValidationError("Start Date must be in YYYY-MM format.")
        else:
            raise serializers.ValidationError("Business start date is required.")
        return value

    def validate_Owner_First_Name(self, value):
        if not value:
            raise serializers.ValidationError("Owner's first name is required.")
        return value

    def validate_Owner_Last_Name(self, value):
        if not value:
            raise serializers.ValidationError("Owner's last name is required.")
        return value

    def validate_Birth_Date(self, value):
        if not value:
            raise serializers.ValidationError("Owner's date of birth is required.")
        return value

    def validate_Home_address(self, value):
        if not value:
            raise serializers.ValidationError("Home address is required.")
        return value

    def validate_Business_Email(self, value):
        if not value:
            raise serializers.ValidationError("Business email is required.")
        return value

    def validate_Phone_no(self, value):
        if value:
            digits = ''.join(filter(str.isdigit, value))
            if len(digits) != 10:
                raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        else:
            raise serializers.ValidationError("Phone number is required.")
        return value

    def validate_SSN(self, value):
        if value:
            stripped = value.replace("-", "")
            if len(stripped) != 9 or not stripped.isdigit():
                raise serializers.ValidationError("SSN must be in the format 123-45-6789.")
        else:
            raise serializers.ValidationError("SSN is required.")
        return value

    def validate_Ownership(self, value):
        if value < 1 or value > 100:
            raise serializers.ValidationError("Ownership percentage must be between 1 and 100.")
        return value

    def validate_Monthly_Revenue(self, value):
        if value < 0:
            raise serializers.ValidationError("Monthly revenue cannot be negative.")
        return value

    def validate_Funds_Requested(self, value):
        if value < 500:
            raise serializers.ValidationError("Requested funds should be at least $500.")
        return value

    def validate_Existing_loans(self, value):
        if value.lower() not in ['yes', 'no']:
            raise serializers.ValidationError("Existing loans must be 'yes' or 'no'.")
        return value.lower()

    def validate_First_time(self, value):
        if value.lower() not in ['yes', 'no']:
            raise serializers.ValidationError("First time must be 'yes' or 'no'.")
        return value.lower()

    def validate_Documents(self, value):
        if value:
            if not value.name.endswith('.pdf'):
                raise serializers.ValidationError("Uploaded document must be a PDF.")
            if value.size > 12 * 1024 * 1024:  # 10MB limit
                raise serializers.ValidationError("File size must be under 10MB.")
        else:
            raise serializers.ValidationError("Financial statement upload is required.")
        return value
    
#--------------------- Job application --------------------

class JobApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplications
        fields = '__all__'
        read_only_fields = ['Application_id', 'Applied_on']

    def validate_Degree_year(self, value):
        from datetime import date
        current_year = date.today().year
        if value > current_year:
            raise serializers.ValidationError("Degree year cannot be in the future.")
        return value

    def validate_Phone_no(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain digits only.")
        if len(value) < 10:
            raise serializers.ValidationError("Phone number is too short.")
        return value
    
    def create(self, validated_data):
        job_instance = validated_data.get('Job')
        validated_data['Job_title'] = job_instance.Title if job_instance else ''
        return super().create(validated_data)
