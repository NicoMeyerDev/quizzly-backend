from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import QuizSerializer
from quiz_management_app.models import Quiz

class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Quiz.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 