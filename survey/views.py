from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import SurgicalExperience, GERDQSurvey
from .serializers import SurgicalExperienceSerializer, GERDQSurveySerializer

# -------------------------
# Surgical Experience Views
# -------------------------

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import mongoengine
#from .models_mongo import SurgicalExperience
from .serializers import SurgicalExperienceSerializer
from .models import SurgicalExperience

# POST → Create new record
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import mongoengine

#from .models_mongo import SurgicalExperience
from .serializers import SurgicalExperienceSerializer
from .models import SurgicalExperience 

# Connect to MongoDB
MONGODB_NAME = 'surgical_experience'
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

mongoengine.connect(
    db=MONGODB_NAME,
    host=MONGODB_HOST,
    port=MONGODB_PORT
)

# POST → Create new record
SATISFACTION_MAP = {
    1: "1/5 - Very Dissatisfied",
    2: "2/5 - Dissatisfied",
    3: "3/5 - Neutral",
    4: "4/5 - Satisfied",
    5: "5/5 - Very Satisfied",
}

@api_view(["POST"])
def submit_experience(request):
    data = request.data.copy()
    
    # Safely convert satisfaction to int
    satisfaction_value = data.get("satisfaction")
    try:
        score = int(satisfaction_value) if satisfaction_value not in [None, ""] else 0
    except ValueError:
        score = 0

    data["satisfaction_text"] = SATISFACTION_MAP.get(score, "")
    
    serializer = SurgicalExperienceSerializer(data=data)
    if serializer.is_valid():
        exp = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# GET → List all records
@api_view(["GET"])
def list_experiences(request):
    experiences = SurgicalExperience.objects.order_by('-submitted_at')
    data = []
    for exp in experiences:
        data.append({
            "id": str(exp.id),
            "name": exp.name,
            "mobile": exp.mobile,
            "email": exp.email,
            "age": exp.age,
            "gender": exp.gender,
            "occupation": exp.occupation,
            "surgeryType": exp.surgeryType,
            "surgeryYear": exp.surgeryYear,
            "surgeryNature": exp.surgeryNature,
            "surgerySeverity": exp.surgerySeverity,
            "painHospital": exp.painHospital,
            "painDischarge": exp.painDischarge,
            "recoveryWalk": exp.recoveryWalk,
            "recoveryRoutine": exp.recoveryRoutine,
            "workDaysLost": exp.workDaysLost,
            "satisfaction": exp.satisfaction,
            "submitted_at": exp.submitted_at,
            "painScore": exp.painScore,
            "recoveryScore": exp.recoveryScore,
            "workLossScore": exp.workLossScore,
            "satisfactionScore": exp.satisfactionScore,
        })
    return Response(data, status=status.HTTP_200_OK)


from django.db.models import Avg, Count

@api_view(["GET"])
def surgical_analytics(request):
    total = SurgicalExperience.objects.count()
    if total == 0:
        return Response({"message": "No submissions yet."}, status=status.HTTP_200_OK)

    data = {
        "total_submissions": total,
        "average_age": SurgicalExperience.objects.aggregate(Avg("age"))["age__avg"],
        "male_count": SurgicalExperience.objects.filter(gender="Male").count(),
        "female_count": SurgicalExperience.objects.filter(gender="Female").count(),
        "elective_count": SurgicalExperience.objects.filter(surgeryNature="Elective").count(),
        "emergency_count": SurgicalExperience.objects.filter(surgeryNature="Emergency").count(),
                "major_count": SurgicalExperience.objects.filter(surgerySeverity="Major").count(),  # ✅ Added
        "minor_count": SurgicalExperience.objects.filter(surgerySeverity="Minor").count(),
        "avg_workdays_lost": SurgicalExperience.objects.aggregate(Avg("workDaysLost"))["workDaysLost__avg"],
        "avg_satisfaction": SurgicalExperience.objects.aggregate(Avg("satisfaction"))["satisfaction__avg"],
    }
    return Response(data, status=status.HTTP_200_OK)

# -------------------------
# GERDQ Survey Views
# -------------------------

# Scoring map
SCORING = {
    "q1": [0, 1, 2, 3],  # heartburn
    "q2": [0, 1, 2, 3],  # regurgitation
    "q3": [3, 2, 1, 0],  # epigastric pain (reverse)
    "q4": [3, 2, 1, 0],  # nausea (reverse)
    "q5": [0, 1, 2, 3],  # sleep trouble
    "q6": [0, 1, 2, 3],  # medication
}

@api_view(["POST"])
def submit_surveyform(request):
    try:
        data = request.data
        responses = data.get("responses", {})

        if not responses:
            return Response({"error": "Missing 'responses' field"}, status=400)

        total = 0
        for q in ["q1", "q2", "q3", "q4", "q5", "q6"]:
            if q not in responses:
                return Response({"error": f"Missing field: {q}"}, status=400)
            idx = int(responses[q])
            if idx < 0 or idx > 3:
                return Response({"error": f"Invalid value for {q}. Must be 0–3"}, status=400)
            total += SCORING[q][idx]
            print()

        interpretation = "Suggestive of GERD" if total >= 8 else "Unlikely GERD"

        survey_data = {
            "name": data.get("name"),
            "gender": data.get("gender"),
            "mobile": data.get("mobile"),
            "email": data.get("email"),   # map to gmail field
            "occupation": data.get("occupation"),
            "age": data.get("age"),
            "responses": responses,       # 👈 store JSON here
            "total_score": total,
            "interpretation": interpretation,
        }

        serializer = GERDQSurveySerializer(data=survey_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)

@api_view(["GET"])
def list_surveyforms(request):
    """
    Get all GERD-Q survey responses.
    """
    surveys = GERDQSurvey.objects.all().order_by("-submitted_at")
    serializer = GERDQSurveySerializer(surveys, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def analytics_surveyform(request):
    surveys = GERDQSurvey.objects.all()
    total = surveys.count()

    if total == 0:
        return Response({"message": "No survey data yet"}, status=200)

    avg_score = sum([s.total_score for s in surveys]) / total
    gerd_positive = surveys.filter(total_score__gte=8).count()
    gerd_negative = total - gerd_positive

    return Response({
        "total_surveys": total,
        "average_score": round(avg_score, 2),
        "gerd_positive": gerd_positive,
        "gerd_negative": gerd_negative,
        "positive_percentage": round((gerd_positive / total) * 100, 2),
    })

# -------------------------
# milestone Survey Views
# -------------------------

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MilestoneForm
from .serializers import MilestoneFormSerializer

# Submit milestone form
@api_view(["POST"])
def submit_milestone(request):
    serializer = MilestoneFormSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # auto calculates age in months in model.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# List all milestone forms
@api_view(["GET"])
def list_milestones(request):
    milestones = MilestoneForm.objects.all().order_by("-created_at")
    serializer = MilestoneFormSerializer(milestones, many=True)
    return Response(serializer.data)

# Simple analytics (e.g., delivery type counts, avg age)
@api_view(["GET"])
def analytics_milestone(request):
    total = MilestoneForm.objects.count()
    normal_count = MilestoneForm.objects.filter(delivery_type="normal").count()
    csection_count = MilestoneForm.objects.filter(delivery_type="csection").count()
    avg_age = MilestoneForm.objects.all().aggregate(models.Avg("age"))["age__avg"]

    return Response({
        "total": total,
        "normal_delivery": normal_count,
        "csection_delivery": csection_count,
        "average_age_months": round(avg_age, 1) if avg_age else None,
    })

# WHO & stress survey/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import StressForm , WHOForm
from django.views.decorators.csrf import csrf_exempt
from .serializers import StressFormSerializer, WHOFormSerializer

@api_view(["POST"])
def submit_stress(request):
    serializer = StressFormSerializer(data=request.data)
    if serializer.is_valid():
        form = serializer.save()
        return Response(StressFormSerializer(form).data, status=201)
    return Response(serializer.errors, status=400)

@api_view(["POST"])
def submit_who(request):
    serializer = WHOFormSerializer(data=request.data)
    if serializer.is_valid():
        form = serializer.save()
        return Response(WHOFormSerializer(form).data, status=201)
    return Response(serializer.errors, status=400)

@api_view(["GET"])
def list_stress(request):
    forms = StressForm.objects.all().order_by("-created_at")
    serializer = StressFormSerializer(forms, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def list_who(request):
    forms = WHOForm.objects.all().order_by("-created_at")
    serializer = WHOFormSerializer(forms, many=True)
    return Response(serializer.data)
