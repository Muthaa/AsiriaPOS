from django.db import models
from django.contrib.auth.models import AbstractBaseUser, Group, Permission, PermissionsMixin, BaseUserManager

# Create your models here.

# class CustomUser(AbstractUser):
#     phone_number = models.CharField(max_length=15, unique=True)
#     is_admin = models.BooleanField(default=False)

#     groups = models.ManyToManyField(
#         Group,
#         related_name="customuser_groups",  # Change the related_name to avoid conflicts
#         blank=True
#     )
#     user_permissions = models.ManyToManyField(
#         Permission,
#         related_name="customuser_permissions",  # Change the related_name to avoid conflicts
#         blank=True
#     )

#     def __str__(self):
#         return self.username

#     class Meta:
#         verbose_name = "User"
#         verbose_name_plural = "Users"
#         ordering = ['username']
#         permissions = [
#             ("can_view_user", "Can view user"),
#             ("can_edit_user", "Can edit user"),
#             ("can_delete_user", "Can delete user"),
#             ("can_create_user", "Can create user"),
#         ]

class UserClientManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        return self.create_user(username, email, password, **extra_fields)


class UserClient(AbstractBaseUser, PermissionsMixin):
    """ UserClient model to manage user information """
    # Using AutoField for primary key to ensure unique user_client_id
    user_client_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserClientManager()  # Make sure this exists

    def __str__(self):
        return self.username
    
class Token(models.Model):
    user = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='tokens')
    key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Token for {self.user.username}"

# class Permission(models.Model):
#     permission_id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=100, unique=True)
#     codename = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name

# class Group(models.Model):
#     group_id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=100, unique=True)
#     permissions = models.ManyToManyField(Permission, related_name='groups')

#     def __str__(self):
#         return self.name

class UserClientGroup(models.Model):
    user = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='user_groups')
    # group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='user_groups')
    group = models.ManyToManyField(Group, related_name='user_groups', blank=True)

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

class UserClientPermission(models.Model):
    user = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='user_permits')
    # permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='user_permissions')
    permission = models.ManyToManyField(Permission, related_name='user_permits', blank=True)

    def __str__(self):
        return f"{self.user.username} has {self.permission.name} permission"

class UserClientSession(models.Model):
    user = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Session for {self.user.username}"
    
class PasswordResetToken(models.Model):
    user = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Password reset token for {self.user.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(UserClient, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
    
class UserClientActivityLog(models.Model):
    user = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"
    
class UserClientLoginHistory(models.Model):
    user = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='login_history')
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} logged in at {self.login_time}"

class UserClientLogoutHistory(models.Model):
    user = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='logout_history')
    logout_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} logged out at {self.logout_time}"

class UserClientPasswordHistory(models.Model):
    user = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='password_history')
    password_hash = models.CharField(max_length=128)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password history for {self.user.username} at {self.changed_at}"
    
class UserClientTwoFactorAuth(models.Model):
    user = models.OneToOneField(UserClient, on_delete=models.CASCADE, related_name='two_factor_auth')
    is_enabled = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=255, blank=True, null=True)
    backup_codes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"2FA for {self.user.username}"
    
class UserClientSocialAuth(models.Model):
    user = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='social_auth')
    provider = models.CharField(max_length=50)
    uid = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.provider} auth for {self.user.username}"