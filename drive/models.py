from django.contrib.auth.models import User
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class File(BaseModel):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="uploads/")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Group(BaseModel):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    files = models.ManyToManyField(File)

    def __str__(self):
        return self.name


class Permission(BaseModel):
    READ = "read"
    CHANGE = "change"
    PERMISSION_CHOICES = [
        (READ, "Read"),
        (CHANGE, "Change"),
    ]
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES)

    def __str__(self):
        return f"{self.file.name} - {self.permission}"

    class Meta:
        unique_together = (
            "file",
            "user",
        )  # Ensure unique permission for each user and file


class Sharing(BaseModel):
    shared_file = models.ForeignKey(File, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shared_with_users"
    )
    shared_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shared_by_users"
    )

    def __str__(self):
        return f"{self.shared_file.name} shared with {self.shared_with.username} by {self.shared_by.username}"
