from django.shortcuts import HttpResponse, render, redirect
import json,os
from django.db.models import Max
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist


from django.http import JsonResponse
from django.db import connection
from django.shortcuts import render

from django.shortcuts import render
import hashlib

#include table
from my_app.models import Students, Enrolled, Class, Classroom, Teacher, Category, Payment, Time, Account
from my_app.models import Semester

# Create your views here.
def homepage(request):
    class_list = Class.objects.raw('''SELECT DISTINCT cId,time,years_old,subject,category,day,available,start
                                        FROM Class JOIN Time ON Class.time=Time.start
                                        WHERE available=1
                                        ORDER BY time''')

    classroom=[1,2,3,4,5,6]
    Days=['一','二','三','四','五','六','日']

    time = Time.objects.raw('SELECT * FROM Time WHERE semId_id=(SELECT MAX(semId) FROM Semester) ORDER BY sequence')
    return render(request, 'homepage.html',{'class':class_list,'Days':Days,'time':time,'classroom':classroom})


def student_list(request):
    student_list = Students.objects.raw('''SELECT *,
                                            CASE 
                                                WHEN EXISTS (SELECT eId,period,COUNT(amount) AS paid_period,
                                                          CASE WHEN (COUNT(amount)>=period) THEN 1
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
                                        FROM Students s ORDER BY years_old''')

    tingkat = ['xxx','國一','國二','國三','高一','高二','高三']

    return render(request, 'student_list.html',{'student_list':student_list,'tingkat':tingkat})

def student_detail(request,sId):
    student_detail = Students.objects.raw('''SELECT * FROM Students WHERE sId=%s''',[sId])
    tingkat = ['xxx','國一','國二','國三','高一','高二','高三']
    class_taken= Class.objects.raw('''SELECT year,eId,cId,day,time,remark,period,subject,category,Enrolled.cId_id,
                                        CASE
                                            WHEN (SELECT COUNT(amount) AS payment FROM Payment WHERE sId_id=%s AND Payment.eId_id=Enrolled.eId) > 0 THEN (SELECT COUNT(amount) FROM Payment WHERE sId_id=%s AND Payment.eId_id=Enrolled.eId)
                                            ELSE 0
                                        END AS payment
                                        FROM Enrolled
                                        JOIN Class ON Class.cId = Enrolled.cId_id
                                        WHERE Enrolled.sId_id = %s
                                        ''',(sId,sId,sId))

    return render(request, 'student_detail.html',{'student_detail': student_detail[0],'tingkat':tingkat,'class_taken':class_taken})

def class_list(request,available):

    class_list = Teacher.objects.raw('''SELECT Class.*, Teacher.*,Semester.*, COALESCE(enrolled_counts.tuple_count, 0) AS student_count,Class.quota - COALESCE(enrolled_counts.tuple_count, 0) AS remain
                                        FROM Class LEFT JOIN Teacher ON Class.tId_id = Teacher.tId
                                        LEFT JOIN (SELECT cId_id, COUNT(*) AS tuple_count FROM Enrolled GROUP BY cId_id
                                        ) AS enrolled_counts ON enrolled_counts.cId_id = Class.cId 
                                        JOIN Semester ON Semester.semId=Class.year 
                                        WHERE available=%s
                                        ORDER BY year DESC,
                                                CASE day
                                                    WHEN '一' THEN 1
                                                    WHEN '二' THEN 2
                                                    WHEN '三' THEN 3
                                                    WHEN '四' THEN 4
                                                    WHEN '五' THEN 5
                                                    WHEN '六' THEN 6
                                                    ELSE 7
                                                END,time
                                        ;''',[available])

    semester = Semester.objects.raw('SELECT * FROM Semester ORDER BY semId DESC')

    return render(request, 'class_list_table.html', {'class_list': class_list, 'available':available,'semester':semester})

def class_detail(request,cId):
    class_detail = Teacher.objects.raw('''SELECT Class.*, Teacher.*,Classroom.classroom_name, COALESCE(enrolled_counts.tuple_count, 0) AS student_count,Class.quota - COALESCE(enrolled_counts.tuple_count, 0) AS remain
                                            FROM Class LEFT JOIN Teacher ON Class.tId_id = Teacher.tId
                                            LEFT JOIN (SELECT cId_id, COUNT(*) AS tuple_count FROM Enrolled GROUP BY cId_id
                                            ) AS enrolled_counts ON enrolled_counts.cId_id = Class.cId JOIN Classroom ON Classroom.crId=Class.crId_id WHERE Class.cId=%s''',[cId])

    students = Students.objects.raw('SELECT * FROM Students,Enrolled WHERE Enrolled.sId_id=Students.sId AND Enrolled.cId_id=%s',[cId])
    return render(request, 'class_detail.html',{'class_detail': class_detail[0],'students':students})

def add_category(request):
    if 'login' in request.session and request.session['login'] == 1:
        if 'permission' in request.session and request.session['permission'] == 1:
            category = Category.objects.raw('SELECT * FROM Category')

            return render(request, 'add_category.html',{'category':category})
        else:
            return render(request, 'no_access.html')
    else:
        return render(request, 'no_access.html')

def add_category_action(request):
    category = request.POST['category']

    try:
        latest_id = Category.objects.latest('catId')
        latest_id = latest_id.catId
        latest_id = latest_id + 1
    except ObjectDoesNotExist:
        latest_id=0

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Category VALUES (%s, %s)', (latest_id, category))

    add_category=f'/add_category'
    return redirect(add_category)  # back to homepage

def delete_category_action(request,catId):
    Category.objects.filter(catId=catId).delete()

    add_category=f'/add_category'
    return redirect(add_category)  # back to homepage

def add_class(request):
    category = Category.objects.raw('SELECT * FROM Category')
    teacher = Teacher.objects.raw('SELECT tId,teacher_name FROM Teacher')
    classroom = Classroom.objects.raw('SELECT * FROM Classroom')

    time = Time.objects.raw('SELECT * FROM Time WHERE semId_id=(SELECT MAX(semId) FROM Semester) ORDER BY start')
    year = Semester.objects.raw('SELECT * FROM Semester WHERE semId=(SELECT MAX(semId) FROM Semester)')

    if 'login' in request.session and request.session['login'] == 1:
        if 'permission' in request.session and request.session['permission'] == 1:
            return render(request, 'add_class.html',
                          {'categories': category, 'teachers': teacher, 'classrooms': classroom, 'time': time,
                           'years': year[0]})
        else:
            return render(request, 'no_access.html')
    else:
        return render(request, 'no_access.html')


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
    try:
        latest_id = Class.objects.latest('cId')
        latest_id = latest_id.cId
        cId = latest_id + 1
    except ObjectDoesNotExist:
        cId = 0


    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Class VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)', (cId,category,subject,time,year,quota,classroom,teacher,day,years_old,class_period,1))

    return redirect('/class_list/1')#back to homepage

def edit_class(request,cId):
    class_detail = Class.objects.raw('SELECT * FROM Class WHERE cId=%s',[cId])
    category = Category.objects.raw('SELECT * FROM Category')
    teacher = Teacher.objects.raw('SELECT * FROM Teacher')
    classroom = Classroom.objects.raw('SELECT * FROM Classroom')

    class_year = Class.objects.raw('SELECT * FROM Class WHERE cId=%s',[cId])[0].year

    time = Time.objects.raw('SELECT * FROM Time WHERE semId_id=%s ORDER BY start',[class_year])

    year = Semester.objects.raw('SELECT * FROM Semester WHERE semId=%s',[class_year])

    return render(request, 'edit_class.html',{'class_detail':class_detail[0],'categories':category,'teachers':teacher,'classrooms':classroom,'time':time,'years':year[0]})

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
    class_period = request.POST['class_period']

    with connection.cursor() as cursor:
        cursor.execute('UPDATE Class SET category=%s, subject=%s, time=%s, year=%s, quota=%s, crId_id=%s, tId_id=%s, day=%s, years_old=%s,periods=%s WHERE cId=%s', (category,subject,time,year,quota,classroom,teacher,day,years_old,class_period,cId,))

    class_detail = f'/class_detail/{cId}'

    return redirect(class_detail)#back to homepage

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

def copy_class(request,cId):
    class_detail = Class.objects.raw('SELECT * FROM Class WHERE cId=%s', [cId])
    category = Category.objects.raw('SELECT * FROM Category')
    teacher = Teacher.objects.raw('SELECT * FROM Teacher')
    classroom = Classroom.objects.raw('SELECT * FROM Classroom')

    time = Time.objects.raw('SELECT * FROM Time WHERE semId_id=(SELECT MAX(semId) FROM Semester) ORDER BY sequence')
    year = Semester.objects.raw('SELECT * FROM Semester ORDER BY semId DESC')

    return render(request, 'copy_class.html',
                  {'class_detail': class_detail[0], 'categories': category, 'teachers': teacher,
                   'classrooms': classroom, 'time': time, 'years': year[0]})

def copy_class_action(request):
    category = request.POST['category']
    subject = request.POST['subject']
    time = request.POST['time']
    year = request.POST['year']
    quota = request.POST['quota']
    classroom = request.POST['classroom']
    teacher = request.POST['teacher']
    day = request.POST['day']
    years_old = request.POST['age']
    class_period = request.POST['class_period']

    try:
        latest_id = Class.objects.latest('cId')
        latest_id = latest_id.cId
        cId = latest_id + 1
    except ObjectDoesNotExist:
        cId = 0


    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Class VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)', (cId,category,subject,time,year,quota,classroom,teacher,day,years_old,class_period,1))

    class_detail = f'/class_detail/{cId}'

    return redirect(class_detail)  # back to homepaged


def add_teacher(request):
    if 'login' in request.session and request.session['login'] == 1:
        if 'permission' in request.session and request.session['permission'] == 1:
            teacher = Teacher.objects.raw('SELECT * FROM Teacher')

            return render(request, 'add_teacher.html',{'teacher':teacher})
        else:
            return render(request, 'no_access.html')
    else:
        return render(request, 'no_access.html')

def add_teacher_action(request):
    name = request.POST['name']
    phone = request.POST['phone']
    line = request.POST['line']
    try:
        latest_id = Teacher.objects.latest('tId')
        latest_id = latest_id.tId
        latest_id = latest_id + 1
    except ObjectDoesNotExist:
        latest_id = 0

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Teacher VALUES (%s, %s, %s, %s)', (latest_id,name,line,phone))

    add_teacher=f'/add_teacher'
    return redirect(add_teacher)#back to homepage

def delete_teacher_action(request,tId):

    Teacher.objects.filter(tId=tId).delete()

    add_teacher=f'/add_teacher'
    return redirect(add_teacher)#back to homepage


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
        try:
            latest_id = Enrolled.objects.latest('eId')
            latest_id = latest_id.eId
            latest_id = latest_id + 1
        except ObjectDoesNotExist:
            latest_id = 0

        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO Enrolled VALUES (%s, %s, %s, %s,%s)', (latest_id,cId,i,"-",period))

    class_detail=f'/class_detail/{cId}'

    return redirect(class_detail)#back to homepage

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

def get_file_extension(uploaded_file):
    filename, file_extension = os.path.splitext(uploaded_file.name)
    return file_extension.lower()

def upload_payment_action(request,eId,sId,cId):
    amount=request.POST['amount'];
    date=request.POST['date'];


    if request.method == 'POST' and request.FILES['receipt']:
        file = request.FILES['receipt']
        file_extension=get_file_extension(file)

        # 看這堂課有幾個payment
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(amount) AS num FROM Payment WHERE Payment.sId_id=%s AND Payment.eId_id=%s',(sId,eId))
            latest_payment = cursor.fetchall()
            latest_payment = latest_payment[0][0]+1

        # 看學生名字
        students = Students.objects.raw('SELECT sId,name FROM Students WHERE sId=%s',[sId])
        student_name = students[0].name

        # 看課程名字
        class_detail = Class.objects.filter(cId=cId).values('cId', 'subject', 'year')
        semester=class_detail[0]['year']
        class_name = class_detail[0]['subject']

        # 設置文件上傳的目錄
        upload_dir = 'my_app/static/img/receipt/'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        # 構造新的文件路徑，將文件名更改為 "xxx"

        new_file_path = f'{upload_dir}{student_name}_{class_name}({semester})_{latest_payment}{file_extension}'
        # 寫入文件到指定目錄
        with open(new_file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO Payment (eId_id,cId_id,sId_id,date,amount) VALUES  (%s,%s,%s,%s,%s)', (eId, cId, sId,date,amount))

    previous_page = f'/student_detail/{sId}'
    return redirect(previous_page)#back to homepage

def add_student(request):
    if 'login' in request.session and request.session['login'] == 1:
        if 'permission' in request.session and request.session['permission'] == 1:

            return render(request, 'add_student.html')
        else:
            return render(request, 'no_access.html')
    else:
        return render(request, 'no_access.html')

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
    if 'login' in request.session and request.session['login'] == 1:
        if 'permission' in request.session and request.session['permission'] == 1:
            Student = Students.objects.raw('Select * FROM Students WHERE sId=%s',[sId])

            return render(request, 'edit_student.html',{'student':Student[0]})
        else:
            return render(request, 'no_access.html')
    else:
        return render(request, 'no_access.html')

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

def add_time(request):
    if 'login' in request.session and request.session['login'] == 1:
        if 'permission' in request.session and request.session['permission'] == 1:
            years=Semester.objects.raw('SELECT * FROM Semester ORDER BY semId DESC')
            time = Time.objects.raw('SELECT * FROM Time WHERE semId_id=(SELECT MAX(semId) FROM Semester) ORDER BY start')

            return render(request, 'add_time.html',{'years':years[0],'time':time})
        else:
            return render(request, 'no_access.html')
    else:
        return render(request, 'no_access.html')

def add_time_action(request,years):

    start  = request.POST['start']
    start_str = datetime.strptime(start , '%H:%M')

    end_str = start_str + timedelta(hours=2)
    end = end_str.strftime('%H:%M')

    # latest_sequence = Time.objects.raw('SELECT * FROM Time WHERE semId_id=%s ORDER BY sequence DESC',[years])[0]
    #
    # if latest_sequence.exists():
    #     next_sequence = latest_sequence.sequence + 1
    # else:

    next_sequence = 1


    latest_timeId = Time.objects.raw('SELECT * FROM Time ORDER BY tId DESC')[0]
    next_timeId = latest_timeId.tId+1

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Time (tId, sequence, start, end, semId_id) VALUES (%s, %s, %s, %s, %s)',(next_timeId,next_sequence,start,end,years))

    add_time=f'/add_time'
    return redirect(add_time)#back to homepage

def delete_time_action(request,tId):

    Time.objects.filter(tId=tId).delete()

    add_time=f'/add_time'
    return redirect(add_time)#back to homepage
def sem_convert(request):
    if 'login' in request.session and request.session['login'] == 1:
        if 'permission' in request.session and request.session['permission'] == 1:
            years = Semester.objects.raw('SELECT * FROM Semester ORDER BY semId DESC')

            new_year = 0
            if years[0].sem == 4:
                new_year = years[0].semId + 7
            # return render(request, 'sem_convert.html', {'years': years[0]})
            return render(request, 'no_access.html')

        else:
            return render(request, 'no_access.html')
    else:
        return render(request, 'no_access.html')


def sem_convert_action(request):
    semID  = request.POST['next_sem']
    sem = int(semID) % 10
    real_year = int(semID) // 10

    text=['上','寒','下','暑']
    semText = f'{real_year}{text[sem-1]}'

    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO Semester (semID, real_year, sem, semText) VALUES (%s, %s, %s, %s)',(semID, real_year, sem, semText))


    if sem == 4:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE Students SET years_old=years_old+1')

    sem_convert = f'/sem_convert'
    return redirect(sem_convert)#back to homepage

def login_page(request):
    # data="lee123456"
    # a=hashlib.md5(data.encode()).hexdigest()
    #
    # with connection.cursor() as cursor:
    #     cursor.execute('INSERT INTO Account (aId, username, password, permission) VALUES (%s, %s, %s, %s)',(2,'ching2chen',a,1))

    return render(request, 'login_page.html')

def login_page_action(request):
    username = request.POST['username']
    password = request.POST['password']

    hashed_password = hashlib.md5(password.encode()).hexdigest()

    account_data = Account.objects.raw('SELECT * FROM Account WHERE username=%s AND password=%s',[username,hashed_password])

    if account_data:
        request.session['username']=username
        request.session['login'] = 1
        request.session['permission'] = account_data[0].permission

        if 'login' in request.session and request.session['login'] == 1:
            student_list = f'/student_list'
            return redirect(student_list)
        else:
            return redirect('/login_page')


    else:
        return redirect('/login_page')

def logout_action(request):
    request.session.flush()
    return redirect('/')

def add_account(request,repeat):

    if 'login' in request.session and request.session['login'] == 1:
        return render(request, 'no_access.html')
        # return render(request, 'add_account.html',{'repeat':repeat})
    else:
        return render(request, 'no_access.html')


def add_account_action(request):
    username = request.POST['username']
    password = request.POST['password']
    permission = request.POST['permission']

    hashed_password = hashlib.md5(password.encode()).hexdigest()

    # account=Account.objects.raw('SELECT * FROM Account WHERE username=%s',[username])
    account = Account.objects.filter(username=username).exists()

    if account:
        add_account = f'/add_account/1'
        return redirect(add_account)
    else:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO Account (username, password, permission) VALUES (%s, %s, %s)',(username,hashed_password,permission))

        add_account = f'/add_account/2'
        return redirect(add_account)


