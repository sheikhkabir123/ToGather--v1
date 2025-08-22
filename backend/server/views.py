from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import MeSerializer, BuddySerializer , LocationSerializer , EventSerializer
from .models import Buddy , Location ,Event , Attendance

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

from .models import Buddy, Location
from .serializers import LocationSerializer

def _is_buddy(viewer, target):
    return Buddy.objects.filter(user=viewer, buddy=target).exists()

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def location_update(request):
    """
    POST body:
    {
      "latitude": 12.345678,
      "longitude": 98.765432,
      "accuracy": 7.2,      # optional
      "heading": 180,       # optional
      "speed": 0.5          # optional
    }
    """
    user = request.user
    data = {
        "latitude": request.data.get("latitude"),
        "longitude": request.data.get("longitude"),
        "accuracy": request.data.get("accuracy"),
        "heading": request.data.get("heading"),
        "speed": request.data.get("speed"),
    }
    if data["latitude"] is None or data["longitude"] is None:
        return Response({"detail": "latitude and longitude are required"}, status=status.HTTP_400_BAD_REQUEST)

    # upsert latest location for this user
    obj, created = Location.objects.update_or_create(
        user=user,
        defaults=data
    )
    return Response(LocationSerializer(obj).data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def location_of(request, username):
    """
    Get a buddy's latest location by username (requires you follow them)
    """
    try:
        target = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"detail": "user not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user == target:
        # You can always see your own
        loc = getattr(target, "location", None)
        if not loc:
            return Response({"detail": "no location yet"}, status=status.HTTP_404_NOT_FOUND)
        return Response(LocationSerializer(loc).data)

    if not _is_buddy(request.user, target):
        return Response({"detail": "not your buddy"}, status=status.HTTP_403_FORBIDDEN)

    loc = getattr(target, "location", None)
    if not loc:
        return Response({"detail": "no location yet"}, status=status.HTTP_404_NOT_FOUND)
    return Response(LocationSerializer(loc).data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def buddies_locations(request):
    """
    List locations of all buddies you follow (only those who have posted).
    """
    buddy_ids = Buddy.objects.filter(user=request.user).values_list("buddy_id", flat=True)
    qs = Location.objects.filter(user_id__in=buddy_ids).select_related("user").order_by("-updated_at")
    return Response(LocationSerializer(qs, many=True).data)
from django.utils import timezone
from django.db.models import Q
from .models import Event, Attendance

def _creator_followers_qs(creator):
    # Users who follow "creator": Buddy(user=follower, buddy=creator)
    from .models import Buddy
    return Buddy.objects.filter(buddy=creator).values_list("user_id", flat=True)

def _visible_to(user):
    # Events the viewer can see:
    # - public events
    # - their own events
    # - buddies-visibility events by creators whom the viewer follows (Buddy.user=viewer, buddy=creator)
    from .models import Buddy
    creators_i_follow = Buddy.objects.filter(user=user).values_list("buddy_id", flat=True)
    return Q(visibility="public") | Q(creator=user) | (Q(visibility="buddies") & Q(creator_id__in=creators_i_follow))

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def events_feed(request):
    # simple feed: upcoming first, then recent
    now = timezone.now()
    qs = Event.objects.filter(_visible_to(request.user)).order_by("starts_at")
    ser = EventSerializer(qs, many=True, context={"request": request})
    return Response(ser.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def events_create(request):
    # Minimal required: title, starts_at (ISO), optional others
    data = {
        "title": request.data.get("title"),
        "description": request.data.get("description"),
        "starts_at": request.data.get("starts_at"),
        "ends_at": request.data.get("ends_at"),
        "place_name": request.data.get("place_name"),
        "latitude": request.data.get("latitude"),
        "longitude": request.data.get("longitude"),
        "visibility": request.data.get("visibility", "buddies"),
    }
    if not data["title"] or not data["starts_at"]:
        return Response({"detail": "title and starts_at are required"}, status=400)
    event = Event.objects.create(creator=request.user, **{k: v for k, v in data.items() if v is not None})
    # auto-join creator
    Attendance.objects.get_or_create(event=event, user=request.user)
    return Response(EventSerializer(event, context={"request": request}).data, status=201)

def _can_view_event(user, event: Event):
    if event.visibility == "public":
        return True
    if event.creator_id == user.id:
        return True
    if event.visibility == "buddies":
        from .models import Buddy
        return Buddy.objects.filter(user=user, buddy=event.creator).exists()
    return False  # private

@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def event_detail(request, event_id: int):
    try:
        ev = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"detail": "not found"}, status=404)

    if request.method == "GET":
        if not _can_view_event(request.user, ev):
            return Response({"detail": "forbidden"}, status=403)
        return Response(EventSerializer(ev, context={"request": request}).data)

    if request.method == "PATCH":
        if ev.creator_id != request.user.id:
            return Response({"detail": "only creator can edit"}, status=403)
        allowed = {"title", "description", "starts_at", "ends_at", "place_name", "latitude", "longitude", "visibility"}
        for k, v in request.data.items():
            if k in allowed:
                setattr(ev, k, v)
        ev.save()
        return Response(EventSerializer(ev, context={"request": request}).data)

    # DELETE
    if ev.creator_id != request.user.id:
        return Response({"detail": "only creator can delete"}, status=403)
    ev.delete()
    return Response(status=204)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def event_join(request, event_id: int):
    try:
        ev = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"detail": "not found"}, status=404)
    if not _can_view_event(request.user, ev):
        return Response({"detail": "forbidden"}, status=403)
    Attendance.objects.get_or_create(event=ev, user=request.user)
    return Response({"detail": "joined"}, status=200)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def event_leave(request, event_id: int):
    try:
        ev = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"detail": "not found"}, status=404)
    Attendance.objects.filter(event=ev, user=request.user).delete()
    return Response(status=204)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_events(request):
    qs = Event.objects.filter(creator=request.user).order_by("-created_at")
    return Response(EventSerializer(qs, many=True, context={"request": request}).data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_attending(request):
    qs = Event.objects.filter(attendances__user=request.user).order_by("starts_at").distinct()
    return Response(EventSerializer(qs, many=True, context={"request": request}).data)
from rest_framework.permissions import IsAuthenticated, AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def ping(request):
    return Response({"message": "pong"})
# --- Events API ---
from django.utils import timezone
from django.db.models import Q
from .models import Event, Attendance, Buddy
from .serializers import EventSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

def _visible_to(user):
    creators_i_follow = Buddy.objects.filter(user=user).values_list("buddy_id", flat=True)
    return Q(visibility="public") | Q(creator=user) | (Q(visibility="buddies") & Q(creator_id__in=creators_i_follow))

def _can_view_event(user, event: Event):
    if event.visibility == "public": return True
    if event.creator_id == user.id: return True
    if event.visibility == "buddies":
        return Buddy.objects.filter(user=user, buddy=event.creator).exists()
    return False

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def events_feed(request):
    qs = Event.objects.filter(_visible_to(request.user)).order_by("starts_at")
    return Response(EventSerializer(qs, many=True, context={"request": request}).data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def events_create(request):
    data = {
        "title": request.data.get("title"),
        "description": request.data.get("description"),
        "starts_at": request.data.get("starts_at"),
        "ends_at": request.data.get("ends_at"),
        "place_name": request.data.get("place_name"),
        "latitude": request.data.get("latitude"),
        "longitude": request.data.get("longitude"),
        "visibility": request.data.get("visibility", "buddies"),
    }
    if not data["title"] or not data["starts_at"]:
        return Response({"detail": "title and starts_at are required"}, status=400)
    ev = Event.objects.create(creator=request.user, **{k: v for k, v in data.items() if v is not None})
    Attendance.objects.get_or_create(event=ev, user=request.user)  # creator joins
    return Response(EventSerializer(ev, context={"request": request}).data, status=201)

@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def event_detail(request, event_id: int):
    try:
        ev = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"detail": "not found"}, status=404)

    if request.method == "GET":
        if not _can_view_event(request.user, ev):
            return Response({"detail": "forbidden"}, status=403)
        return Response(EventSerializer(ev, context={"request": request}).data)

    if request.method == "PATCH":
        if ev.creator_id != request.user.id:
            return Response({"detail": "only creator can edit"}, status=403)
        allowed = {"title","description","starts_at","ends_at","place_name","latitude","longitude","visibility"}
        for k, v in request.data.items():
            if k in allowed:
                setattr(ev, k, v)
        ev.save()
        return Response(EventSerializer(ev, context={"request": request}).data)

    # DELETE
    if ev.creator_id != request.user.id:
        return Response({"detail": "only creator can delete"}, status=403)
    ev.delete()
    return Response(status=204)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def event_join(request, event_id: int):
    try:
        ev = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"detail": "not found"}, status=404)
    if not _can_view_event(request.user, ev):
        return Response({"detail": "forbidden"}, status=403)
    Attendance.objects.get_or_create(event=ev, user=request.user)
    return Response({"detail": "joined"}, status=200)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def event_leave(request, event_id: int):
    try:
        ev = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"detail": "not found"}, status=404)
    Attendance.objects.filter(event=ev, user=request.user).delete()
    return Response(status=204)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_events(request):
    qs = Event.objects.filter(creator=request.user).order_by("-created_at")
    return Response(EventSerializer(qs, many=True, context={"request": request}).data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_attending(request):
    qs = Event.objects.filter(attendances__user=request.user).order_by("starts_at").distinct()
    return Response(EventSerializer(qs, many=True, context={"request": request}).data)
# --- Events API ---
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Event, Attendance, Buddy
from .serializers import EventSerializer

def _visible_to(user):
    creators_i_follow = Buddy.objects.filter(user=user).values_list("buddy_id", flat=True)
    return Q(visibility="public") | Q(creator=user) | (Q(visibility="buddies") & Q(creator_id__in=creators_i_follow))

def _can_view_event(user, event: Event):
    if event.visibility == "public":
        return True
    if event.creator_id == user.id:
        return True
    if event.visibility == "buddies":
        return Buddy.objects.filter(user=user, buddy=event.creator).exists()
    return False

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def events_feed(request):
    qs = Event.objects.filter(_visible_to(request.user)).order_by("starts_at")
    return Response(EventSerializer(qs, many=True, context={"request": request}).data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def events_create(request):
    data = {
        "title": request.data.get("title"),
        "description": request.data.get("description"),
        "starts_at": request.data.get("starts_at"),
        "ends_at": request.data.get("ends_at"),
        "place_name": request.data.get("place_name"),
        "latitude": request.data.get("latitude"),
        "longitude": request.data.get("longitude"),
        "visibility": request.data.get("visibility", "buddies"),
    }
    if not data["title"] or not data["starts_at"]:
        return Response({"detail": "title and starts_at are required"}, status=400)
    ev = Event.objects.create(creator=request.user, **{k: v for k, v in data.items() if v is not None})
    Attendance.objects.get_or_create(event=ev, user=request.user)  # auto-join creator
    return Response(EventSerializer(ev, context={"request": request}).data, status=201)

@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def event_detail(request, event_id: int):
    try:
        ev = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"detail": "not found"}, status=404)

    if request.method == "GET":
        if not _can_view_event(request.user, ev):
            return Response({"detail": "forbidden"}, status=403)
        return Response(EventSerializer(ev, context={"request": request}).data)

    if request.method == "PATCH":
        if ev.creator_id != request.user.id:
            return Response({"detail": "only creator can edit"}, status=403)
        allowed = {"title","description","starts_at","ends_at","place_name","latitude","longitude","visibility"}
        for k, v in request.data.items():
            if k in allowed:
                setattr(ev, k, v)
        ev.save()
        return Response(EventSerializer(ev, context={"request": request}).data)

    # DELETE
    if ev.creator_id != request.user.id:
        return Response({"detail": "only creator can delete"}, status=403)
    ev.delete()
    return Response(status=204)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def event_join(request, event_id: int):
    try:
        ev = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"detail": "not found"}, status=404)
    if not _can_view_event(request.user, ev):
        return Response({"detail": "forbidden"}, status=403)
    Attendance.objects.get_or_create(event=ev, user=request.user)
    return Response({"detail": "joined"}, status=200)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def event_leave(request, event_id: int):
    try:
        ev = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"detail": "not found"}, status=404)
    Attendance.objects.filter(event=ev, user=request.user).delete()
    return Response(status=204)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_events(request):
    qs = Event.objects.filter(creator=request.user).order_by("-created_at")
    return Response(EventSerializer(qs, many=True, context={"request": request}).data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_attending(request):
    qs = Event.objects.filter(attendances__user=request.user).order_by("starts_at").distinct()
    return Response(EventSerializer(qs, many=True, context={"request": request}).data)
