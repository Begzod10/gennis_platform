import datetime
import os
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.generic import TemplateView
from branch.models import Branch
from classes.models import ClassNumber
from drf_spectacular.utils import extend_schema, OpenApiTypes

from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

# We initialize the client globally or inside the view.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1alpha"})
    except Exception as e:
        client = None
        print(f"Failed to initialize genai Client: {e}")
else:
    client = None

class GeminiTokenAPIView(APIView):
    """
    Generate an ephemeral token for Gemini Live API.
    """
    authentication_classes = []
    permission_classes = []

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def post(self, request, *args, **kwargs):
        if not client:
            return Response({"error": "GEMINI_API_KEY is not configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            expire_time = now + datetime.timedelta(minutes=30)

            token = client.auth_tokens.create(
                config={
                    "uses": 1,
                    "expire_time": expire_time.isoformat(),
                    "new_session_expire_time": (now + datetime.timedelta(minutes=1)).isoformat(),
                    "http_options": {"api_version": "v1alpha"},
                }
            )

            return Response({
                "token": token.name,
                "expires_at": expire_time.isoformat()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GeminiTemplateView(TemplateView):
    template_name = "gemini/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        branches = Branch.objects.filter(location__system__name='school',location__system__name__isnull=False)
        
        branch_data = []
        for branch in branches:
            classes = ClassNumber.objects.filter(branch=branch).prefetch_related('subjects')
            class_info = []
            for c in classes:
                subjects = [s.name for s in c.subjects.all() if s.name]
                if subjects:
                    class_info.append(f"{c.number}-sinf ({', '.join(subjects)})")
                else:
                    class_info.append(f"{c.number}-sinf")
                    
            branch_data.append({
                "name": branch.name,
                "classes": class_info
            })
            
        context['branches'] = branch_data
        return context
