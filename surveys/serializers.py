from rest_framework import serializers

from .models import Survey, SurveyQuestion, SurveyQuestionOption, SurveySubmission, SurveyAnswer


class SurveyQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestionOption
        fields = ['id', 'text', 'order']


class SurveyQuestionOptionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestionOption
        fields = ['text', 'order']


class SurveyQuestionSerializer(serializers.ModelSerializer):
    options = SurveyQuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyQuestion
        fields = ['id', 'text', 'type', 'order', 'is_required', 'options']


class SurveyQuestionWriteSerializer(serializers.ModelSerializer):
    options = SurveyQuestionOptionWriteSerializer(many=True, required=False)

    class Meta:
        model = SurveyQuestion
        fields = ['text', 'type', 'order', 'is_required', 'options']

    def validate(self, attrs):
        if attrs.get('type') == 'test' and not attrs.get('options'):
            raise serializers.ValidationError("Test turi uchun variantlar kiritilishi shart.")
        return attrs


class SurveyAdminCreateSerializer(serializers.ModelSerializer):
    questions = SurveyQuestionWriteSerializer(many=True)

    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'target_role', 'branch', 'deadline', 'is_anonymous', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        survey = Survey.objects.create(
            created_by=self.context['request'].user,
            **validated_data
        )
        for q_data in questions_data:
            options_data = q_data.pop('options', [])
            question = SurveyQuestion.objects.create(survey=survey, **q_data)
            for opt in options_data:
                SurveyQuestionOption.objects.create(question=question, **opt)
        return survey


class SurveyAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['title', 'description', 'target_role', 'branch', 'deadline', 'is_active', 'is_anonymous']


class SurveyAdminListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    questions_count = serializers.IntegerField(source='questions.count', read_only=True)
    submissions_count = serializers.IntegerField(source='submissions.count', read_only=True)
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'description', 'target_role',
            'branch', 'branch_name',
            'deadline', 'is_active', 'is_anonymous',
            'status', 'questions_count', 'submissions_count', 'created_at'
        ]

    def get_status(self, obj):
        return obj.status

    def get_branch_name(self, obj):
        return obj.branch.name if obj.branch else 'Barcha branchlar'


class SurveyAdminDetailSerializer(serializers.ModelSerializer):
    questions = SurveyQuestionSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'description', 'target_role',
            'branch', 'branch_name',
            'deadline', 'is_active', 'is_anonymous',
            'status', 'questions', 'created_at'
        ]

    def get_status(self, obj):
        return obj.status

    def get_branch_name(self, obj):
        return obj.branch.name if obj.branch else 'Barcha branchlar'


class SurveyMobileListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    questions_count = serializers.IntegerField(source='questions.count', read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'status', 'deadline', 'questions_count', 'created_at']

    def get_status(self, obj):
        return obj.status


class SurveyMobileDetailSerializer(serializers.ModelSerializer):
    questions = SurveyQuestionSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'status', 'deadline', 'questions']

    def get_status(self, obj):
        return obj.status


class AnswerItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    value = serializers.CharField(allow_blank=False, max_length=500)


class SurveySubmitSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField(required=False, allow_null=True)
    answers = AnswerItemSerializer(many=True)

    def validate(self, attrs):
        survey = self.context['survey']
        user = self.context['request'].user
        teacher_id = attrs.get('teacher_id')

        qs = SurveySubmission.objects.filter(survey=survey, respondent=user)
        if teacher_id:
            qs = qs.filter(target_teacher_id=teacher_id)
        else:
            qs = qs.filter(target_teacher__isnull=True)

        if qs.exists():
            raise serializers.ValidationError("Bu so'rovnoma allaqachon to'ldirilgan.")

        required_ids = set(survey.questions.filter(is_required=True).values_list('id', flat=True))
        answered_ids = {a['question_id'] for a in attrs['answers']}
        missing = required_ids - answered_ids
        if missing:
            raise serializers.ValidationError(f"Majburiy savollar javoblanmagan: {missing}")

        questions = {q.id: q for q in survey.questions.prefetch_related('options').all()}
        for answer in attrs['answers']:
            qid = answer['question_id']
            if qid not in questions:
                raise serializers.ValidationError(f"Savol topilmadi: {qid}")
            q = questions[qid]
            val = answer['value']

            if q.type == 'yes_no' and val not in ('yes', 'no'):
                raise serializers.ValidationError(f"Savol {qid}: faqat 'yes' yoki 'no'.")

            if q.type == 'star':
                if not val.isdigit() or int(val) not in range(1, 6):
                    raise serializers.ValidationError(f"Savol {qid}: 1 dan 5 gacha yulduz kiriting.")

            if q.type == 'test':
                valid_ids = set(str(o.id) for o in q.options.all())
                if val not in valid_ids:
                    raise serializers.ValidationError(f"Savol {qid}: noto'g'ri variant.")

        return attrs

    def save(self):
        survey = self.context['survey']
        user = self.context['request'].user
        role_info = self.context['role_info']
        teacher_id = self.validated_data.get('teacher_id')

        submission = SurveySubmission.objects.create(
            survey=survey,
            respondent=user,
            respondent_role=role_info['role'],
            student_ref=role_info.get('student'),
            teacher_ref=role_info.get('teacher'),
            parent_ref=role_info.get('parent'),
            branch=user.branch,
            target_teacher_id=teacher_id,
        )
        SurveyAnswer.objects.bulk_create([
            SurveyAnswer(submission=submission, question_id=a['question_id'], value=a['value'])
            for a in self.validated_data['answers']
        ])
        return submission


class SubmissionAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    question_type = serializers.CharField(source='question.type', read_only=True)

    class Meta:
        model = SurveyAnswer
        fields = ['question_id', 'question_text', 'question_type', 'value']


class SurveySubmissionListSerializer(serializers.ModelSerializer):
    respondent_name = serializers.SerializerMethodField()
    target_teacher_name = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = SurveySubmission
        fields = ['id', 'respondent_name', 'respondent_role', 'branch_name', 'target_teacher_name', 'submitted_at']

    def get_respondent_name(self, obj):
        return f"{obj.respondent.name} {obj.respondent.surname}".strip()

    def get_target_teacher_name(self, obj):
        if obj.target_teacher:
            u = obj.target_teacher.user
            return f"{u.name} {u.surname}".strip()
        return None

    def get_branch_name(self, obj):
        return obj.branch.name if obj.branch else None


class SurveySubmissionDetailSerializer(serializers.ModelSerializer):
    respondent_name = serializers.SerializerMethodField()
    target_teacher_name = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    answers = SubmissionAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = SurveySubmission
        fields = [
            'id', 'respondent_name', 'respondent_role',
            'branch_name', 'target_teacher_name',
            'submitted_at', 'answers'
        ]

    def get_respondent_name(self, obj):
        return f"{obj.respondent.name} {obj.respondent.surname}".strip()

    def get_target_teacher_name(self, obj):
        if obj.target_teacher:
            u = obj.target_teacher.user
            return f"{u.name} {u.surname}".strip()
        return None

    def get_branch_name(self, obj):
        return obj.branch.name if obj.branch else None
