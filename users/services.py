import boto3
import imghdr
from django.views.decorators.http import require_POST
import redis
# from .upload import upload_profilenew
"""Include all services files"""

# s3=boto3.client('s3')  # Connection for S3


@require_POST
def upload_profilenew(request):
    res = {}
    try:
        if request.FILES['pic']:
            file = request.FILES['pic']  # Uploading a Pic
            print("Name of a File",file)
            tag_file= request.POST.get('email')
            valid_image=imghdr.what(file)
            print("Image Extension",valid_image)
            if valid_image:
                key = tag_file
                s3.upload_fileobj(file, 'fundoobucket', Key=key)
                res['message'] = "Sucessfully Uploaded the Image"
                res['Sucess'] = True
                return JsonResponse(res, status=200)
            else:
                res['message'] = "Invalid Image File Uploaded"
                res['Sucess'] = False
                return JsonResponse(res, status=404)
        else:
            res['message'] = "Please select a valid file"
            res['Sucess'] = False
            return JsonResponse(res, status=404)
    except MultiValueDictKeyError:
        res['message'] = "Select a Valid File"
        res['Sucess'] = False
        return JsonResponse(res,status=404)
    except Exception as e:
        print(e)
        return json()


r=redis.StrictRedis(host='localhost',port=6379, db=0)
class redis_information:
    def set_token(self,key,value):
        r.set(key,value)

    def get_token(self,key):
        value=r.get(key)
        return value

