import hashlib
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import User, Progress
from .training_data import TRAINING_DATA, TRACK_ORDER


# ── helpers ──────────────────────────────────────────────

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return view(request, *args, **kwargs)
    wrapper.__name__ = view.__name__
    return wrapper

def admin_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        if request.session.get('user_role') != 'admin':
            return redirect('dashboard')
        return view(request, *args, **kwargs)
    wrapper.__name__ = view.__name__
    return wrapper

def get_progress_data(user, track_id):
    rows = Progress.objects.filter(user=user, track_id=track_id)
    modules = {}
    total = completed = 0
    for row in rows:
        m, c = row.module_index, row.course_index
        if m not in modules:
            modules[m] = {'courses': {}, 'quiz_passed': False, 'quiz_score': None, 'quiz_attempts': 0}
        if c is not None:
            total += 1
            if row.completed:
                completed += 1
            modules[m]['courses'][c] = {'completed': row.completed}
        else:
            modules[m]['quiz_passed'] = row.quiz_passed
            modules[m]['quiz_score'] = row.quiz_score
            modules[m]['quiz_attempts'] = row.quiz_attempts
    overall = int(completed / total * 100) if total else 0
    return modules, overall


# ── auth pages ───────────────────────────────────────────

def login_page(request):
    if request.session.get('user_id'):
        return redirect('dashboard')

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        try:
            user = User.objects.get(email=email, password=hash_pw(password))
            request.session['user_id']    = str(user.id)
            request.session['user_role']  = user.role
            request.session['user_email'] = user.email
            request.session['user_name']  = f"{user.first_name} {user.last_name}"
            return redirect('dashboard')
        except User.DoesNotExist:
            return render(request, 'ncbw/login.html', {'error': 'Invalid email or password'})

    return render(request, 'ncbw/login.html')


def signup_page(request):
    if request.method == 'POST':
        email      = request.POST.get('email', '').strip().lower()
        password   = request.POST.get('password', '')
        first_name = request.POST.get('first_name', '')
        last_name  = request.POST.get('last_name', '')

        if User.objects.filter(email=email).exists():
            return render(request, 'ncbw/signup.html', {'error': 'Email already in use'})

        User.objects.create(
            email=email, password=hash_pw(password),
            first_name=first_name, last_name=last_name, role='trainee'
        )
        return redirect('login')

    return render(request, 'ncbw/signup.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


# ── main pages ───────────────────────────────────────────

@login_required
def dashboard(request):
    user = User.objects.get(id=request.session['user_id'])

    if user.role == 'admin':
        return redirect('admin_dashboard')

    # Trainee: show track selection or their track
    if not user.selected_track:
        return render(request, 'ncbw/select_track.html', {
            'tracks': [(k, v['name']) for k, v in TRAINING_DATA.items()]
        })

    track_id   = user.selected_track
    track_data = TRAINING_DATA.get(track_id, {})
    modules, overall = get_progress_data(user, track_id)

    return render(request, 'ncbw/dashboard.html', {
        'user':       user,
        'track_id':   track_id,
        'track':      track_data,
        'modules':    modules,
        'overall':    overall,
        'attributes': track_data.get('attributes', []),
    })


@login_required
@require_POST
def select_track(request):
    track_id = request.POST.get('track_id')
    if track_id not in TRAINING_DATA:
        return redirect('dashboard')
    user = User.objects.get(id=request.session['user_id'])
    user.selected_track = track_id
    user.save()
    return redirect('dashboard')


@login_required
def module_detail(request, track_id, module_index):
    user     = User.objects.get(id=request.session['user_id'])
    track    = TRAINING_DATA.get(track_id)
    if not track or module_index >= len(track['attributes']):
        return redirect('dashboard')

    module   = track['attributes'][module_index]
    modules, overall = get_progress_data(user, track_id)
    mod_prog = modules.get(module_index, {'courses': {}, 'quiz_passed': False, 'quiz_score': None, 'quiz_attempts': 0})

    return render(request, 'ncbw/module.html', {
        'user':         user,
        'track_id':     track_id,
        'track_name':   track['name'],
        'module_index': module_index,
        'module':       module,
        'progress':     mod_prog,
        'overall':      overall,
    })


@login_required
@require_POST
def mark_complete(request):
    data         = json.loads(request.body)
    track_id     = data.get('track_id')
    module_index = int(data.get('module_index'))
    course_index = int(data.get('course_index'))
    user         = User.objects.get(id=request.session['user_id'])

    row, _ = Progress.objects.get_or_create(
        user=user, track_id=track_id,
        module_index=module_index, course_index=course_index
    )
    row.completed    = True
    row.completed_at = timezone.now()
    row.save()

    _, overall = get_progress_data(user, track_id)
    return JsonResponse({'success': True, 'overall': overall})


@login_required
@require_POST
def submit_quiz(request):
    data         = json.loads(request.body)
    track_id     = data.get('track_id')
    module_index = int(data.get('module_index'))
    score        = float(data.get('score', 0))
    passed       = score >= 70
    user         = User.objects.get(id=request.session['user_id'])

    row, _ = Progress.objects.get_or_create(
        user=user, track_id=track_id,
        module_index=module_index, course_index=None
    )
    row.quiz_score    = max(row.quiz_score or 0, score)
    row.quiz_passed   = row.quiz_passed or passed
    row.quiz_attempts += 1
    row.save()

    return JsonResponse({'success': True, 'passed': passed, 'score': score})


# ── admin pages ──────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    users   = User.objects.filter(role='trainee')
    reports = []
    for u in users:
        rows      = Progress.objects.filter(user=u)
        total     = rows.filter(course_index__isnull=False).count()
        completed = rows.filter(course_index__isnull=False, completed=True).count()
        reports.append({
            'user':     u,
            'overall':  int(completed / total * 100) if total else 0,
            'completed': completed,
            'total':    total,
        })

    return render(request, 'ncbw/admin.html', {
        'reports':    reports,
        'all_users':  User.objects.all(),
        'user_name':  request.session.get('user_name'),
    })


@admin_required
@require_POST
def admin_delete_user(request, user_id):
    User.objects.filter(id=user_id).delete()
    return redirect('admin_dashboard')
