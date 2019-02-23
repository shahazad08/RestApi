import boto3
from django.utils.datastructures import MultiValueDictKeyError
from django.http import HttpResponse
from django.views.decorators.http import require_POST
s3 = boto3.client('s3')
@require_POST

def upload_profilenew(request):
      # Using to write software that makes use of Amazon services like S3 and EC2.

    try:
        file = request.FILES['pic']  # Uploading a Pic
        email = request.POST.get('email')
        key = email + '.jpeg' or email + '.png'  # storing in a key



        profilePath = s3.upload_fileobj(file, 'fundoobucket', Key=key) # Upload in a s3 bucket
        return profilePath

    except MultiValueDictKeyError:
        messages.error(request, "Please select valid file")  # if Not display the error
        return HttpResponse(request, 'profile.html')  # return
    except Exception as e:
        print(e)
        return json()
        #return render(request, 'home.html')  # return Home Page
    # else:
    #     # return HttpResponse("Not a Valid")  # Get
    #     # messages.error(request, "Please select valid file")  # if Not display the error
    #     return render(request, 'profile.html')