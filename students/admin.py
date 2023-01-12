from django.contrib import admin

# Register your models here.

from students.models import Course, Student


class StudentInLine(admin.TabularInline):
    model = Course.students.through
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', ]
    inlines = [StudentInLine,]
    exclude = ('students',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'birth_date']
    inlines = [StudentInLine, ]
