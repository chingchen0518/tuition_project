"""
URL configuration for tuition_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
import my_app.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',my_app.views.homepage, name='homepage'),

    #學生相關
    path('student_list', my_app.views.student_list, name='student_list'),
    path('student_detail/<int:sId>', my_app.views.student_detail, name='student_detail'),

    #課程相關
    path('class_list', my_app.views.class_list, name='class_list'),
    path('class_detail/<int:cId>', my_app.views.class_detail, name='class_detail'),

    path('add_class', my_app.views.add_class, name='add_class'),
    path('add_class_action', my_app.views.add_class_action, name='add_class_action'),
    path('edit_class/<int:cId>', my_app.views.edit_class, name='edit_class'),
    path('edit_class_action/<int:cId>', my_app.views.edit_class_action, name='edit_class_action'),

    path('add_teacher', my_app.views.add_teacher, name='add_teacher'),
    path('add_teacher_action', my_app.views.add_teacher_action, name='add_teacher_action'),
    
    path('add_category', my_app.views.add_category, name='add_category'),
    path('add_category_action', my_app.views.add_category_action, name='add_category_action'),

    path('add_enroll/<int:cId>', my_app.views.add_enroll, name='add_enroll'),
    path('add_enroll_action/<int:cId>', my_app.views.add_enroll_action, name='add_enroll_action'),
    path('delete_enrolled_student/<int:sId>/<int:cId>', my_app.views.delete_enrolled_student, name='delete_enrolled_student'),


]
