from rest_framework import serializers

from quiz_management_app.models import Answer, Question, Quiz

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['answer_text', 'is_correct', 'created_at', 'updated_at']

class QuestionSerializer(serializers.ModelSerializer):
    questions_options = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question_title', "questions_options", "answer"]

    def get_questions_options(self, obj):
        return [answer.answer_text for answer in obj.answers.all()]


    def get_answer(self, obj):
            answer = obj.answers.filter(is_correct=True).first()
            if answer:
                return answer.answer_text
            return None

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'video_url', 'created_at', 'updated_at', "questions"]        
    
    
        