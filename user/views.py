from rest_framework.views import APIView
from rest_framework.response import Response  # Corrected import
from .models import User
from django.http import Http404

class QueryUser(APIView):
    @staticmethod
    def get(request):
        req = request.GET.dict()  # Corrected to use request.GET
        user_id = req.get("user_id")  # Use get() to safely access dictionary keys
        if not user_id:
            raise Http404("User ID is required")

        user_pswd = User.objects.filter(user_id=user_id).values_list('user_pswd', flat=True).first()
        if user_pswd is None:
            raise Http404("User not found")

        return Response({'user_pswd': user_pswd})
    
    @staticmethod
    def post(request):


        req = request.data
        user_id = req.get("user_id")
        user_pswd = req.get("user_pswd")
        user = User(user_id=user_id, user_pswd=user_pswd)
        user.save()

        # For now, just return a success response
        return Response()
