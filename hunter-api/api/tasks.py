from api.models import Guild, Hunter, Raid
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_hunter_welcome_email(hunter_id):
    try:
        hunter = Hunter.objects.get(pk=hunter_id)
        subject = "Welcome to the Hunter Network"
        message = (
            f"Hi {hunter.first_name},\n\nWelcome to the Hunter Network! "
            "Start exploring dungeons, joining raids, and leveling up your skills."
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [hunter.email])
        return f"Welcome email sent to {hunter.email}"
    except Hunter.DoesNotExist:
        return f"Hunter with id {hunter_id} does not exist."


@shared_task
def send_guild_invite_email(hunter_id, guild_id):
    try:
        hunter = Hunter.objects.get(pk=hunter_id)
        guild = Guild.objects.get(pk=guild_id)
        subject = f"You are invited to join the guild {guild.name}"
        message = f'Hi {hunter.first_name},\n\nYou have been invited to join the guild "{guild.name}".'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [hunter.email])
        return f"Guild invite sent to {hunter.email}"
    except (Hunter.DoesNotExist, Guild.DoesNotExist):
        return f"Hunter or Guild does not exist."


@shared_task
def send_raid_notification_email(raid_id):
    try:
        raid = Raid.objects.get(pk=raid_id)
        hunters = [p.hunter for p in raid.participations.all()]
        subject = f"Raid Notification: {raid.name}"
        for hunter in hunters:
            message = (
                f'Hi {hunter.first_name},\n\nYou are participating in the raid "{raid.name}" '
                f"on {raid.date}. Be prepared!"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [hunter.email])
        return f"Raid notifications sent to {len(hunters)} hunters."
    except Raid.DoesNotExist:
        return f"Raid with id {raid_id} does not exist."


@shared_task
def send_guild_creation_email(guild_id):
    try:
        guild = Guild.objects.get(pk=guild_id)
        subject = f"Guild Created: {guild.name}"
        message = f'Hi {guild.leader.first_name},\n\nYour guild "{guild.name}" has been created.'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [guild.leader.email])
        return f"Guild creation email sent to {guild.leader.email}"
    except Guild.DoesNotExist:
        return f"Guild with id {guild_id} does not exist."
