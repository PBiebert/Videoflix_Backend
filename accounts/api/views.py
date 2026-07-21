import django_rq
from django.contrib.auth.forms import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from accounts.api.serializers import RegistrationSerializer
from accounts.api.services import send_activation_email


class RegisterView(APIView):

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_url = request.build_absolute_uri(f"/api/activate/{uidb64}/{token}/")
        django_rq.enqueue(send_activation_email, user, activation_url)

        return Response(
            {"user": {"id": user.id, "email": user.email}, "token": token},
            status=HTTP_201_CREATED,
        )
