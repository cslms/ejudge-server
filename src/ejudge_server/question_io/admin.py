from django.contrib import admin
from .models import Grader, Question


admin.site.register(Question)
admin.site.register(Grader)