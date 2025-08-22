from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import MeSerializer, BuddySerializer, LocationSerializer
from .models import Buddy, Location

@api_view(['GET'])
def ping(request):
    return Response({"message": "pong"})

@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    if request.method == "GET":
        return Response(MeSerializer(user).data)
    serializer = MeSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def buddies(request):
    if request.method == "GET":
        links = Buddy.objects.filter(user=request.user).select_related("buddy").order_by("-created_at")
        return Response(BuddySerializer(links, many=True).data)

    friend_username = request.data.get("username")
    if not friend_username:
        return Response({"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST)
    if friend_username == request.user.username:
        return Response({"detail": "cannot add yourself"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        friend = User.objects.get(username=friend_username)
    except User.DoesNotExist:
        return Response({"detail": "user not found"}, status=status.HTTP_404_NOT_FOUND)

    obj, created = Buddy.objects.get_or_create(user=request.user, buddy=friend)
    if not created:
        return Response({"detail": "already a buddy"}, status=status.HTTP_200_OK)
    return Response(BuddySerializer(obj).data, status=status.HTTP_201_CREATED)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def buddy_delete(request, username):
    deleted, _ = Buddy.objects.filter(user=request.user, buddy__username=username).delete()
    if deleted == 0:
        return Response({"detail": "not a buddy"}, status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_204_NO_CONTENT)

def _is_buddy(viewer, target):
    return Buddy.objects.filter(user=viewer, buddy=target).exists()

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def location_update(request):
    data = {
        "latitude": request.data.get("latitude"),
        "longitude": request.data.get("longitude"),
        "accuracy": request.data.get("accuracy"),
        "heading": request.data.get("heading"),
        "speed": request.data.get("speed"),
    }
    if data["latitude"] is None or data["longitude"] is None:
        return Response({"detail": "latitude and longitude are required"}, status=status.HTTP_400_BAD_REQUEST)
    obj, _ = Location.objects.update_or_create(user=request.user, defaults=data)
    return Response(LocationSerializer(obj).data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def location_of(request, username):
    try:
        target = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"detail": "user not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user != target and not _is_buddy(request.user, target):
        return Response({"detail": "not your buddy"}, status=status.HTTP_403_FORBIDDEN)

    loc = getattr(target, "location", None)
    if not loc:
        return Response({"detail": "no location yet"}, status=status.HTTP_404_NOT_FOUND)
    return Response(LocationSerializer(loc).data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def buddies_locations(request):
    buddy_users = User.objects.filter(follower_links__user=request.user)
    qs = Location.objects.filter(user__in=buddy_users).select_related("user").order_by("-updated_at")
    return Response(LocationSerializer(qs, many=True).data, status=status.HTTP_200_OK)
