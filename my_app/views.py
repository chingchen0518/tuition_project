from django.shortcuts import render

# Create your views here.
def homepage(request):
    return render(request, 'homepage.html')

def student_list(request):
    return render(request, 'student_list.html')

