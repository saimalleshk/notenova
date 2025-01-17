from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField

class Case(models.Model):
    case_id = models.CharField(max_length=50, unique=True)
    assigned_at = models.DateTimeField()
    solved_at = models.DateTimeField(null=True, blank=True)
    annotations = models.TextField(blank=True)

    def __str__(self):
        return self.case_id

class Point(models.Model):
    case = models.ForeignKey(Case, related_name='points', on_delete=models.CASCADE)
    key = models.CharField(max_length=50)
    value = models.TextField()

    def __str__(self):
        return f"{self.case.case_id} - {self.key}"


class TimeTracker(models.Model):
    BREAK_CHOICES = [
        ('break1', 'Break 1'),
        ('break2', 'Break 2'),
        ('lunch', 'Lunch'),
        ('training', 'Training'),
        ('meeting', 'Meeting'),
    ]

    AUX_CHOICES = [
        ('timeout', 'TimeOut'),
        ('Other', 'Other'),
        ('training', 'Training'),
        ('Mentoring', 'DEP'),

    ]

    break_type = models.CharField(max_length=20, choices=BREAK_CHOICES)
    aux_used = models.CharField(max_length=20, choices=AUX_CHOICES)
    in_time = models.DateTimeField()
    out_time = models.DateTimeField(null=True, blank=True)
    
    @property
    def total_time(self):
        if self.out_time:
            duration = self.out_time - self.in_time
            return round(duration.total_seconds() / 60)
        return None

    def __str__(self):
        return f"{self.break_type} - {self.in_time}"


class NewsEntry(models.Model):
    headline = models.CharField(max_length=200)
    paragraph = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.headline


