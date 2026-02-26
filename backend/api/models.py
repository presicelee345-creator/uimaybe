from django.db import models
import uuid


class User(models.Model):
    ROLE_CHOICES = [('admin', 'Admin'), ('trainee', 'Trainee')]

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email         = models.EmailField(unique=True)
    password      = models.CharField(max_length=64)   # SHA-256 hex
    first_name    = models.CharField(max_length=100)
    last_name     = models.CharField(max_length=100)
    role          = models.CharField(max_length=10, choices=ROLE_CHOICES, default='trainee')
    selected_track = models.CharField(max_length=100, blank=True, null=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} ({self.role})"


class Session(models.Model):
    token      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Progress(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    track_id     = models.CharField(max_length=100)
    module_index = models.IntegerField()
    course_index = models.IntegerField(null=True, blank=True)  # null = quiz row
    completed    = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    quiz_score   = models.FloatField(null=True, blank=True)
    quiz_passed  = models.BooleanField(default=False)
    quiz_attempts = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'track_id', 'module_index', 'course_index')
