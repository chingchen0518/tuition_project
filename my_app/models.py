from django.db import models

# Create your models here.

class Classroom(models.Model):
    crId = models.AutoField(primary_key=True,default='0')
    quota = models.IntegerField(default=0)

    class Meta:
        db_table = 'Classroom'

class Teacher(models.Model):
    tId = models.AutoField(primary_key=True,default=0)
    teacher_name = models.CharField(default="-", null=True, max_length=10)


    class Meta:
        db_table = 'Teacher'

class Class(models.Model):
    cId = models.AutoField(primary_key=True)
    category = models.CharField(default="-", null=False, max_length=20)
    subject = models.CharField(default="-", null=False, max_length=20)
    time = models.TimeField(null=True, blank=True)
    year = models.IntegerField(default=0)
    years_old = models.IntegerField(default=0)
    quota = models.IntegerField(default=0)
    crId = models.ForeignKey(Classroom, on_delete=models.CASCADE, to_field='crId', auto_created=False, unique=False,default='0')
    tId = models.OneToOneField(Teacher, to_field='tId',  on_delete=models.CASCADE, auto_created=False, default=0)

    class Meta:
        db_table = 'Class'
#
class Students(models.Model):
    sId = models.AutoField(primary_key=True)
    name = models.CharField(default="-", null=False, max_length=20)
    parent_name = models.CharField(default="-", null=False, max_length=20)
    hp = models.CharField(default="-", null=False, max_length=10)
    parent_hp = models.CharField(default="-", null=False, max_length=10)
    years_old = models.IntegerField(default=0)
    school = models.CharField(default="-", null=False, max_length=20)
    birthday = models.DateField(null=True,blank=True)
    remark = models.CharField(default="-", null=False, max_length=1000)
    address = models.CharField(default="-", null=True, max_length=100)

    class Meta:
        db_table = 'Students'

class Enrolled(models.Model):
    sId = models.ForeignKey(Students, on_delete=models.CASCADE, to_field='sId', auto_created=False, unique=False, default=0)
    cId = models.ForeignKey(Class, on_delete=models.CASCADE, to_field='cId', auto_created=False, unique=False,default=0)
#
#     class Meta:
#         db_table = 'Enrolled'
#
