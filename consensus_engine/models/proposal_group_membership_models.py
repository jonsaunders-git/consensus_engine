from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone


class GroupMembership(models.Model):
    """ Defines membership of Groups """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    group = models.ForeignKey('ProposalGroup', on_delete=models.CASCADE, null=False)
    date_joined = models.DateTimeField('date joined')
    can_trial = models.BooleanField(default=False, null=True)


class GroupInviteManager(models.Manager):
    """ Manager for Group Invites """

    def my_open_invites(self, user):
        return self.get_queryset().filter(invitee=user, accepted=None)

    def my_open_invites_count(self, user):
        return self.my_open_invites(user).count()

    # To implement when needed
    # def my_accepted_invites(self, user):
    #    return self.get_queryset().filter(invitee=user, accepted=True)
    #
    # def my_declined_invites(self, user):
    #    return self.get_queryset().filter(invitee=user, accepted=True)
    #
    # def my_open_send_invitations(self, user):
    #    return self.get_queryset().filter(inviter=user, accepted=None)


class GroupInvite(models.Model):
    """ Defines an invite to a Group """
    group = models.ForeignKey('ProposalGroup', on_delete=models.CASCADE, null=False)
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name="invites")
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name="invited")
    invite_date_time = models.DateTimeField('date invited', null=False)
    # accepted - True = accepted, False=declined, null=Neither accepted or declined
    accepted = models.BooleanField(null=True)
    date_accepted_or_declined = models.DateTimeField('date accepted or declined', null=True)
    can_trial = models.BooleanField(null=True)
    # managers
    objects = GroupInviteManager()

    def accept(self):
        with transaction.atomic():
            self.accepted = True
            self.date_accepted_or_declined = timezone.now()
            self.group.join_group(self.invitee, can_trial=self.can_trial)
            self.save()

    def decline(self):
        with transaction.atomic():
            self.accepted = False
            self.date_accepted_or_declined = timezone.now()
            self.save()
