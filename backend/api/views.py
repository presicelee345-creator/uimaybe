from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
import hashlib
from .models import User, Session, Progress


# ── helpers ──────────────────────────────────────────────

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(request):
    """Return User from Bearer token, or None."""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        session = Session.objects.select_related('user').get(token=token)
        return session.user
    except Session.DoesNotExist:
        return None

def ok(data):
    return Response({'success': True, **data})

def err(msg, status=400):
    return Response({'success': False, 'error': msg}, status=status)

def user_dict(u):
    return {
        'id': str(u.id),
        'email': u.email,
        'firstName': u.first_name,
        'lastName': u.last_name,
        'role': u.role,
        'selectedTrack': u.selected_track,
    }


# ── auth ─────────────────────────────────────────────────

@api_view(['POST'])
def signup(request):
    d = request.data
    email      = d.get('email', '').strip().lower()
    password   = d.get('password', '')
    first_name = d.get('firstName', '')
    last_name  = d.get('lastName', '')
    role       = d.get('role', 'trainee')

    if not all([email, password, first_name, last_name]):
        return err('All fields are required')

    if User.objects.filter(email=email).exists():
        return err('Email already in use')

    User.objects.create(
        email=email, password=hash_pw(password),
        first_name=first_name, last_name=last_name, role=role
    )
    return ok({'message': 'Account created'})


@api_view(['POST'])
def signin(request):
    email    = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    try:
        user = User.objects.get(email=email, password=hash_pw(password))
    except User.DoesNotExist:
        return err('Invalid email or password', 401)

    session = Session.objects.create(user=user)
    return ok({'accessToken': str(session.token), 'user': user_dict(user)})


@api_view(['GET'])
def get_user_view(request):
    user = get_user(request)
    if not user:
        return err('Unauthorized', 401)
    return ok({'user': user_dict(user)})


@api_view(['POST'])
def signout(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    Session.objects.filter(token=token).delete()
    return ok({})


# ── track ────────────────────────────────────────────────

@api_view(['POST'])
def select_track(request):
    user = get_user(request)
    if not user:
        return err('Unauthorized', 401)

    track_id = request.data.get('trackId')
    if not track_id:
        return err('trackId is required')

    user.selected_track = track_id
    user.save()
    return ok({'trackId': track_id})


@api_view(['GET'])
def get_track(request):
    user = get_user(request)
    if not user:
        return err('Unauthorized', 401)
    return ok({'trackId': user.selected_track})


# ── progress ─────────────────────────────────────────────

@api_view(['GET'])
def get_progress(request, track_id):
    user = get_user(request)
    if not user:
        return err('Unauthorized', 401)

    rows = Progress.objects.filter(user=user, track_id=track_id)

    modules = {}
    total = completed = 0

    for row in rows:
        m, c = row.module_index, row.course_index
        if m not in modules:
            modules[m] = {'courses': {}, 'quizPassed': False, 'quizScore': None, 'quizAttempts': 0}

        if c is not None:
            total += 1
            if row.completed:
                completed += 1
            modules[m]['courses'][c] = {
                'completed': row.completed,
                'completedAt': row.completed_at.isoformat() if row.completed_at else None,
            }
        else:
            modules[m]['quizPassed']   = row.quiz_passed
            modules[m]['quizScore']    = row.quiz_score
            modules[m]['quizAttempts'] = row.quiz_attempts

    overall = int(completed / total * 100) if total else 0
    return ok({'progress': {'modules': modules, 'overallProgress': overall}})


@api_view(['POST'])
def mark_course_complete(request):
    user = get_user(request)
    if not user:
        return err('Unauthorized', 401)

    d = request.data
    row, _ = Progress.objects.get_or_create(
        user=user,
        track_id=d.get('trackId'),
        module_index=d.get('moduleIndex'),
        course_index=d.get('courseIndex'),
    )
    row.completed    = True
    row.completed_at = timezone.now()
    row.save()
    return ok({})


@api_view(['POST'])
def submit_quiz(request):
    user = get_user(request)
    if not user:
        return err('Unauthorized', 401)

    d      = request.data
    score  = float(d.get('score', 0))
    passed = score >= 70

    row, _ = Progress.objects.get_or_create(
        user=user,
        track_id=d.get('trackId'),
        module_index=d.get('moduleIndex'),
        course_index=None,
    )
    row.quiz_score    = max(row.quiz_score or 0, score)
    row.quiz_passed   = row.quiz_passed or passed
    row.quiz_attempts += 1
    row.save()
    return ok({'passed': passed, 'score': score})


# ── admin ────────────────────────────────────────────────

@api_view(['GET'])
def admin_users(request):
    user = get_user(request)
    if not user or user.role != 'admin':
        return err('Unauthorized', 403)

    users = User.objects.all()
    return ok({'users': [user_dict(u) for u in users]})


@api_view(['GET'])
def admin_reports(request):
    user = get_user(request)
    if not user or user.role != 'admin':
        return err('Unauthorized', 403)

    reports = []
    for u in User.objects.filter(role='trainee'):
        rows      = Progress.objects.filter(user=u)
        total     = rows.filter(course_index__isnull=False).count()
        completed = rows.filter(course_index__isnull=False, completed=True).count()
        reports.append({
            **user_dict(u),
            'overallProgress': int(completed / total * 100) if total else 0,
            'completedCourses': completed,
        })

    return ok({'reports': reports})


@api_view(['DELETE'])
def admin_delete_user(request, user_id):
    user = get_user(request)
    if not user or user.role != 'admin':
        return err('Unauthorized', 403)

    User.objects.filter(id=user_id).delete()  # cascades to sessions & progress
    return ok({})
