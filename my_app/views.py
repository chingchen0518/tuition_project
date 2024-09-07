from django.shortcuts import HttpResponse, render, redirect
import json,os
from django.http import JsonResponse
from django.db import connection

from django.shortcuts import render
import pdb

#include table
from my_app.models import Students, Enrolled, Class, Classroom, Teacher,Category,Payment

# Create your views here.
def homepage(request):
    class_list = Class.objects.raw('''SELECT cId,time,years_old,subject,category,day,available,
                                        CASE
                                            WHEN (time>'12:59') THEN 0
                                            ELSE 1
                                            END AS morning
                                        FROM Class
                                        WHERE available=1
                                        ORDER BY time''')
    Days=['一','二','三','四','五','六','日']
    return render(request, 'homepage.html',{'class':class_list,'Days':Days})


def student_list(request):
    student_list = Students.objects.raw('''SELECT *,
                                            CASE 
                                                WHEN EXISTS (SELECT eId,period,COUNT(amount) AS paid_period,
                                                          CASE WHEN (COUNT(amount)=period) THEN 1
                                                          ELSE 0
                                                          END AS pay_or_not
                                                        FROM Enrolled
                                                        LEFT OUTER JOIN Payment ON Enrolled.eId=Payment.eId_id 
                                                        WHERE Enrolled.sId_id=s.sId
                                                        GROUP BY Enrolled.eId
                                                        HAVING pay_or_not = 0
                                                        ) THEN 0
                                                ELSE 1
                                        END AS fully_paid
                                        FROM Students s''')

    tingkat = ['xxx','國一','國二','國三','高一','高二','高三']

    return render(request, 'student_list.html',{'student_list':student_list,'tingkat':tingkat})

def student_detail(request,sId):
    student_detail = Students.objects.raw('''SELECT * FROM Students WHERE sId=%s''',[sId])
    tingkat = ['xxx','國一','國二','國三','高一','高二','高三']
    class_taken= Class.objects.raw('''SELECT year,eId,cId,day,time,remark,period,subject,category,Enrolled.cId_id,
                                        CASE
                                            WHEN (SELECT COUNT(amount) AS payment FROM Payment WHERE sId_id=%s AND Payment.eId_id=Enrolled.eId) = 1 THEN 1
                                            WHEN (SELECT COUNT(amount) AS payment FROM Payment WHERE sId_id=%s AND Payment.eId_id=Enrolled.eId) = 2 THEN 2
                                            ELSE 0
                                        END AS payment
                                        FROM Enrolled
                                        JOIN Class ON Class.cId = Enrolled.cId_id
                                        WHERE Enrolled.sId_id = %s
                                        ''',(sId,sId,sId))

    return render(request, 'student_detail.html',{'student_detail': student_detail[0],'tingkat':tingkat,'class_taken':class_taken})


def class_list(request,available):
    # class_list = Teacher.objects.raw('SELECT * FROM Teacher JOIN Class ON Class.tId_id = Teacher.tId JOIN ')
    class_list = Teacher.objects.raw('''SELECT Class.*, Teacher.*, COALESCE(enrolled_counts.tuple_count, 0) AS student_count,Class.quota - COALESCE(enrolled_counts.tuple_count, 0) AS remain
                                        FROM Class LEFT JOIN Teacher ON Class.tId_id = Teacher.tId
                                        LEFT JOIN (SELECT cId_id, COUNT(*) AS tuple_count FROM Enrolled GROUP BY cId_id
                                        ) AS enrolled_counts ON enrolled_counts.cId_id = Class.cId WHERE available=%s;''',[available])
    # remain =
    return render(request, 'class_list.html',{'class_list': class_list,'available':available})

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
    class_period = request.POST['class_period']

    latest_id = Class.objects.latest('cId')
    latest_id = latest_id.cId
    cId = latest_id + 1

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Class VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)', (cId,category,subject,time,year,quota,classroom,teacher,day,years_old,class_period))
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

def delete_class_action(request,cId):
    Class.objects.filter(cId=cId).delete()

    return redirect('/class_list/1')#back to homepage

def end_class_action(request,cId):
    with connection.cursor() as cursor:
        cursor.execute('UPDATE Class SET available=0 WHERE cId=%s',[cId])

    return redirect('/class_list/1')#back to homepage

def recover_class_action(request,cId):
    with connection.cursor() as cursor:
        cursor.execute('UPDATE Class SET available=1 WHERE cId=%s',[cId])
    return redirect('/class_list/0')  # back to homepage


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
    student_enrolled = Students.objects.raw('''SELECT DISTINCT sId,name FROM Students,Enrolled 
                                            WHERE Students.sId = Enrolled.sId_id and Enrolled.cId_id=%s''', [cId])

    return render(request, 'add_enroll.html',{'student_list':student_list,'student_enrolled':student_enrolled,'cId':cId})

def add_enroll_action(request,cId):
    new_students = request.POST.getlist('student')

    period=Class.objects.raw('SELECT * FROM Class WHERE cId=%s',[cId])
    period=period[0].periods

    for i in new_students:
        # pdb.set_trace()
        latest_id = Enrolled.objects.latest('eId')
        latest_id = latest_id.eId
        latest_id=latest_id + 1

        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO Enrolled VALUES (%s, %s, %s, %s,%s)', (latest_id,cId,i,"-",period))

    return redirect('/')#back to homepage

def delete_enrolled_student(request,sId,cId):

    Enrolled.objects.filter(sId_id=sId, cId_id=cId).delete()

    class_detail=f'/class_detail/{cId}'
    return redirect(class_detail)#back to previous page

def delete_enrolled_student_from_class_detail(request,cId):
    student_to_delete = request.POST.getlist('enrolled_student')


    for i in student_to_delete:
        Enrolled.objects.filter(sId_id=i, cId_id=cId).delete()

    class_detail = f'/class_detail/{cId}'
    return redirect(class_detail)  # back to previous page


def edit_student_status(request,sId,cId):

    remark = Enrolled.objects.raw('SELECT * FROM Enrolled WHERE sId_id=%s AND cId_id=%s',[sId,cId])

    return render(request, 'edit_student_status.html',{'remark':remark[0]})

def edit_student_status_action(request,sId,cId):
    remark = request.POST['remark']

    with connection.cursor() as cursor:
        cursor.execute('UPDATE Enrolled SET remark=%s WHERE cId_id=%s AND sId_id=%s', (remark, cId, sId))

    class_detail = f'/class_detail/{cId}'
    return redirect(class_detail)  # back to homepage

def upload_payment(request,eId):
    students=Class.objects.raw('''SELECT name,cId,category,subject,eId,sId
                                    FROM Students,Enrolled,Class 
                                    Where Students.sId=Enrolled.sId_id 
                                    AND Enrolled.cId_id=Class.cId 
                                    AND Enrolled.eId=%s
                                  ''',[eId])
    return render(request, 'upload_payment.html',{'student':students[0]})

def upload_payment_action(request,eId,sId,cId):
    amount=request.POST['amount'];
    date=request.POST['date'];

    if request.method == 'POST' and request.FILES['receipt']:
        file = request.FILES['receipt']
        # 設置文件上傳的目錄
        upload_dir = 'my_app/static/img/receipt/'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        # 構造新的文件路徑，將文件名更改為 "xxx"

        new_file_path = f'{upload_dir}{1}_receipt.pdf'
        # 寫入文件到指定目錄
        with open(new_file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Payment (eId_id,cId_id,sId_id,date,amount) VALUES  (%s,%s,%s,%s,%s)', (eId, cId, sId,date,amount))

    previous_page = f'/student_detail/{sId}'
    return redirect(previous_page)#back to homepage

def add_student(request):
    return render(request, 'add_student.html')

def add_student_action(request):
    name=request.POST['name']
    hp=request.POST['hp']
    parent_name=request.POST['parent_name']
    parent_hp=request.POST['parent_hp']
    years_old=request.POST['years_old']
    school=request.POST['school']
    birthday=request.POST['birthday']
    address=request.POST['address']
    remarks=request.POST['remarks']

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Students (name,hp,parent_name,parent_hp, years_old,school,birthday,address,remarks) VALUES  (%s,%s,%s,%s,%s,%s,%s,%s,%s)', (name,hp,parent_name,parent_hp, years_old,school,birthday,address,remarks))

    student_list_page='/student_list'
    return  redirect(student_list_page)#back to homepage

def edit_student(request,sId):
    Student = Students.objects.raw('Select * FROM Students WHERE sId=%s',[sId])

    return render(request, 'edit_student.html',{'student':Student[0]})

def edit_student_action(request,sId):
    name=request.POST['name']
    hp=request.POST['hp']
    parent_name=request.POST['parent_name']
    parent_hp=request.POST['parent_hp']
    years_old=request.POST['years_old']
    school=request.POST['school']
    birthday=request.POST['birthday']
    address=request.POST['address']
    remarks=request.POST['remarks']

    with connection.cursor() as cursor:
        cursor.execute('UPDATE Students SET name=%s,hp=%s,parent_name=%s,parent_hp=%s,years_old=%s,school=%s,birthday=%s,address=%s,remarks=%s WHERE sId=%s',(name, hp, parent_name, parent_hp, years_old, school, birthday, address, remarks,sId))

    student_detail=f'/student_detail/{sId}'
    return redirect(student_detail)#back to homepage


