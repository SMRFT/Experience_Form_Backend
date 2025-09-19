from rest_framework import serializers
from .models import SurgicalExperience, GERDQSurvey,MilestoneForm
from bson import ObjectId


class ObjectIdField(serializers.Field):
    def to_representation(self, value):
        return str(value)
    def to_internal_value(self, data):
        return ObjectId(data)
    
class SurgicalExperienceSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)

    class Meta:
        model = SurgicalExperience
        fields = "__all__"

class GERDQSurveySerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    class Meta:
        model = GERDQSurvey
        fields = "__all__"

class MilestoneFormSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)  
    class Meta:
        model = MilestoneForm
        fields = "__all__"

from rest_framework import serializers
from .models import StressForm

class StressFormSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    class Meta:
        model = StressForm
        fields = "__all__"

from rest_framework import serializers
from .models import WHOForm

class WHOFormSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    class Meta:
        model = WHOForm
        fields = "__all__"
