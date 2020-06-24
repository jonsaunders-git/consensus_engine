from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User
from  django.core.exceptions import PermissionDenied

from .mixins import TwoUserMixin, ProposalGroupMixin
from django.db import DataError

# Create your tests here.

from consensus_engine.models import ProposalGroup
from django.utils import timezone


# models test
class InviteTest(TwoUserMixin, ProposalGroupMixin, TestCase):

    def test_invite_creation(self):
        dt = timezone.now()
        pg = self.create_proposal_group()
        # user 1 invites user2 to the group
        i = pg.invite_user(self.user, self.user2)
        self.assertTrue(i is not None)
        self.assertTrue(i.invite_date_time >= dt and i.invite_date_time <= timezone.now())
        self.assertTrue(i.inviter == self.user)
        self.assertTrue(i.invitee == self.user2)
        self.assertTrue(i.accepted is None)

    def test_already_in_group(self):
        pg = self.create_proposal_group()
        # check owner
        with self.assertRaises(DataError, msg="User is already a member of this group") as e:
            i = pg.invite_user(self.user, self.user)
        # check joined user
        pg.join_group(self.user2)
        with self.assertRaises(DataError, msg="User is already a member of this group") as e:
            i2 = pg.invite_user(self.user, self.user2)

    def test_already_invited(self):
        pg = self.create_proposal_group()
        i = pg.invite_user(self.user, self.user2)
        # check invited user
        with self.assertRaises(DataError, msg="User has already been invited") as e:
            i2 = pg.invite_user(self.user, self.user2)

    def test_no_allowed_to_invite(self):
        pg = self.create_proposal_group()
        with self.assertRaises(PermissionDenied, msg="Inviter is not a member of the group") as e:
            i = pg.invite_user(self.user2, self.user)

    def test_invite_accept(self):
        pg = self.create_proposal_group()
        # user 1 invites user2 to the group
        i = pg.invite_user(self.user, self.user2)
        dt = timezone.now()
        i.accept()
        self.assertTrue(pg.is_user_member(self.user2))
        self.assertTrue(i.accepted == True)
        self.assertTrue(i.date_accepted_or_declined >= dt and i.date_accepted_or_declined <= timezone.now())
        self.assertTrue(pg.has_user_been_invited(self.user2) == False)

    def test_invite_declined(self):
        pg = self.create_proposal_group()
        # user 1 invites user2 to the group
        i = pg.invite_user(self.user, self.user2)
        dt = timezone.now()
        i.decline()
        self.assertFalse(pg.is_user_member(self.user2))
        self.assertTrue(i.accepted == False)
        self.assertTrue(i.date_accepted_or_declined >= dt and i.date_accepted_or_declined <= timezone.now())
        self.assertTrue(pg.has_user_been_invited(self.user2) == False)
