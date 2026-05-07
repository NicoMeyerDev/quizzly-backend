from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import IsQuizOwner
from rest_framework.response import Response

from quiz_management_app.models import Answer, Quiz, Question
from .serializers import QuizSerializer
from .services import download_audio, transcribe_audio, generate_quiz
import re

class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]

   
    def get_queryset(self):
        if self.action == 'list':
            return Quiz.objects.filter(user=self.request.user)
        return Quiz.objects.all()

    def create(self, request, *args, **kwargs):
        """Handles the creation of a new quiz based on a YouTube video URL provided in the request data."""
        
        video_url = request.data.get("url")

        if not video_url:
            return Response(
                {"detail": "YouTube-URL fehlt oder ist ungültig."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not re.match(r'https?://(www\.)?youtube\.com/watch\?v=[\w-]{11}', video_url):
            return Response(
        {"detail": "Ungültige YouTube-URL."},
        status=status.HTTP_400_BAD_REQUEST,
        )
        match = re.search(r'v=([a-zA-Z0-9_-]{11})', video_url)
        video_id =match.group(1)
        clean_url = f"https://www.youtube.com/watch?v={video_id}"
            

        try:
            audio_path = download_audio(clean_url)
            transcript = transcribe_audio(audio_path)
            quiz_data = generate_quiz(transcript)

            quiz = Quiz.objects.create(
                user=request.user,
                title=quiz_data["title"],
                description=quiz_data["description"],
                video_url=video_url,
            )

            for question_data in quiz_data["questions"]:
                question = Question.objects.create(
                    quiz=quiz,
                    question_title=question_data["question_title"],
                )

                for answer_data in question_data["answers"]:
                    Answer.objects.create(
                        question=question,
                        answer_text=answer_data["answer_text"],
                        is_correct=answer_data["is_correct"],
                    )

            serializer = self.get_serializer(quiz)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )