from typing import Any
from typing import Dict

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models.repositories import UserStatusRepository


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_user_status(sender, instance: User | None = None, created: bool = False, **kwargs: Dict[str, Any]) -> None:
    """
    Signal handler to update user status (gqlauth_userstatus table).
    Set user's verified status based on user's is_active state.

    Args:
        sender: The sender of the signal (AUTH_USER_MODEL).
        instance (User, optional): The instance of the newly created user.
        created (bool, optional): True if the user was newly created, False otherwise.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    if created and instance:
        user = UserStatusRepository.filter(user=instance).first()
        user.verified = instance.is_active
        user.save()

    if not created and instance:
        user, created = UserStatusRepository.get_or_create(user=instance)
        if user:
            user.verified = instance.is_active
            user.save()
