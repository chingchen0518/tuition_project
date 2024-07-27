from django.shortcuts import HttpResponse, render, redirect
import json
from django.http import JsonResponse
from django.db import connection

from django.shortcuts import render
import pdb

#include table
from my_app.models import Students, Enrolled, Class, Classroom, Teacher,Category

# Create your views here.
def homepage(request):
    return render(request, 'homepage.html')

def student_list(request):
    student_list = Students.objects.raw('SELECT * FROM Students')
    tingkat = ['xxx','國一','國二','國三','高一','高二','高三']

    return render(request, 'student_list.html',{'student_list':student_list,'tingkat':tingkat})

def student_detail(request,sId):
    student_detail = Students.objects.raw('SELECT * FROM Students WHERE sId=%s',[sId])
    tingkat = ['xxx','國一','國二','國三','高一','高二','高三']
    class_taken= Class.objects.raw('SELECT * FROM Enrolled,Class WHERE sId_id=%s AND Class.cId=Enrolled.cId_id',[sId])

    return render(request, 'student_detail.html',{'student_detail': student_detail[0],'tingkat':tingkat,'class_taken':class_taken})


def class_list(request):
    # class_list = Teacher.objects.raw('SELECT * FROM Teacher JOIN Class ON Class.tId_id = Teacher.tId JOIN ')
    class_list = Teacher.objects.raw('''SELECT Class.*, Teacher.*, COALESCE(enrolled_counts.tuple_count, 0) AS student_count,Class.quota - COALESCE(enrolled_counts.tuple_count, 0) AS remain
                                        FROM Class LEFT JOIN Teacher ON Class.tId_id = Teacher.tId
                                        LEFT JOIN (SELECT cId_id, COUNT(*) AS tuple_count FROM Enrolled GROUP BY cId_id
                                        ) AS enrolled_counts ON enrolled_counts.cId_id = Class.cId;''')
    # remain =
    return render(request, 'class_list.html',{'class_list': class_list})

def class_detail(request,cId):
    class_detail = Teacher.objects.raw('''SELECT Class.*, Teacher.*,Classroom.classroom_name, COALESCE(enrolled_counts.tuple_count, 0) AS student_count,Class.quota - COALESCE(enrolled_counts.tuple_count, 0) AS remain
                                            FROM Class LEFT JOIN Teacher ON Class.tId_id = Teacher.tId
                                            LEFT JOIN (SELECT cId_id, COUNT(*) AS tuple_count FROM Enrolled GROUP BY cId_id
                                            ) AS enrolled_counts ON enrolled_counts.cId_id = Class.cId JOIN Classroom ON Classroom.crId=Class.crId_id WHERE Class.cId=%s''',[cId])

    students = Students.objects.raw('SELECT * FROM Students,Enrolled WHERE Enrolled.sId_id=Students.sId AND Enrolled.cId_id=%s',[cId])
    return render(request, 'class_detail.html',{'class_detail': class_detail[0],'students':students})

def add_category(request):
    return render(request, 'add_category.html')

def add_category_action(request):
    category = request.POST['category']

    latest_id = Category.objects.latest('catId')
    latest_id = latest_id.catId
    latest_id = latest_id + 1

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Category VALUES (%s, %s)', (latest_id, category))

    return redirect('/')  # back to homepage


def add_class(request):
    category = Category.objects.raw('SELECT * FROM Category')
    teacher = Teacher.objects.raw('SELECT tId,teacher_name FROM Teacher')
    classroom = Classroom.objects.raw('SELECT * FROM Classroom')

    return render(request, 'add_class.html',{'categories':category,'teachers':teacher,'classrooms':classroom})

def add_class_action(request):
    category = request.POST['category']
    subject = request.POST['subject']
    time= request.POST['time']
    year = request.POST['year']
    quota = request.POST['quota']
    classroom = request.POST['classroom']
    teacher= request.POST['teacher']
    day = request.POST['day']
    years_old = request.POST['age']

    latest_id = Class.objects.latest('cId')
    latest_id = latest_id.cId
    cId = latest_id + 1

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Class VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (cId,category,subject,time,year,quota,classroom,teacher,day,years_old))
    return redirect('/')#back to homepage

def edit_class(request,cId):
    class_detail = Class.objects.raw('SELECT * FROM Class WHERE cId=%s',[cId])
    category = Category.objects.raw('SELECT * FROM Category')
    teacher = Teacher.objects.raw('SELECT tId,teacher_name FROM Teacher')
    classroom = Classroom.objects.raw('SELECT * FROM Classroom')
    return render(request, 'edit_class.html',{'class_detail':class_detail[0],'categories':category,'teachers':teacher,'classrooms':classroom})

def edit_class_action(request,cId):
    category = request.POST['category']
    subject = request.POST['subject']
    time= request.POST['time']
    year = request.POST['year']
    quota = request.POST['quota']
    classroom = request.POST['classroom']
    teacher= request.POST['teacher']
    day = request.POST['day']
    years_old = request.POST['age']

    with connection.cursor() as cursor:
        cursor.execute('UPDATE Class SET category=%s, subject=%s, time=%s, year=%s, quota=%s, crId_id=%s, tId_id=%s, day=%s, years_old=%s WHERE cId=%s', (category,subject,time,year,quota,classroom,teacher,day,years_old,cId))
    return redirect('/')#back to homepage


def add_teacher(request):
    return render(request, 'add_teacher.html')
def add_teacher_action(request):
    name = request.POST['name']
    phone = request.POST['phone']
    line = request.POST['line']

    latest_id = Teacher.objects.latest('tId')
    latest_id = latest_id.tId
    latest_id=latest_id + 1
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Teacher VALUES (%s, %s, %s, %s)', (latest_id,name,line,phone))

    return redirect('/')#back to homepage

def add_enroll(request,cId):
    student_list = Students.objects.raw('''SELECT sId,name FROM Students EXCEPT
                                        SELECT DISTINCT sId,name FROM Students,Enrolled 
                                        WHERE Students.sId = Enrolled.sId_id and Enrolled.cId_id=%s''',[cId])

    return render(request, 'add_enroll.html',{'student_list':student_list,'cId':cId})

def add_enroll_action(request,cId):
    new_students = request.POST.getlist('student')



    for i in new_students:
        # pdb.set_trace()
        latest_id = Enrolled.objects.latest('id')
        latest_id = latest_id.id
        latest_id=latest_id + 1

        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO Enrolled VALUES (%s, %s, %s, %s)', (latest_id,cId,i,"-"))

    return redirect('/')#back to homepage

def delete_enrolled_student(request,sId,cId):
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM Enrolled where cID_id=%s AND sId_id=%s', (cId, sId))

    class_detail=f'/class_detail/{cId}'
    return redirect(class_detail)#back to homepage

