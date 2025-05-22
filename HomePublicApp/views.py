from django.shortcuts import render

# Create your views here.
def main(request):
    # sleep.delay()
    return render(request, 'main.html')