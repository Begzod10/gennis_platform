import pprint
from datetime import datetime

from rest_framework import serializers

from branch.models import Branch
from branch.serializers import BranchSerializer
from classes.models import ClassNumber, ClassColors
from language.models import Language
from language.serializers import LanguageSerializers
from students.models import DeletedNewStudent
from students.models import Student, DeletedStudent, StudentHistoryGroups
from subjects.models import Subject, SubjectLevel
from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from system.models import System
from system.serializers import SystemSerializers
from teachers.models import Teacher, TeacherHistoryGroups
from teachers.serializers import TeacherSerializer
from time_table.models import GroupTimeTable
from group.functions.CreateSchoolStudentDebts import create_school_student_debts
from group.models import Group, GroupReason, CourseTypes


class AddClassesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'branch']
