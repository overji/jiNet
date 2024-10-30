from django.shortcuts import render

def index(request):
    context = {}
    return render(request,'index.html',context)

def llm(request):
    context = {}
    return render(request,'llm.html',context)
