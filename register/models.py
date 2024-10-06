from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from django.db import models

# Create your models here.
class Supervisor(models.Model):
    user = models.OneToOneField(User, null=True,on_delete=models.CASCADE)
    name = models.CharField(max_length=30, verbose_name='First Name')
    surname = models.CharField(max_length=30,verbose_name='Last Name')
    email = models.EmailField(unique=True,validators=[EmailValidator()],verbose_name='Email Address')
    sussex_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    telephone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username

class Student(models.Model):
    user = models.OneToOneField(User,null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, verbose_name='First Name')
    surname = models.CharField(max_length=30,verbose_name='Last Name')
    email = models.EmailField(unique=True,validators=[EmailValidator()],verbose_name='Email Address')
    sussex_id = models.CharField(max_length=20, unique=True)
    course = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Project(models.Model):
    STATUS_CHOICES = [
        ('Accepted', 'Accepted'),
        ('Proposed', 'Proposed'),
        ('Available', 'Available'),
        ('Requested', 'Requested'),
        ('Confirmed', 'Confirmed')
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    required_skills = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    proposed_by = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL)
    supervisor = models.ForeignKey(Supervisor, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.title

class ProjectTopic(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    projects = models.ManyToManyField(Project)
    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'
