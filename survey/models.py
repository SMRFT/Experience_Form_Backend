from djongo import models
class SurgicalExperience(models.Model):    
    SURGERY_SEVERITY_CHOICES = [
            ("Major", "Major"),
            ("Minor", "Minor"),
        ]
    # --- Form fields ---
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    occupation = models.CharField(max_length=100)
    surgeryType = models.CharField(max_length=100)
    surgeryYear = models.IntegerField()
    surgeryNature = models.CharField(max_length=20)
    surgerySeverity = models.CharField(
        max_length=10, choices=SURGERY_SEVERITY_CHOICES, blank=True, null=True
    )
    painHospital = models.IntegerField()   # Q7
    painDischarge = models.IntegerField()  # Q8
    recoveryWalk = models.IntegerField()   # Q9
    recoveryRoutine = models.IntegerField() # Q10
    workDaysLost = models.IntegerField()   # Q11
    submitted_at = models.DateTimeField(auto_now_add=True)

    # --- Assessment Results ---
    painScore = models.FloatField(null=True, blank=True)
    recoveryScore = models.FloatField(null=True, blank=True)
    workLossScore = models.IntegerField(null=True, blank=True)
    satisfactionScore = models.FloatField(null=True, blank=True)  # overall

    def _pain_points(self, value):
        """Q7/Q8 pain scoring"""
        if 0 <= value <= 2:
            return 5
        elif 3 <= value <= 4:
            return 4
        elif 5 <= value <= 6:
            return 3
        elif 7 <= value <= 8:
            return 2
        elif 9 <= value <= 10:
            return 1
        return 0

    def _recovery_points(self, days):
        """Q9/Q10 recovery scoring"""
        if 0 <= days <= 2:
            return 5
        elif 3 <= days <= 6:
            return 4
        elif 7 <= days <= 30:
            return 3
        elif 31 <= days <= 180:
            return 2
        elif days > 180:
            return 1
        return 0

    def _workdays_points(self, days):
        """Q11 workdays lost scoring, same as recovery rules"""
        return self._recovery_points(days)

    def save(self, *args, **kwargs):
        """Auto-calculate assessment results before saving"""

        # --- Pain Score ---
        q7_points = self._pain_points(self.painHospital)
        q8_points = self._pain_points(self.painDischarge)
        self.painScore = q7_points + q8_points  # Sum of points

        # --- Recovery Score ---
        q9_points = self._recovery_points(self.recoveryWalk)
        q10_points = self._recovery_points(self.recoveryRoutine)
        q11_points = self._workdays_points(self.workDaysLost)
        self.recoveryScore = q9_points + q10_points + q11_points  # Sum of points

        # --- Overall Satisfaction Score ---
        # As per your formula: (painScore + recoveryScore) / 5
        total_score = self.painScore + self.recoveryScore
        self.satisfactionScore = round(total_score / 5, 2)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.surgeryType} ({self.surgeryYear})"

    class Meta:
        db_table = "surgical-form"

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

class GERDQSurvey(models.Model):
    # Demographics
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=100, blank=True, null=True)
    mobile = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?\d{10,15}$')]
    )
    email = models.EmailField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)

    # Survey
    age = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)])


    responses = models.JSONField(default=dict)  # <-- stores full JSON payload

    total_score = models.IntegerField()
    interpretation = models.CharField(max_length=100)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "gerdq_surveys"

    def __str__(self):
        return f"{self.name} ({self.age}, {self.gender}) - Score {self.total_score}"

from django.db import models
from datetime import date

class MilestoneForm(models.Model):
    DELIVERY_CHOICES = [
        ("normal", "Normal Delivery"),
        ("cesarean", "C Section"),
    ]
    COMPLICATION_CHOICES = [
        ("no", "None"),
        ("preterm", "Preterm"),
        ("low_weight", "Low Weight"),
        ("nicu", "NICU"),
    ]

    name = models.CharField(max_length=100)
    dob = models.DateField()
    age_months = models.IntegerField(blank=True, null=True)
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    complication_before_after = models.BooleanField(default=False)
    complication_type = models.CharField(
        max_length=20,
        choices=COMPLICATION_CHOICES,
        default="none"
    )
    answers = models.JSONField(default=dict)  # ✅ Store all question answers
    feedback = models.JSONField(default=list)  # ✅ Store feedback array
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate age in months from DOB
        today = date.today()
        if self.dob:
            self.age_months = (today.year - self.dob.year) * 12 + (today.month - self.dob.month)
            # Optional: adjust if day of month has not passed yet
            if today.day < self.dob.day:
                self.age_months -= 1

        # Ensure complication_type is 'none' if no complication
        if not self.complication_before_after:
            self.complication_type = "none"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.age_months} months)"

from django.db import models

class StressForm(models.Model):
    name = models.CharField(max_length=100)
    dob = models.DateField()
    email = models.EmailField()
    gender = models.CharField(max_length=10)
    mobile = models.CharField(max_length=15)

    pss_raw = models.IntegerField()
    pss_percentage = models.FloatField()
    pss_responses = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "survey_stressform"

    def __str__(self):
        return self.name

from django.db import models

class WHOForm(models.Model):
    name = models.CharField(max_length=100)
    dob = models.DateField()
    email = models.EmailField()
    gender = models.CharField(max_length=10)
    mobile = models.CharField(max_length=15)

    who_raw = models.IntegerField()
    who_percentage = models.FloatField()
    who_responses = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "survey_whoform"

    def __str__(self):
        return self.name