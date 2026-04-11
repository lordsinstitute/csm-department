from django.shortcuts import render


def basefunction(request):
    return render(request,'base.html')



def demofunction(request):
    return render(request,'demo.html')
