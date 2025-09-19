from django.urls import path
from . import views

urlpatterns = [
    # Surgical Experience
    # path("surgical/analytics/", views.analytics),
    path('submit_surgical/', views.submit_experience, name='submit_experience'),
    path('get_surgical/', views.list_experiences, name='list_experiences'),
    path("analytics/", views.surgical_analytics, name="surgical_analytics"),

    # GERDQ Survey
    path("gerdq/submit/", views.submit_surveyform),
    path("gerdq/list_surveyforms/", views.list_surveyforms, name="list_surveyforms"),
    path("gerdq/analytics/", views.analytics_surveyform),

    # Milestone Form
    path("milestone/submit/", views.submit_milestone, name="submit_milestone"),
    path("milestone/list/", views.list_milestones, name="list_milestones"),
    path("milestone/analytics/", views.analytics_milestone, name="analytics_milestone"),

    # Stess Who
    path("stress/submit/", views.submit_stress, name="submit_stress"),
    path("stress/list/", views.list_stress, name="list_stress"),
    path("who/submit/", views.submit_who, name="submit_who"),
    path("who/list/", views.list_who, name="list_who"),
]
