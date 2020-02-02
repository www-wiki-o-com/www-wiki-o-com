"""  __      __    __               ___
    /  \    /  \__|  | _ __        /   \
    \   \/\/   /  |  |/ /  |  __  |  |  |
     \        /|  |    <|  | |__| |  |  |
      \__/\__/ |__|__|__\__|       \___/

A web service for sharing opinions and avoiding arguments

@file       theories/test_models.py
@brief      A collection of unit tests for the app's models
@copyright  GNU Public License, 2018
@authors    Frank Imeson
"""


# *******************************************************************************
# imports
# *******************************************************************************
import random
import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from actstream.actions import follow

from theories.models import *
from theories.forms import *
from theories.utils import *
from users.utils import *
from theories.views import *


# *******************************************************************************
# defines
# *******************************************************************************


# ************************************************************
# CategoryTests
#
#
#
#
#
#
#
#
# ************************************************************
class CategoryTests(TestCase):

    # ******************************
    # CategoryTests
    # ******************************
    def setUp(self):

        # setup
        random.seed(0)
        create_groups_and_permissions()
        create_reserved_nodes()
        create_categories()

        # create user(s)
        self.bob = create_test_user(username='bob', password='1234')
        self.user = create_test_user(username='not_bob', password='1234')

        # create data
        self.theory = create_test_theory(created_by=self.user)
        self.category = Category.get('all')
        follow(self.bob, self.category, send_action=False)

    # ******************************
    # CategoryTests
    # ******************************
    def test_str(self):
        self.assertEqual(str(self.category), 'All')

    # ******************************
    # CategoryTests
    # ******************************
    def test_save(self):
        category = Category.objects.create(title='New')
        self.assertEqual(category.slug, 'new')

    # ******************************
    # CategoryTests
    # ******************************
    def test_get_exisiting(self):
        category = Category.get('ALL')
        self.assertEqual(category.slug, 'all')

    # ******************************
    # CategoryTests
    # ******************************
    def test_get_none(self):
        category = Category.get('blah')
        self.assertIsNone(category)

    # ******************************
    # CategoryTests
    # ******************************
    def test_get_create(self):
        category = Category.get('blah', create=True)
        self.assertIsNotNone(category)

    # ******************************
    # CategoryTests
    # ******************************
    def test_get_all(self):
        categories = [x.slug for x in Category.get_all(exclude=['ALL'])]
        self.assertIn('legal', categories)
        self.assertIn('health', categories)
        self.assertIn('conspiracy', categories)
        self.assertIn('pop-culture', categories)
        self.assertIn('science', categories)
        self.assertIn('politics', categories)
        self.assertNotIn('all', categories)

    # ******************************
    # CategoryTests
    # ******************************
    def test_get_url(self):
        self.assertEqual(self.category.get_absolute_url(), '/theories/all/')

    # ******************************
    # CategoryTests
    # ******************************
    def test_url(self):
        self.assertEqual(self.category.url(), '/theories/all/')

    # ******************************
    # CategoryTests
    # ******************************
    def test_activity_url(self):
        self.assertEqual(self.category.activity_url(),
                         '/theories/all/activity/')

    # ******************************
    # CategoryTests
    # ******************************
    def test_get_theories(self):
        self.assertIn(self.theory, self.category.get_theories())

    # ******************************
    # CategoryTests
    # ******************************
    def test_update_activity_logs(self):
        verb = "Yo Bob, what's up? Check out this theory yo."

        self.category.update_activity_logs(
            self.user, verb, action_object=self.theory)
        self.assertEqual(self.category.target_actions.count(), 1)
        self.assertEqual(self.bob.notifications.count(), 1)

        self.category.update_activity_logs(
            self.user, verb, action_object=self.theory)
        self.assertEqual(self.category.target_actions.count(), 1)
        self.assertEqual(self.bob.notifications.count(), 1)

        action = self.category.target_actions.first()
        action.timestamp -= datetime.timedelta(seconds=36000)
        action.save()

        notification = self.bob.notifications.first()
        notification.timestamp -= datetime.timedelta(seconds=36000)
        notification.save()

        self.category.update_activity_logs(
            self.user, verb, action_object=self.theory)
        self.assertEqual(self.category.target_actions.count(), 2)
        self.assertEqual(self.bob.notifications.count(), 2)


# ************************************************************
# TheoryNodeTests
#
#
#
#
#
#
#
#
#
# ************************************************************
class TheoryNodeTests(TestCase):

    # ******************************
    # TheoryNodeTests
    # ******************************
    def setUp(self):

        # setup
        random.seed(0)
        create_groups_and_permissions()
        create_reserved_nodes()
        create_categories()

        # create user(s)
        self.bob = create_test_user(username='bob', password='1234')
        self.user = create_test_user(username='not bob', password='1234')

        # create data
        self.category = Category.get('all')
        self.theory = create_test_theory(created_by=self.user, backup=True)
        self.subtheory = create_test_subtheory(
            parent_theory=self.theory, created_by=self.user)
        self.evidence = create_test_evidence(
            parent_theory=self.subtheory, created_by=self.user)
        self.fact = create_test_evidence(
            parent_theory=self.theory, title='Fact', fact=True, created_by=self.user)
        self.fiction = create_test_evidence(
            parent_theory=self.theory, title='Fiction', fact=False, created_by=self.user)
        self.intuition = TheoryNode.get_intuition_node()
        self.opinion = create_test_opinion(
            theory=self.theory, user=self.user, nodes=True)
        for stats in self.theory.get_all_stats():
            if stats.opinion_is_member(self.opinion):
                stats.add_opinion(self.opinion, save=False)
            stats.save_changes()
        follow(self.bob, self.theory, send_action=False)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_demo(self):
        demo = TheoryNode.get_demo()
        self.assertIsNotNone(demo)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_or_create_theory(self):
        node01 = TheoryNode.get_or_create_theory(
            true_title='Test', false_title='Test', created_by=self.user)
        node02 = TheoryNode.get_or_create_theory(true_title='Test')
        self.assertEqual(node01, node02)
        self.assertIn(node01, self.category.get_theories())
        self.assertTrue(node01.is_theory())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_or_create_subtheory00(self):
        node = self.evidence.get_or_create_subtheory(true_title='TestXXX')
        self.assertIsNone(node)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_or_create_subtheory01(self):
        node01 = self.theory.get_or_create_subtheory(
            true_title='Test', false_title='Test', created_by=self.user)
        node02 = self.theory.get_or_create_subtheory(true_title='Test')
        self.assertIn(node01, self.theory.get_nodes())
        self.assertEqual(node01, node02)
        self.assertNotIn(node01, self.category.get_theories())
        self.assertTrue(node01.is_theory())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_or_create_evidence00(self):
        node = self.evidence.get_or_create_evidence(title='TestXXX')
        self.assertIsNone(node)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_or_create_evidence01(self):
        node01 = self.theory.get_or_create_evidence(
            title='Test', created_by=self.user)
        node02 = self.theory.get_or_create_evidence(title='Test')
        self.assertIn(node01, self.theory.get_nodes())
        self.assertEqual(node01, node02)
        self.assertNotIn(node01, self.category.get_theories())
        self.assertTrue(node01.is_evidence())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_str(self):
        node01 = self.theory.get_or_create_subtheory(
            true_title='Test01', false_title='XXX')
        node02 = self.theory.get_or_create_evidence(title='Test02')
        self.assertEqual(node01.__str__(1, 0), 'Test01')
        self.assertEqual(node01.__str__(0, 1), 'XXX')
        self.assertEqual(str(node01), 'Test01')
        self.assertEqual(str(node02), 'Test02')

        node01.delete()
        self.assertEqual(str(node01), 'Test01 (deleted)')

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_true_statement(self):
        self.assertEqual(self.theory.get_true_statement(), self.theory.title01)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_false_statement(self):
        self.assertEqual(self.theory.get_false_statement(),
                         self.theory.__str__(0, 1))

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_title(self):
        self.assertEqual(self.evidence.get_title(), self.evidence.title01)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_about(self):
        self.assertEqual(self.theory.about().strip(), self.theory.title01)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_absolute_url(self):
        self.assertIsNotNone(self.theory.get_absolute_url())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_url(self):
        self.assertIsNotNone(self.theory.url())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_activity_url(self):
        self.assertIsNotNone(self.theory.activity_url())
        self.assertIsNotNone(self.evidence.activity_url())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_tag_id(self):
        self.assertIsNotNone(self.theory.tag_id())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_is_deleted(self):
        self.assertFalse(self.theory.is_deleted())
        self.theory.delete()
        self.assertTrue(self.theory.is_deleted())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_is_theory(self):
        self.assertTrue(self.theory.is_theory())
        self.assertTrue(self.subtheory.is_theory())
        self.assertFalse(self.evidence.is_theory())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_is_evidence(self):
        self.assertTrue(self.evidence.is_evidence())
        self.assertFalse(self.theory.is_evidence())
        self.assertFalse(self.subtheory.is_evidence())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_is_root(self):
        self.assertTrue(self.theory.is_root())
        self.assertFalse(self.subtheory.is_root())
        self.assertFalse(self.evidence.is_root())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_is_fact(self):
        self.assertTrue(self.fact.is_fact())
        self.assertFalse(self.evidence.is_fact())
        self.assertFalse(self.theory.is_fact())
        self.assertFalse(self.subtheory.is_fact())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_is_verifiable(self):
        self.assertTrue(self.fact.is_verifiable())
        self.assertFalse(self.evidence.is_verifiable())
        self.assertFalse(self.theory.is_verifiable())
        self.assertFalse(self.subtheory.is_verifiable())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_assert_theory(self):
        self.evidence.nodes.add(self.theory)
        self.evidence.flat_nodes.add(self.theory)
        self.assertTrue(self.theory.assert_theory())
        self.assertTrue(self.subtheory.assert_theory())
        self.assertFalse(self.evidence.assert_theory())

        self.evidence.delete()
        self.subtheory.flat_nodes.add(self.evidence)
        self.assertFalse(self.subtheory.assert_theory(check_nodes=True))

        # ToDo: test log

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_assert_evidence(self):
        self.assertTrue(self.evidence.assert_evidence())
        self.assertFalse(self.theory.assert_evidence())
        self.assertFalse(self.subtheory.assert_evidence())

        self.evidence.flat_nodes.add(self.theory)
        self.assertFalse(self.evidence.assert_evidence(check_nodes=True))

        self.evidence.nodes.add(self.theory)
        self.assertFalse(self.evidence.assert_evidence(check_nodes=True))

        # ToDo: test log

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_save01(self):
        self.theory.title01 = 'blah'
        self.theory.save()
        self.theory.refresh_from_db()
        self.assertEqual(self.theory.title01, 'blah')

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_save02(self):
        node01 = TheoryNode(title01='Test', node_type=TheoryNode.TYPE.THEORY)
        node01.save(user=self.user)
        self.assertEqual(node01.created_by, self.user)
        self.assertEqual(node01.modified_by, self.user)
        self.assertIn(TheoryNode.get_intuition_node(), node01.get_flat_nodes())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_autosave(self):
        assert self.evidence.get_revisions().count() == 0

        self.evidence.autosave(self.bob)
        self.assertEqual(self.evidence.get_revisions().count(), 1)

        self.evidence.autosave(self.bob, force=True)
        self.assertEqual(self.evidence.get_revisions().count(), 2)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_save_snapshot(self):
        assert self.evidence.get_revisions().count() == 0

        self.evidence.save_snapshot(self.bob)
        self.assertEqual(self.evidence.get_revisions().count(), 1)

        self.evidence.save_snapshot(self.bob)
        self.assertEqual(self.evidence.get_revisions().count(), 1)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_add_node(self):
        new = TheoryNode.objects.create(
            title01='new', node_type=TheoryNode.TYPE.EVIDENCE)

        result = self.evidence.add_node(new)
        self.assertFalse(result)

        result = self.subtheory.add_node(new)
        self.assertTrue(result)
        self.assertIn(new, self.subtheory.nodes.all())
        self.assertIn(new, self.subtheory.flat_nodes.all())
        self.assertIn(new, self.theory.flat_nodes.all())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_add_nodes(self):
        new = TheoryNode.objects.create(
            title01='new', node_type=TheoryNode.TYPE.EVIDENCE)
        result = self.evidence.add_nodes([new])
        self.assertFalse(result)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_nodes00(self):
        nodes = self.evidence.get_nodes()
        self.assertIsNone(nodes)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_nodes01(self):

        self.subtheory.delete()

        nodes = self.theory.get_nodes()
        self.assertIn(self.fact, nodes)
        self.assertIn(self.fiction, nodes)
        self.assertNotIn(self.subtheory, nodes)
        self.assertEqual(nodes.count(), 2)
        self.assertFalse(hasattr(self.theory, 'saved_nodes'))

        nodes = self.theory.get_nodes(deleted=True)
        self.assertIn(self.fact, nodes)
        self.assertIn(self.fiction, nodes)
        self.assertIn(self.subtheory, nodes)
        self.assertEqual(nodes.count(), 3)
        self.assertFalse(hasattr(self.theory, 'saved_nodes'))

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_nodes02(self):

        nodes = self.theory.get_nodes(cache=True)
        self.assertIn(self.fact, nodes)
        self.assertIn(self.fiction, nodes)
        self.assertIn(self.subtheory, nodes)
        self.assertEqual(nodes.count(), 3)
        self.assertEqual(self.theory.saved_nodes, nodes)

        nodes = self.theory.get_nodes(cache=True)
        self.assertIn(self.fact, nodes)
        self.assertIn(self.fiction, nodes)
        self.assertIn(self.subtheory, nodes)
        self.assertEqual(nodes.count(), 3)
        self.assertEqual(self.theory.saved_nodes, nodes)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_flat_nodes(self):

        nodes = self.evidence.get_flat_nodes()
        self.assertIsNone(nodes)

        nodes = self.theory.get_flat_nodes()
        self.assertIn(self.fact, nodes)
        self.assertIn(self.fiction, nodes)
        self.assertIn(self.evidence, nodes)
        self.assertIn(self.intuition, nodes)
        self.assertEqual(nodes.count(), 4)
        self.assertFalse(hasattr(self.theory, 'saved_flat_nodes'))

        self.subtheory.delete()

        nodes = self.theory.get_flat_nodes()
        self.assertIn(self.fact, nodes)
        self.assertIn(self.fiction, nodes)
        self.assertIn(self.intuition, nodes)
        self.assertEqual(nodes.count(), 3)
        self.assertFalse(hasattr(self.theory, 'saved_flat_nodes'))

        nodes = self.theory.get_flat_nodes(cache=True)
        self.assertIn(self.fact, nodes)
        self.assertIn(self.fiction, nodes)
        self.assertIn(self.intuition, nodes)
        self.assertEqual(nodes.count(), 3)
        self.assertTrue(hasattr(self.theory, 'saved_flat_nodes'))

        nodes = self.theory.get_flat_nodes(deleted=True)
        self.assertIn(self.fact, nodes)
        self.assertIn(self.fiction, nodes)
        self.assertIn(self.evidence, nodes)
        self.assertIn(self.intuition, nodes)
        self.assertEqual(nodes.count(), 4)
        self.assertNotIn(self.evidence, self.theory.nodes.all())
        self.assertTrue(hasattr(self.theory, 'saved_flat_nodes'))

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_evidence_nodes(self):

        nodes = self.evidence.get_evidence_nodes()
        self.assertIsNone(nodes)

        nodes = self.theory.get_evidence_nodes()
        self.assertIn(self.fact, nodes)
        self.assertIn(self.fiction, nodes)
        self.assertEqual(nodes.count(), 2)

        self.fiction.delete()

        nodes = self.theory.get_evidence_nodes()
        self.assertIn(self.fact, nodes)
        self.assertEqual(nodes.count(), 1)

        nodes = self.theory.get_evidence_nodes(deleted=True)
        self.assertIn(self.fact, nodes)
        self.assertIn(self.fiction, nodes)
        self.assertEqual(nodes.count(), 2)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_subtheory_nodes(self):

        nodes = self.evidence.get_subtheory_nodes()
        self.assertIsNone(nodes)

        nodes = self.theory.get_subtheory_nodes()
        self.assertIn(self.subtheory, nodes)
        self.assertEqual(nodes.count(), 1)

        self.subtheory.delete()

        nodes = self.theory.get_subtheory_nodes()
        self.assertEqual(nodes.count(), 0)

        nodes = self.theory.get_subtheory_nodes(deleted=True)
        self.assertIn(self.subtheory, nodes)
        self.assertEqual(nodes.count(), 1)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_parent_nodes01(self):

        nodes = self.evidence.get_parent_nodes()
        self.assertIn(self.subtheory, nodes)
        self.assertEqual(nodes.count(), 1)

        self.subtheory.delete()

        nodes = self.evidence.get_parent_nodes()
        self.assertEqual(nodes.count(), 0)

        nodes = self.evidence.get_parent_nodes(deleted=True)
        self.assertIn(self.subtheory, nodes)
        self.assertEqual(nodes.count(), 1)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_parent_nodes02(self):

        nodes = self.evidence.get_parent_nodes(cache=True)
        self.assertIn(self.subtheory, nodes)
        self.assertEqual(nodes.count(), 1)

        nodes = self.evidence.get_parent_nodes(cache=True)
        self.assertIn(self.subtheory, nodes)
        self.assertEqual(nodes.count(), 1)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_climb_theory_nodes(self):
        new = self.subtheory.get_or_create_subtheory(true_title='new')
        nodes = new.climb_theory_nodes()
        self.assertIn(self.theory, nodes)
        self.assertIn(self.subtheory, nodes)
        self.assertEqual(nodes.count(), 2)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_nested_nodes(self):

        nodes = self.evidence.get_nested_nodes()
        self.assertIsNone(nodes)

        nodes = self.theory.get_nested_nodes()
        self.assertIn(self.fact, nodes)
        self.assertIn(self.fiction, nodes)
        self.assertIn(self.evidence, nodes)
        self.assertIn(self.intuition, nodes)
        self.assertIn(self.subtheory, nodes)
        self.assertEqual(nodes.count(), 5)

        self.subtheory.delete()

        nodes = self.theory.get_nested_nodes()
        self.assertIn(self.fact, nodes)
        self.assertIn(self.fiction, nodes)
        self.assertIn(self.intuition, nodes)
        self.assertEqual(nodes.count(), 3)

        nodes = self.theory.get_nested_nodes(deleted=True)
        self.assertIn(self.fact, nodes)
        self.assertIn(self.fiction, nodes)
        self.assertIn(self.evidence, nodes)
        self.assertIn(self.intuition, nodes)
        self.assertIn(self.subtheory, nodes)
        self.assertEqual(nodes.count(), 5)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_nested_subtheory_nodes(self):
        new = self.subtheory.get_or_create_subtheory(true_title='new')

        nodes = self.evidence.get_nested_subtheory_nodes()
        self.assertIsNone(nodes)

        nodes = self.theory.get_nested_subtheory_nodes()
        self.assertIn(self.subtheory, nodes)
        self.assertIn(new, nodes)
        self.assertEqual(nodes.count(), 2)

        self.subtheory.delete()

        nodes = self.theory.get_nested_subtheory_nodes()
        self.assertEqual(nodes.count(), 0)

        nodes = self.theory.get_nested_subtheory_nodes(deleted=True)
        self.assertIn(self.subtheory, nodes)
        self.assertIn(new, nodes)
        self.assertEqual(nodes.count(), 2)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_remove_node00(self):
        result = self.evidence.remove_node(self.intuition)
        self.assertFalse(result)
        # todo: test log

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_remove_node01(self):
        self.subtheory.remove_node(self.evidence)
        self.assertNotIn(self.evidence, self.subtheory.nodes.all())
        self.assertNotIn(self.evidence, self.subtheory.flat_nodes.all())
        self.assertNotIn(self.evidence, self.theory.flat_nodes.all())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_remove_node02(self):
        self.theory.add_node(self.evidence)
        self.theory.refresh_from_db()
        self.subtheory.remove_node(self.evidence)
        self.assertNotIn(self.evidence, self.subtheory.nodes.all())
        self.assertNotIn(self.evidence, self.subtheory.flat_nodes.all())
        self.assertIn(self.evidence, self.theory.nodes.all())
        self.assertIn(self.evidence, self.theory.flat_nodes.all())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_remove_node03(self):
        assert self.user.notifications.count() == 0
        self.theory.remove_node(self.fiction, user=self.bob)
        self.assertEqual(self.user.notifications.count(), 1)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_remove_flat_node(self):
        result = self.theory.remove_flat_node(self.intuition)
        self.assertFalse(result)
        self.assertIn(self.intuition, self.theory.get_flat_nodes())

        result = self.theory.remove_flat_node(self.evidence)
        self.assertFalse(result)
        self.assertIn(self.evidence, self.theory.flat_nodes.all())

        self.theory.nodes.remove(self.subtheory)
        result = self.theory.remove_flat_node(self.evidence)
        self.assertTrue(result)
        self.assertNotIn(self.evidence, self.theory.flat_nodes.all())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_opinions(self):

        opinions = self.evidence.get_opinions()
        self.assertEqual(opinions.count(), 0)

        opinions = self.theory.get_opinions()
        self.assertEqual(opinions.count(), 1)
        self.assertFalse(hasattr(self.theory, 'saved_opinions'))

        opinions = self.theory.get_opinions(cache=True)
        self.assertEqual(opinions.count(), 1)
        self.assertEqual(self.theory.saved_opinions, opinions)

        opinions = self.theory.get_opinions(cache=True)
        self.assertEqual(opinions.count(), 1)
        self.assertEqual(self.theory.saved_opinions, opinions)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_revisions(self):
        revisions = self.theory.get_revisions()
        self.assertEqual(revisions.count(), 1)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_intuition_node(self):
        nodes = TheoryNode.objects.filter(title01='Intuition.')
        self.assertEqual(nodes.count(), 1)

        node = TheoryNode.get_intuition_node()
        nodes = TheoryNode.objects.filter(title01='Intuition.')
        self.assertTrue(node.is_evidence())
        self.assertFalse(node.is_fact())
        self.assertFalse(node.is_deleted())
        self.assertEqual(node.title01, 'Intuition.')
        self.assertEqual(nodes.count(), 1)

        node.delete(soft=False)
        TheoryNode.INTUITION_PK += 1
        nodes = TheoryNode.objects.filter(title01='Intuition.')
        self.assertEqual(nodes.count(), 1)

        super(TheoryNode, node).delete()
        node = TheoryNode.get_intuition_node(create=False)
        nodes = TheoryNode.objects.filter(title01='Intuition.')
        self.assertIsNone(node)
        self.assertEqual(nodes.count(), 0)

        node = TheoryNode.get_intuition_node()
        nodes = TheoryNode.objects.filter(title01='Intuition.')
        self.assertTrue(node.is_evidence())
        self.assertFalse(node.is_fact())
        self.assertFalse(node.is_deleted())
        self.assertEqual(node.title01, 'Intuition.')
        self.assertEqual(nodes.count(), 1)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_cache(self):
        assert not hasattr(self.theory, 'saved_nodes')
        assert not hasattr(self.theory, 'saved_flat_nodes')
        assert not hasattr(self.theory, 'saved_stats')

        result = self.evidence.cache()
        self.assertFalse(result)

        result = self.theory.cache(nodes=True, flat_nodes=False, stats=False)
        self.assertTrue(result)
        self.assertTrue(hasattr(self.theory, 'saved_nodes'))
        self.assertFalse(hasattr(self.theory, 'saved_flat_nodes'))
        self.assertFalse(hasattr(self.theory, 'saved_stats'))

        result = self.theory.cache(nodes=False, flat_nodes=True, stats=False)
        self.assertTrue(result)
        self.assertTrue(hasattr(self.theory, 'saved_nodes'))
        self.assertTrue(hasattr(self.theory, 'saved_flat_nodes'))
        self.assertFalse(hasattr(self.theory, 'saved_stats'))

        result = self.theory.cache(nodes=False, flat_nodes=False, stats=True)
        self.assertTrue(result)
        self.assertTrue(hasattr(self.theory, 'saved_nodes'))
        self.assertTrue(hasattr(self.theory, 'saved_flat_nodes'))
        self.assertTrue(hasattr(self.theory, 'saved_stats'))

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_stats(self):

        stats = self.evidence.get_stats(Stats.TYPE.ALL)
        self.assertIsNone(stats)

        stats = self.theory.get_stats(Stats.TYPE.ALL)
        self.assertIsNotNone(stats)

        self.theory.cache(stats=True)

        stats = self.theory.get_stats(Stats.TYPE.ALL)
        self.assertIsNotNone(stats)

        self.assertEqual(self.theory.stats.count(), 4)
        self.assertEqual(self.evidence.stats.count(), 0)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_get_all_stats(self):
        assert not hasattr(self.theory, 'saved_stats')

        stats = self.theory.get_all_stats()
        self.assertEqual(stats.count(), 4)
        self.assertFalse(hasattr(self.theory, 'saved_stats'))

        stats = self.theory.get_all_stats(cache=True)
        self.assertEqual(stats.count(), 4)
        self.assertTrue(hasattr(self.theory, 'saved_stats'))

        stats = self.evidence.get_all_stats()
        self.assertIsNone(stats)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_update_hits(self):
        old_rank = self.theory.rank
        old_hit_count = HitCount.objects.get_for_object(self.theory)
        response = self.client.get(self.theory.url())
        self.theory.refresh_from_db()
        hit_count = HitCount.objects.get_for_object(self.theory)
        self.assertEqual(hit_count.hits, old_hit_count.hits+1)
        self.assertTrue(self.theory.rank > old_rank)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_update_activity_logs01(self):
        verb = "Created."
        self.subtheory.update_activity_logs(self.user, verb)
        self.assertEqual(self.subtheory.target_actions.count(), 1)
        self.assertEqual(self.theory.target_actions.count(), 1)
        self.assertEqual(self.category.target_actions.count(), 1)
        self.assertEqual(self.bob.notifications.count(), 1)

        self.subtheory.update_activity_logs(self.user, verb)
        self.assertEqual(self.subtheory.target_actions.count(), 1)
        self.assertEqual(self.theory.target_actions.count(), 1)
        self.assertEqual(self.category.target_actions.count(), 1)
        self.assertEqual(self.bob.notifications.count(), 1)

        action = self.subtheory.target_actions.first()
        action.timestamp -= datetime.timedelta(seconds=36000)
        action.save()

        action = self.theory.target_actions.first()
        action.timestamp -= datetime.timedelta(seconds=36000)
        action.save()

        action = self.category.target_actions.first()
        action.timestamp -= datetime.timedelta(seconds=36000)
        action.save()

        notification = self.bob.notifications.first()
        notification.timestamp -= datetime.timedelta(seconds=36000)
        notification.save()

        self.subtheory.update_activity_logs(self.user, verb)
        self.assertEqual(self.subtheory.target_actions.count(), 2)
        self.assertEqual(self.theory.target_actions.count(), 2)
        self.assertEqual(self.category.target_actions.count(), 2)
        self.assertEqual(self.bob.notifications.count(), 2)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_update_activity_logs02(self):
        verb = "Deleted."
        self.subtheory.update_activity_logs(self.user, verb)
        self.assertEqual(self.subtheory.target_actions.count(), 1)
        self.assertEqual(self.theory.target_actions.count(), 1)
        self.assertEqual(self.category.target_actions.count(), 1)
        self.assertEqual(self.bob.notifications.count(), 1)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_delete00(self):
        result = self.evidence.delete()
        self.assertTrue(result)
        self.assertTrue(self.evidence.is_deleted())
        self.assertEqual(self.evidence.parent_flat_nodes.count(), 0)

        result = self.evidence.delete()
        self.assertFalse(result)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_delete01(self):
        self.evidence.delete()
        self.assertTrue(self.evidence.is_deleted())
        self.assertEqual(self.evidence.parent_flat_nodes.count(), 0)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_delete02(self):
        self.evidence.delete(soft=False)
        self.assertIsNone(self.evidence.id)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_delete03(self):
        self.subtheory.delete()
        self.evidence.refresh_from_db()
        self.assertTrue(self.subtheory.is_deleted())
        self.assertTrue(self.evidence.is_deleted())
        self.assertEqual(self.subtheory.parent_flat_nodes.count(), 0)
        self.assertEqual(self.evidence.parent_flat_nodes.count(), 0)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_delete04(self):
        new = self.theory.get_or_create_subtheory(true_title='new')
        new.add_node(self.evidence)
        self.subtheory.delete()
        self.evidence.refresh_from_db()
        self.assertTrue(self.subtheory.is_deleted())
        self.assertFalse(self.evidence.is_deleted())
        self.assertEqual(self.subtheory.parent_flat_nodes.count(), 0)
        self.assertIn(self.evidence, new.get_nodes())
        self.assertIn(self.evidence, self.subtheory.get_nodes())
        self.assertEqual(self.evidence.get_parent_nodes().count(), 1)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_delete05(self):
        assert self.user.notifications.count() == 0

        self.fiction.delete(user=self.bob)
        self.assertEqual(self.user.notifications.count(), 1)

        self.theory.delete(user=self.bob)
        self.assertEqual(self.user.notifications.count(), 4)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_swap_titles00(self):
        self.evidence.title00 = 'False'
        self.evidence.swap_titles()
        self.assertNotEqual(self.evidence.title01, 'False')

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_swap_titles01(self):
        self.theory.title00 = 'False'
        self.theory.swap_titles()
        self.assertEqual(self.theory.title01, 'False')
        self.assertEqual(self.user.notifications.count(), 1)
        # ToDo: test that points were reversed

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_convert00(self):
        success = self.theory.convert()
        self.assertTrue(self.theory.is_theory())
        self.assertFalse(success)

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_convert01(self):
        self.subtheory.convert()
        self.assertTrue(self.subtheory.is_evidence())
        self.assertFalse(self.subtheory.is_fact())
        # ToDo: lots...
        # ToDo: test notify

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_convert02(self):
        self.subtheory.convert(verifiable=True)
        self.assertTrue(self.subtheory.is_evidence())
        self.assertTrue(self.subtheory.is_fact())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_convert03(self):
        self.evidence.convert()
        self.assertTrue(self.subtheory.is_subtheory())

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_merge00(self):
        result = self.fact.merge(self.fiction)
        self.assertFalse(result)
        # todo lots more

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_merge01(self):
        new = self.theory.get_or_create_subtheory(true_title='new')
        assert new in self.theory.get_nodes()

    # ******************************
    # TheoryNodeTests
    # ******************************
    def test_recalculate_stats(self):

        result = self.evidence.recalculate_stats()
        self.assertFalse(result)

        result = self.theory.recalculate_stats()
        self.assertTrue(result)
        # toDo lots more


# ************************************************************
# OpinionTests
#
#
#
#
#
#
#
#
# ************************************************************
class OpinionTests(TestCase):

    # ******************************
    # OpinionTests
    # ******************************
    def setUp(self):

        # setup
        random.seed(0)
        create_groups_and_permissions()
        create_reserved_nodes()
        create_categories()

        # create user(s)
        self.user = create_test_user(username='bob1', password='1234')
        self.bob = create_test_user(username='bob2', password='1234')

        # create data
        self.theory = create_test_theory(created_by=self.user)
        self.subtheory = create_test_subtheory(
            parent_theory=self.theory, created_by=self.user)
        self.evidence = create_test_evidence(
            parent_theory=self.subtheory, created_by=self.user)
        self.fact = create_test_evidence(
            parent_theory=self.theory, title='Fact', fact=True, created_by=self.user)
        self.fiction = create_test_evidence(
            parent_theory=self.theory, title='Fiction', fact=False, created_by=self.user)
        self.intuition = self.theory.get_intuition_node()

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_demo(self):
        demo = Opinion.get_demo()
        self.assertIsNotNone(demo)

    # ******************************
    # OpinionTests
    # ******************************
    def test_str(self):
        opinion = self.theory.opinions.create(user=self.user)
        self.assertEqual(opinion.__str__(), self.theory.__str__())

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_evidence_nodes(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node01 = opinion.nodes.create(
            theory_node=self.fact,
            tt_input=100,
        )
        opinion_node02 = opinion.nodes.create(
            theory_node=self.subtheory,
            tt_input=100,
        )
        evidence = opinion.get_evidence_nodes()
        self.assertEqual(evidence.count(), 1)
        self.assertIn(opinion_node01, evidence)
        self.assertNotIn(opinion_node02, evidence)

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_subtheory_nodes(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node01 = opinion.nodes.create(
            theory_node=self.fact,
            tt_input=100,
        )
        opinion_node02 = opinion.nodes.create(
            theory_node=self.subtheory,
            tt_input=100,
        )
        subtheories = opinion.get_subtheory_nodes()
        self.assertEqual(subtheories.count(), 1)
        self.assertNotIn(opinion_node01, subtheories)
        self.assertIn(opinion_node02, subtheories)

    # ******************************
    # OpinionTests
    # ******************************
    def test_is_anonymous(self):
        # setup
        opinion = self.theory.opinions.create(user=self.user)

        # blah
        self.user.hidden = False
        opinion.anonymous = False
        self.assertFalse(opinion.is_anonymous())

        # blah
        self.user.hidden = False
        opinion.anonymous = True
        self.assertTrue(opinion.is_anonymous())

        # blah
        self.user.hidden = True
        opinion.anonymous = False
        self.assertTrue(opinion.is_anonymous())

        # blah
        self.user.hidden = True
        opinion.anonymous = True
        self.assertTrue(opinion.is_anonymous())

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_owner(self):
        # setup
        opinion = self.theory.opinions.create(user=self.user)

        # blah
        self.user.hidden = False
        opinion.anonymous = False
        self.assertEqual(opinion.get_owner(), self.user.__str__())

        # blah
        self.user.hidden = True
        opinion.anonymous = True
        self.assertEqual(opinion.get_owner(), 'Anonymous')

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_owner_long(self):
        # setup
        opinion = self.theory.opinions.create(user=self.user)

        # blah
        self.user.hidden = False
        opinion.anonymous = False
        self.assertEqual(opinion.get_owner_long(),
                         self.user.__str__(print_fullname=True))

        # blah
        self.user.hidden = True
        opinion.anonymous = True
        self.assertEqual(opinion.get_owner_long(), 'Anonymous')

    # ******************************
    # OpinionTests
    # ******************************
    def test_edit_url(self):
        opinion = self.theory.opinions.create(user=self.user)
        self.assertIsNotNone(opinion.edit_url())

    # ******************************
    # OpinionTests
    # ******************************
    def test_compare_url(self):
        opinion = self.theory.opinions.create(user=self.user)
        stats = self.theory.get_stats(Stats.TYPE.ALL)
        self.assertIsNotNone(opinion.compare_url())
        self.assertIsNotNone(opinion.compare_url(opinion))
        self.assertIsNotNone(opinion.compare_url(stats))

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_absolute_url(self):
        opinion = self.theory.opinions.create(user=self.user)
        self.assertIsNotNone(opinion.get_absolute_url())

    # ******************************
    # OpinionTests
    # ******************************
    def test_url(self):
        opinion = self.theory.opinions.create(user=self.user)
        self.assertIsNotNone(opinion.url())

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_node(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion.nodes.create(
            theory_node=self.fact,
            tt_input=100,
        )
        assert not hasattr(opinion, 'saved_nodes')

        # blah
        opinion_node = opinion.get_node(self.fact)
        self.assertIsNotNone(opinion_node)

        # blah
        opinion_node = opinion.get_node(self.fiction)
        self.assertIsNone(opinion_node)

        # blah
        opinion_node = opinion.get_node(self.fiction, create=True)
        self.assertIsNotNone(opinion_node)

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_node_cached(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion.nodes.create(
            theory_node=self.fact,
            tt_input=100,
        )
        assert not hasattr(opinion, 'saved_nodes')
        opinion.cache()

        # blah
        opinion_node = opinion.get_node(self.fact)
        self.assertIsNotNone(opinion_node)

        # blah
        opinion_node = opinion.get_node(self.fiction)
        self.assertIsNone(opinion_node)

        # blah
        opinion_node = opinion.get_node(self.fiction, create=True)
        self.assertIsNotNone(opinion_node)

    # ******************************
    # OpinionTests
    # ******************************
    def test_cache(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.fact,
            tt_input=100,
        )
        assert not hasattr(opinion, 'saved_nodes')
        opinion.cache()

        self.assertEqual(opinion.saved_nodes.count(), 1)
        self.assertIn(opinion_node, opinion.saved_nodes)

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_nodes(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node01 = opinion.nodes.create(
            theory_node=self.fact,
            tt_input=100,
        )
        opinion_node02 = opinion.nodes.create(
            theory_node=self.fiction,
            tt_input=100,
        )
        self.fiction.delete()
        assert not hasattr(opinion, 'saved_nodes')

        # blah
        nodes = opinion.get_nodes()
        self.assertEqual(nodes.count(), 2)
        self.assertIn(opinion_node01, nodes)
        self.assertIn(opinion_node02, nodes)

        # blah
        nodes = opinion.get_nodes(cache=True)
        self.assertTrue(hasattr(opinion, 'saved_nodes'))
        self.assertEqual(nodes, opinion.saved_nodes)
        self.assertEqual(nodes.count(), 2)
        self.assertIn(opinion_node01, nodes)
        self.assertIn(opinion_node02, nodes)

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_flat_node(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion.nodes.create(
            theory_node=self.fact,
            tt_input=100,
        )
        assert not hasattr(opinion, 'saved_flat_nodes')

        # blah
        opinion_node = opinion.get_flat_node(self.fact)
        self.assertIsNotNone(opinion_node)

        # blah
        opinion_node = opinion.get_flat_node(self.fiction, create=False)
        self.assertIsNone(opinion_node)

        # blah
        opinion_node = opinion.get_flat_node(self.fiction, create=True)
        self.assertIsNotNone(opinion_node)

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_flat_nodes(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node01 = opinion.nodes.create(
            theory_node=self.fact,
            ft_input=100,
        )
        opinion_node02 = opinion.nodes.create(
            theory_node=self.fiction,
            ft_input=100,
        )
        opinion_node03 = opinion.nodes.create(
            theory_node=self.subtheory,
            ft_input=100,
        )
        child_opinion = self.subtheory.opinions.create(
            user=self.user,
        )
        opinion_node04 = child_opinion.nodes.create(
            theory_node=self.evidence,
            tt_input=100,
        )
        self.fiction.delete()

        # blah
        flat_nodes = opinion.get_flat_nodes()
        self.assertEqual(flat_nodes.count(), 4)
        self.assertIsNotNone(flat_nodes.get(self.intuition.pk))
        self.assertIsNotNone(flat_nodes.get(self.fact.pk))
        self.assertIsNotNone(flat_nodes.get(self.fiction.pk))
        self.assertIsNotNone(flat_nodes.get(self.evidence.pk))
        self.assertIsNone(flat_nodes.get(self.subtheory.pk))

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_intuition_node(self):
        opinion = self.theory.opinions.create(user=self.user)

        # blah
        node = opinion.get_intuition_node(create=False)
        self.assertIsNone(node)

        # blah
        node = opinion.get_intuition_node(create=True)
        self.assertIsNotNone(node)
        self.assertEqual(node.theory_node, self.intuition)

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_subtheory_nodes(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion.nodes.create(
            theory_node=self.fact,
            ft_input=100,
        )
        opinion.nodes.create(
            theory_node=self.subtheory,
            ft_input=100,
        )

        # blah
        nodes = opinion.get_subtheory_nodes()
        self.assertEqual(nodes.count(), 1)
        self.assertEqual(nodes[0].theory_node, self.subtheory)

        # blah
        self.subtheory.delete()

        # blah
        nodes = opinion.get_subtheory_nodes()
        self.assertEqual(nodes.count(), 1)
        self.assertEqual(nodes[0].theory_node, self.subtheory)

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_evidence_nodes(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion.nodes.create(
            theory_node=self.fact,
            ft_input=100,
        )
        opinion.nodes.create(
            theory_node=self.subtheory,
            ft_input=100,
        )

        # blah
        nodes = opinion.get_evidence_nodes()
        self.assertEqual(nodes.count(), 1)
        self.assertEqual(nodes[0].theory_node, self.fact)

        # blah
        self.subtheory.delete()

        # blah
        nodes = opinion.get_evidence_nodes()
        self.assertEqual(nodes.count(), 1)
        self.assertEqual(nodes[0].theory_node, self.fact)

    # ******************************
    # OpinionTests
    # ******************************
    def test_get_parent_nodes(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            tt_input=80,
            ff_input=20,
        )
        child_opinion = self.subtheory.opinions.create(
            user=self.user,
            true_input=80,
            false_input=20,
            force=True,
        )

        # blah
        parent_nodes = child_opinion.get_parent_nodes()
        self.assertEqual(parent_nodes.count(), 1)
        self.assertIn(opinion_node, parent_nodes)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points00(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion.update_points()
        intuition = opinion.get_intuition_node()
        self.assertEqual(intuition.true_points(), 0.0)
        self.assertEqual(intuition.false_points(), 0.0)
        self.assertEqual(opinion.true_points(), 0.0)
        self.assertEqual(opinion.false_points(), 0.0)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points01(self):
        opinion = self.theory.opinions.create(
            user=self.user,
            true_input=100,
            false_input=0,
        )
        opinion.update_points()
        intuition = opinion.get_intuition_node()
        self.assertEqual(intuition.true_points(), 1.0)
        self.assertEqual(intuition.false_points(), 0.0)
        self.assertEqual(opinion.true_points(), 1.0)
        self.assertEqual(opinion.false_points(), 0.0)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points02(self):
        opinion = self.theory.opinions.create(
            user=self.user,
            true_input=0,
            false_input=100,
        )
        opinion.update_points()
        intuition = opinion.get_intuition_node()
        self.assertEqual(intuition.true_points(), 0.0)
        self.assertEqual(intuition.false_points(), 1.0)
        self.assertEqual(opinion.true_points(), 0.0)
        self.assertEqual(opinion.false_points(), 1.0)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points03(self):
        opinion = self.theory.opinions.create(
            user=self.user,
            true_input=50,
            false_input=50,
        )
        opinion.update_points()
        intuition = opinion.get_intuition_node()
        self.assertEqual(intuition.true_points(), 0.5)
        self.assertEqual(intuition.false_points(), 0.5)
        self.assertEqual(opinion.true_points(), 0.5)
        self.assertEqual(opinion.false_points(), 0.5)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points04(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.fact,
        )
        opinion.update_points()

        # blah
        nodes = opinion.get_nodes()
        self.assertNotIn(opinion_node, nodes)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points_fact01(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.fact,
            tt_input=100,
        )
        opinion.update_points()
        opinion_node.refresh_from_db()
        intuition = opinion.get_intuition_node()
        self.assertEqual(intuition.true_points(), 0.0)
        self.assertEqual(intuition.false_points(), 0.0)
        self.assertEqual(opinion_node.true_points(), 1.0)
        self.assertEqual(opinion_node.false_points(), 0.0)
        self.assertEqual(opinion.true_points(), 1.0)
        self.assertEqual(opinion.false_points(), 0.0)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points_fact02(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.fact,
            tf_input=100,
        )
        opinion.update_points()
        opinion_node.refresh_from_db()
        intuition = opinion.get_intuition_node()
        self.assertEqual(intuition.true_points(), 0.0)
        self.assertEqual(intuition.false_points(), 0.0)
        self.assertEqual(opinion_node.true_points(), 0.0)
        self.assertEqual(opinion_node.false_points(), 1.0)
        self.assertEqual(opinion.true_points(), 0.0)
        self.assertEqual(opinion.false_points(), 1.0)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points_fact03(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.fact,
            tt_input=100,
            tf_input=100,
        )
        opinion.update_points()
        opinion_node.refresh_from_db()
        intuition = opinion.get_intuition_node()
        self.assertEqual(intuition.true_points(), 0.0)
        self.assertEqual(intuition.false_points(), 0.0)
        self.assertEqual(opinion_node.true_points(), 0.5)
        self.assertEqual(opinion_node.false_points(), 0.5)
        self.assertEqual(opinion.true_points(), 0.5)
        self.assertEqual(opinion.false_points(), 0.5)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points_fact10(self):
        opinion = self.theory.opinions.create(
            user=self.user,
            true_input=50,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.fact,
            tf_input=50,
        )
        opinion.update_points()
        opinion_node.refresh_from_db()
        intuition = opinion.get_intuition_node()
        self.assertEqual(intuition.true_points(), 0.5)
        self.assertEqual(intuition.false_points(), 0.0)
        self.assertEqual(opinion_node.true_points(), 0.0)
        self.assertEqual(opinion_node.false_points(), 0.5)
        self.assertEqual(opinion.true_points(), 0.5)
        self.assertEqual(opinion.false_points(), 0.5)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points_fact11(self):
        opinion = self.theory.opinions.create(
            user=self.user,
            true_input=25,
            false_input=75,
            force=True,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.fact,
            tf_input=50,
        )
        opinion.update_points()
        opinion_node.refresh_from_db()
        intuition = opinion.get_intuition_node()
        self.assertEqual(intuition.true_points(), 0.25)
        self.assertEqual(intuition.false_points(), 0.0)
        self.assertEqual(opinion_node.true_points(), 0.0)
        self.assertEqual(opinion_node.false_points(), 0.75)
        self.assertEqual(opinion.true_points(), 0.25)
        self.assertEqual(opinion.false_points(), 0.75)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points_subtheory01(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            tt_input=100,
        )
        opinion.update_points()
        opinion_node.refresh_from_db()
        flat_intuition = opinion.get_flat_node(theory_node=self.intuition)
        self.assertEqual(flat_intuition.true_points(), 1.0)
        self.assertEqual(flat_intuition.false_points(), 0.0)
        self.assertEqual(opinion_node.true_points(), 1.0)
        self.assertEqual(opinion_node.false_points(), 0.0)
        self.assertEqual(opinion.true_points(), 1.0)
        self.assertEqual(opinion.false_points(), 0.0)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points_subtheory02(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            tf_input=100,
        )
        opinion.update_points()
        opinion_node.refresh_from_db()
        flat_intuition = opinion.get_flat_node(theory_node=self.intuition)
        self.assertEqual(flat_intuition.true_points(), 0.0)
        self.assertEqual(flat_intuition.false_points(), 1.0)
        self.assertEqual(opinion_node.true_points(), 0.0)
        self.assertEqual(opinion_node.false_points(), 1.0)
        self.assertEqual(opinion.true_points(), 0.0)
        self.assertEqual(opinion.false_points(), 1.0)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points_subtheory10(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            tt_input=100,
        )
        child_opinion = self.subtheory.opinions.create(
            user=self.user,
        )
        child_opinion.update_points()
        opinion.update_points()
        opinion_node.refresh_from_db()
        flat_intuition = opinion.get_flat_node(theory_node=self.intuition)
        self.assertEqual(flat_intuition.true_points(), 1.0)
        self.assertEqual(flat_intuition.false_points(), 0.0)
        self.assertEqual(opinion_node.true_points(), 1.0)
        self.assertEqual(opinion_node.false_points(), 0.0)
        self.assertEqual(opinion.true_points(), 1.0)
        self.assertEqual(opinion.false_points(), 0.0)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points_subtheory11(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            tf_input=100,
        )
        child_opinion = self.subtheory.opinions.create(
            user=self.user,
        )
        child_opinion.update_points()
        opinion.update_points()
        opinion_node.refresh_from_db()
        flat_intuition = opinion.get_flat_node(theory_node=self.intuition)
        self.assertEqual(flat_intuition.true_points(), 0.0)
        self.assertEqual(flat_intuition.false_points(), 1.0)
        self.assertEqual(opinion_node.true_points(), 0.0)
        self.assertEqual(opinion_node.false_points(), 1.0)
        self.assertEqual(opinion.true_points(), 0.0)
        self.assertEqual(opinion.false_points(), 1.0)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points_subtheory20(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            ft_input=100,
        )
        child_opinion = self.subtheory.opinions.create(
            user=self.user,
        )
        child_node = child_opinion.nodes.create(
            theory_node=self.evidence,
            tt_input=100,
        )
        child_opinion.update_points()
        opinion.update_points()
        opinion_node.refresh_from_db()
        child_node.refresh_from_db()
        flat_intuition = opinion.get_flat_node(theory_node=self.intuition)
        self.assertEqual(flat_intuition.true_points(), 1.0)
        self.assertEqual(flat_intuition.false_points(), 0.0)
        self.assertEqual(opinion_node.true_points(), 1.0)
        self.assertEqual(opinion_node.false_points(), 0.0)
        self.assertEqual(opinion.true_points(), 1.0)
        self.assertEqual(opinion.false_points(), 0.0)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points_subtheory21(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            tt_input=100,
        )
        child_opinion = self.subtheory.opinions.create(
            user=self.user,
        )
        child_node = child_opinion.nodes.create(
            theory_node=self.evidence,
            tt_input=100,
        )
        child_opinion.update_points()
        opinion.update_points()
        opinion_node.refresh_from_db()
        child_node.refresh_from_db()
        flat_intuition = opinion.get_flat_node(theory_node=self.intuition)
        self.assertEqual(flat_intuition.true_points(), 0.0)
        self.assertEqual(flat_intuition.false_points(), 0.0)
        self.assertEqual(opinion_node.true_points(), 1.0)
        self.assertEqual(opinion_node.false_points(), 0.0)
        self.assertEqual(opinion.true_points(), 1.0)
        self.assertEqual(opinion.false_points(), 0.0)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points_subtheory22(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            tt_input=80,
            tf_input=20,
        )
        child_opinion = self.subtheory.opinions.create(
            user=self.user,
            true_input=80,
            false_input=20,
            force=True,
        )
        child_node = child_opinion.nodes.create(
            theory_node=self.evidence,
            tt_input=100,
        )
        child_opinion.update_points()
        opinion.update_points()
        opinion_node.refresh_from_db()
        child_node.refresh_from_db()

        flat_intuition = child_opinion.get_flat_node(
            theory_node=self.intuition)
        self.assertEqual(child_opinion.true_points(), 0.8)
        self.assertEqual(child_opinion.false_points(), 0.2)
        self.assertEqual(flat_intuition.true_points(), 0.0)
        self.assertEqual(flat_intuition.false_points(), 0.2)
        self.assertEqual(child_node.true_points(), 0.8)
        self.assertEqual(child_node.false_points(), 0.0)

        flat_intuition = opinion.get_flat_node(theory_node=self.intuition)
        flat_evidence = opinion.get_flat_node(theory_node=self.evidence)
        self.assertEqual(opinion_node.true_points(), 0.8)
        self.assertEqual(opinion_node.false_points(), 0.2)
        self.assertEqual(flat_intuition.true_points(), 0.0)
        self.assertEqual(flat_intuition.false_points(), 0.0)
        self.assertEqual(flat_evidence.true_points(), 0.8)
        self.assertEqual(flat_evidence.false_points(), 0.2)
        self.assertEqual(opinion.true_points(), 0.8)
        self.assertEqual(opinion.false_points(), 0.2)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_points_subtheory23(self):
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            tt_input=80,
            ff_input=20,
        )
        child_opinion = self.subtheory.opinions.create(
            user=self.user,
            true_input=80,
            false_input=20,
            force=True,
        )
        child_node = child_opinion.nodes.create(
            theory_node=self.evidence,
            tt_input=100,
        )
        child_opinion.update_points()
        opinion.update_points()
        opinion_node.refresh_from_db()
        child_node.refresh_from_db()

        flat_intuition = child_opinion.get_flat_node(
            theory_node=self.intuition)
        self.assertEqual(child_opinion.true_points(), 0.8)
        self.assertEqual(child_opinion.false_points(), 0.2)
        self.assertEqual(flat_intuition.true_points(), 0.0)
        self.assertEqual(flat_intuition.false_points(), 0.2)
        self.assertEqual(child_node.true_points(), 0.8)
        self.assertEqual(child_node.false_points(), 0.0)

        flat_intuition = opinion.get_flat_node(theory_node=self.intuition)
        flat_evidence = opinion.get_flat_node(theory_node=self.evidence)
        self.assertEqual(opinion_node.true_points(), 0.8)
        self.assertEqual(opinion_node.false_points(), 0.2)
        self.assertEqual(flat_intuition.true_points(), 0.0)
        self.assertEqual(flat_intuition.false_points(), 0.2)
        self.assertEqual(flat_evidence.true_points(), 0.8)
        self.assertEqual(flat_evidence.false_points(), 0.0)
        self.assertEqual(opinion.true_points(), 0.8)
        self.assertEqual(opinion.false_points(), 0.2)

    # ******************************
    # OpinionTests
    # ******************************
    def test_copy(self):
        # setup existing opinion
        opinion = self.theory.opinions.create(
            user=self.user,
            true_input=10,
            false_input=20,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            tt_input=80,
            ff_input=20,
        )
        child_opinion = self.subtheory.opinions.create(
            user=self.user,
            true_input=80,
            false_input=20,
            force=True,
        )
        child_node = child_opinion.nodes.create(
            theory_node=self.evidence,
            tt_input=100,
        )
        opinion.update_points()
        child_opinion.update_points()

        # setup bob's opinion
        opinion = self.theory.opinions.create(
            user=self.bob,
            true_input=44,
            false_input=55,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            tt_input=66,
            ff_input=33,
        )
        child_opinion = self.subtheory.opinions.create(
            user=self.bob,
            true_input=99,
            false_input=22,
            force=True,
        )
        child_node = child_opinion.nodes.create(
            theory_node=self.evidence,
            ff_input=100,
        )
        opinion.update_points()
        child_opinion.update_points()

        # blah
        copied_opinion = opinion.copy(self.user)
        copied_node = copied_opinion.get_nodes().get(
            theory_node=opinion_node.theory_node)
        copied_child = get_or_none(
            self.subtheory.get_opinions(), user=self.user)
        self.assertEqual(copied_opinion.true_points(), opinion.true_points())
        self.assertEqual(copied_node.tt_input, opinion_node.tt_input)
        self.assertEqual(copied_node.ff_input, opinion_node.ff_input)
        self.assertNotEqual(copied_child.true_points(),
                            child_opinion.true_points())

        # blah
        copied_opinion = opinion.copy(self.user, recursive=True)
        copied_node = copied_opinion.get_nodes().get(
            theory_node=opinion_node.theory_node)
        copied_child = get_or_none(
            self.subtheory.get_opinions(), user=self.user)
        self.assertEqual(copied_opinion.true_points(), opinion.true_points())
        self.assertEqual(copied_node.tt_input, opinion_node.tt_input)
        self.assertEqual(copied_node.ff_input, opinion_node.ff_input)
        self.assertEqual(copied_child.true_points(),
                         child_opinion.true_points())

    # ******************************
    # OpinionTests
    # ******************************
    def test_true_points(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            tt_input=80,
            ff_input=20,
        )
        opinion.update_points()

        # blah
        self.assertEqual(opinion.true_points(), 0.8)

        # coverage test
        opinion.true_total = 0
        opinion.false_total = 0
        self.assertEqual(opinion.true_points(), 0.0)

        # coverage test
        opinion.true_total = 0
        opinion.false_total = 0
        opinion.force = True
        self.assertEqual(opinion.true_points(), 0.0)

        # ToDo: Much more

    # ******************************
    # OpinionTests
    # ******************************
    def test_false_points(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.user,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            tt_input=80,
            ff_input=20,
        )
        opinion.update_points()

        # blah
        self.assertEqual(opinion.false_points(), 0.2)

        # coverage test
        opinion.true_total = 0
        opinion.false_total = 0
        self.assertEqual(opinion.false_points(), 0.0)

        # coverage test
        opinion.true_total = 0
        opinion.false_total = 0
        opinion.force = True
        self.assertEqual(opinion.false_points(), 0.0)

        # ToDo: Much more

    # ******************************
    # OpinionTests
    # ******************************
    def test_swap_true_false(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.user,
            true_input=80,
            false_input=20,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.subtheory,
            tt_input=80,
            ff_input=20,
        )
        opinion.update_points()
        opinion.swap_true_false()

        # blah
        self.assertEqual(opinion.true_input, 20)
        self.assertEqual(opinion.false_input, 80)
        self.assertEqual(opinion.true_points(), 0.2)
        self.assertEqual(opinion.false_points(), 0.8)

        # ToDo: much more

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_hits(self):
        # setup
        opinion = self.theory.opinions.create(user=self.user)
        hit_count = HitCount.objects.get_for_object(opinion)
        assert hit_count.hits == 0

        # blah
        url = reverse('theories:opinion-detail', kwargs={'pk': opinion.pk})
        self.client.get(url)
        hit_count = HitCount.objects.get_for_object(opinion)
        self.assertEqual(hit_count.hits, 1)

    # ******************************
    # OpinionTests
    # ******************************
    def test_update_activity_logs(self):
        # setup
        opinion = self.theory.opinions.create(user=self.user)
        follow(self.bob, opinion, send_action=False)
        assert self.bob.notifications.count() == 0
        assert opinion.target_actions.count() == 0

        # blah
        verb = "Modified."
        opinion.update_activity_logs(self.user, verb)
        self.assertEqual(opinion.target_actions.count(), 1)
        self.assertEqual(self.bob.notifications.count(), 1)

        # ToDo: Much more


# ************************************************************
# OpinionNodeTests
#
#
#
#
#
#
# ************************************************************
class OpinionNodeTests(TestCase):

    # ******************************
    # OpinionNodeTests
    # ******************************
    def setUp(self):

        # setup
        random.seed(0)
        create_groups_and_permissions()
        create_reserved_nodes()
        create_categories()

        # create user(s)
        self.user = create_test_user(username='not_bob', password='1234')
        self.bob = create_test_user(username='bob', password='1234')

        # create data
        self.theory = create_test_theory(created_by=self.user)
        self.subtheory = create_test_subtheory(
            parent_theory=self.theory, created_by=self.user)
        self.evidence = create_test_evidence(
            parent_theory=self.subtheory, created_by=self.user)
        self.fact = create_test_evidence(
            parent_theory=self.theory, title='Fact', fact=True, created_by=self.user)
        self.fiction = create_test_evidence(
            parent_theory=self.theory, title='Fiction', fact=False, created_by=self.user)
        self.opinion = create_test_opinion(
            theory=self.theory, user=self.user, nodes=True)
        self.sub_opinion = create_test_opinion(
            theory=self.subtheory, user=self.user, nodes=True)
        self.stats = self.theory.get_stats(Stats.TYPE.ALL)
        self.opinion_node = self.opinion.get_node(self.fact)

    # ******************************
    # OpinionNodeTests
    # ******************************
    def test_get_absolute_url(self):
        # blah
        opinion_node = self.opinion.get_node(self.fact)
        self.assertIsNone(opinion_node.get_absolute_url())

        # blah
        opinion_node = self.opinion.get_node(self.subtheory)
        self.assertIsNotNone(opinion_node.get_absolute_url())

    # ******************************
    # OpinionNodeTests
    # ******************************
    def test_url(self):
        # blah
        opinion_node = self.opinion.get_node(self.fact)
        self.assertIsNone(opinion_node.get_absolute_url())

        # blah
        opinion_node = self.opinion.get_node(self.subtheory)
        self.assertIsNotNone(opinion_node.get_absolute_url())

    # ******************************
    # OpinionNodeTests
    # ******************************
    def test_get_root(self):
        # blah
        opinion_node = self.opinion.get_node(self.fact)
        self.assertIsNone(opinion_node.get_root())

        # blah
        opinion_node = self.opinion.get_node(self.subtheory)
        self.assertEqual(opinion_node.get_root(), self.sub_opinion)

    # ******************************
    # OpinionNodeTests
    # ******************************
    def test_tt_points(self):
        self.opinion_node.tt_points()
        # ToDo: more

    # ******************************
    # OpinionNodeTests
    # ******************************
    def test_tf_points(self):
        self.opinion_node.tf_points()
        # ToDo: more

    # ******************************
    # OpinionNodeTests
    # ******************************
    def test_ft_points(self):
        self.opinion_node.ft_points()
        # ToDo: more

    # ******************************
    # OpinionNodeTests
    # ******************************
    def test_ff_points(self):
        self.opinion_node.ff_points()
        # ToDo: more

    # ******************************
    # OpinionNodeTests
    # ******************************
    def test_true_points(self):
        self.opinion_node.true_points()
        # ToDo: more

    # ******************************
    # OpinionNodeTests
    # ******************************
    def test_false_points(self):
        self.opinion_node.false_points()
        # ToDo: more

    # ******************************
    # OpinionNodeTests
    # ******************************
    def test_is_deleted(self):

        # blah
        opinion_node = self.opinion.get_node(self.fact)
        self.assertFalse(opinion_node.is_deleted())

        # blah
        self.fact.delete()
        opinion_node = self.opinion.get_node(self.fact)
        self.assertTrue(opinion_node.is_deleted())

        # blah
        self.theory.remove_node(self.fiction)
        opinion_node = self.opinion.get_node(self.fiction)
        self.assertTrue(opinion_node.is_deleted())


# ************************************************************
# Stats Model Tests
#
#
#
#
#
#
#
#
# ************************************************************
class StatsTests(TestCase):

    # ******************************
    # StatsTests
    # ******************************
    def setUp(self):

        # setup
        random.seed(0)
        create_groups_and_permissions()
        create_reserved_nodes()
        create_categories()

        # create user(s)
        self.user = create_test_user(username='not_bob', password='1234')
        self.bob = create_test_user(username='bob', password='1234')

        # create data
        self.theory = create_test_theory(created_by=self.user)
        self.subtheory = create_test_subtheory(
            parent_theory=self.theory, created_by=self.user)
        self.evidence = create_test_evidence(
            parent_theory=self.subtheory, created_by=self.user)
        self.fact = create_test_evidence(
            parent_theory=self.theory, title='Fact', fact=True, created_by=self.user)
        self.fiction = create_test_evidence(
            parent_theory=self.theory, title='Fiction', fact=False, created_by=self.user)
        self.opinion = create_test_opinion(
            theory=self.theory, user=self.user, nodes=True)
        self.stats = self.theory.get_stats(Stats.TYPE.ALL)

    # ******************************
    # StatsTests
    # ******************************
    def test_str(self):
        self.assertIsNotNone(self.stats.__str__())

    # ******************************
    # StatsTests
    # ******************************
    def test_initialize(self):
        for stats in self.theory.get_all_stats():
            stats.delete()
        assert self.theory.stats.count() == 0

        # blah
        Stats.initialize(self.theory)
        stats = self.theory.get_all_stats()
        self.assertEqual(stats.count(), 4)

    # ******************************
    # StatsTests
    # ******************************
    def test_get_slug(self):
        self.assertEqual(Stats.get_slug(Stats.TYPE.ALL), 'all')

    # ******************************
    # StatsTests
    # ******************************
    def test_slug(self):
        self.assertEqual(self.stats.slug(), 'all')

    # ******************************
    # StatsTests
    # ******************************
    def test_get_owner(self):
        # blah
        self.assertEqual(self.stats.get_owner(), 'Everyone')

        # coverage
        for stats in self.theory.get_all_stats():
            stats.get_owner()

    # ******************************
    # StatsTests
    # ******************************
    def test_get_owner_long(self):
        # blah
        self.assertEqual(self.stats.get_owner_long(),
                         'Statistics for Everyone')

        # coverage
        for stats in self.theory.get_all_stats():
            stats.get_owner_long()

    # ******************************
    # StatsTests
    # ******************************
    def test_point_range(self):
        # blah
        self.assertEqual(self.stats.get_point_range(), (0.0, 1.0))

        # coverage
        for stats in self.theory.get_all_stats():
            stats.get_point_range()

    # ******************************
    # StatsTests
    # ******************************
    def test_get_node(self):
        # blah
        stats_node = self.stats.get_node(self.fact)
        self.assertIsNotNone(stats_node)

        # blah
        stats_node = self.stats.get_node(self.evidence, create=False)
        self.assertIsNone(stats_node)

        # blah
        stats_node = self.stats.get_node(self.evidence, create=True)
        self.assertIsNotNone(stats_node)

    # ******************************
    # StatsTests
    # ******************************
    def test_get_nodes(self):
        # blah
        nodes = self.stats.get_nodes(cache=False)
        self.assertEqual(nodes.count(), 4)
        self.assertFalse(hasattr(self.stats, 'saved_nodes'))

        # blah
        nodes = self.stats.get_nodes(cache=True)
        self.assertEqual(nodes.count(), 4)
        self.assertTrue(hasattr(self.stats, 'saved_nodes'))

    # ******************************
    # StatsTests
    # ******************************
    def test_get_flat_node(self):
        # blah
        stats_node = self.stats.get_flat_node(self.fact)
        self.assertIsNotNone(stats_node)

        # blah
        stats_node = self.stats.get_flat_node(self.evidence, create=False)
        self.assertIsNone(stats_node)

        # blah
        stats_node = self.stats.get_flat_node(self.evidence, create=True)
        self.assertIsNotNone(stats_node)

    # ******************************
    # StatsTests
    # ******************************
    def test_get_flat_nodes(self):
        # blah
        nodes = self.stats.get_flat_nodes(cache=False)
        self.assertEqual(nodes.count(), 3)
        self.assertFalse(hasattr(self.stats, 'saved_flat_nodes'))

        # blah
        nodes = self.stats.get_flat_nodes(cache=True)
        self.assertEqual(nodes.count(), 3)
        self.assertTrue(hasattr(self.stats, 'saved_flat_nodes'))

    # ******************************
    # StatsTests
    # ******************************
    def test_add_opinion(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.bob,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.fact,
            tt_input=20,
            tf_input=80,
        )
        self.stats.reset()
        opinion.update_points()
        assert self.stats.opinions.count() == 0

        # blah
        self.stats.add_opinion(opinion)
        self.assertEqual(self.stats.opinions.count(), 1)

    # ******************************
    # StatsTests
    # ******************************
    def test_remove_opinion(self):
        self.stats.remove_opinion(self.opinion)
        self.assertEqual(self.stats.opinions.count(), 0)
        self.assertEqual(self.stats.true_points(), 0.0)
        self.assertEqual(self.stats.false_points(), 0.0)
        # ToDo: more

    # ******************************
    # StatsTests
    # ******************************
    def test_cache(self):
        assert not hasattr(self.stats, 'saved_nodes')
        assert not hasattr(self.stats, 'saved_flat_nodes')

        # blah
        self.stats.cache(lazy=True)
        self.assertEqual(self.stats.saved_nodes.count(), 0)
        self.assertEqual(self.stats.saved_flat_nodes.count(), 0)

        # blah
        del self.stats.saved_nodes
        del self.stats.saved_flat_nodes
        self.stats.cache(lazy=False)
        self.assertEqual(self.stats.saved_nodes.count(), 4)
        self.assertEqual(self.stats.saved_flat_nodes.count(), 3)

    # ******************************
    # StatsTests
    # ******************************
    def test_save_changes(self):
        # setup
        true_points = self.stats.true_points()
        false_points = self.stats.false_points()
        assert true_points > 0
        assert false_points > 0

        # blah
        self.stats.reset(save=False)
        self.stats.refresh_from_db()
        self.assertEqual(self.stats.true_points(), true_points)
        self.assertEqual(self.stats.false_points(), false_points)

        # blah
        self.stats.reset(save=False)
        self.stats.save_changes()
        self.stats.refresh_from_db()
        self.assertEqual(self.stats.true_points(), 0.0)
        self.assertEqual(self.stats.false_points(), 0.0)

        # ToDo: more

    # ******************************
    # StatsTests
    # ******************************
    def test_total_points(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.bob,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.fact,
            tt_input=20,
            tf_input=80,
        )
        self.stats.reset()
        opinion.update_points()
        self.stats.add_opinion(opinion)

        # blah
        self.assertEqual(self.stats.total_points(), 1.0)

    # ******************************
    # StatsTests
    # ******************************
    def test_true_points(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.bob,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.fact,
            tt_input=20,
            tf_input=80,
        )
        self.stats.reset()
        opinion.update_points()
        self.stats.add_opinion(opinion)

        # blah
        self.assertEqual(self.stats.true_points(), 0.20)

    # ******************************
    # StatsTests
    # ******************************
    def test_false_points(self):
        # setup
        opinion = self.theory.opinions.create(
            user=self.bob,
        )
        opinion_node = opinion.nodes.create(
            theory_node=self.fact,
            tt_input=20,
            tf_input=80,
        )
        self.stats.reset()
        opinion.update_points()
        self.stats.add_opinion(opinion)

        # blah
        self.assertEqual(self.stats.false_points(), 0.80)

    # ******************************
    # StatsTests
    # ******************************
    def test_swap_true_false(self):
        # setup
        true_points = self.stats.true_points()
        false_points = self.stats.false_points()
        assert true_points != false_points

        # blah
        self.stats.swap_true_false()
        self.assertEqual(self.stats.true_points(), false_points)
        self.assertEqual(self.stats.false_points(), true_points)

        # ToDo: more

    # ******************************
    # StatsTests
    # ******************************
    def test_reset(self):
        assert self.stats.true_points() != 0
        assert self.stats.false_points() != 0
        self.stats.reset()
        self.assertEqual(self.stats.true_points(), 0)
        self.assertEqual(self.stats.false_points(), 0)
        # ToDo: test save

    # ******************************
    # StatsTests
    # ******************************
    def test_opinion_is_member(self):
        self.assertTrue(self.stats.opinion_is_member(self.opinion))

    # ******************************
    # StatsTests
    # ******************************
    def test_get_opinions(self):
        self.assertIn(self.opinion, self.stats.get_opinions())

    # ******************************
    # StatsTests
    # ******************************
    def test_url(self):
        self.assertIsNotNone(self.stats.url())

    # ******************************
    # StatsTests
    # ******************************
    def test_compare_url(self):
        self.assertIsNotNone(self.stats.compare_url())


# ************************************************************
# StatsNodeTests
#
#
#
#
#
#
# ************************************************************
class StatsNodeTests(TestCase):

    # ******************************
    # StatsNodeTests
    # ******************************
    def setUp(self):

        # setup
        random.seed(0)
        create_groups_and_permissions()
        create_reserved_nodes()
        create_categories()

        # create user(s)
        self.user = create_test_user(username='not_bob', password='1234')
        self.bob = create_test_user(username='bob', password='1234')

        # create data
        self.theory = create_test_theory(created_by=self.user)
        self.subtheory = create_test_subtheory(
            parent_theory=self.theory, created_by=self.user)
        self.evidence = create_test_evidence(
            parent_theory=self.subtheory, created_by=self.user)
        self.fact = create_test_evidence(
            parent_theory=self.theory, title='Fact', fact=True, created_by=self.user)
        self.fiction = create_test_evidence(
            parent_theory=self.theory, title='Fiction', fact=False, created_by=self.user)
        self.opinion = create_test_opinion(
            theory=self.theory, user=self.user, nodes=True)
        self.stats = self.theory.get_stats(Stats.TYPE.ALL)
        self.stats_node = self.stats.get_node(self.fact)

    # ******************************
    # StatsNodeTests
    # ******************************
    def test_url(self):
        # blah
        stats_node = self.stats.get_node(self.fact)
        self.assertIsNone(stats_node.url())

        # blah
        stats_node = self.stats.get_node(self.subtheory)
        self.assertIsNotNone(stats_node.url())

    # ******************************
    # StatsNodeTests
    # ******************************
    def test_get_root(self):
        # blah
        stats_node = self.stats.get_node(self.fact)
        self.assertIsNone(stats_node.get_root())

        # blah
        stats_node = self.stats.get_node(self.subtheory)
        self.assertIsNotNone(stats_node.get_root())

    # ******************************
    # StatsNodeTests
    # ******************************
    def test_true_points(self):
        self.stats_node.true_points()
        # ToDo: more

    # ******************************
    # StatsNodeTests
    # ******************************
    def test_false_points(self):
        self.stats_node.false_points()
        # ToDo: more

    # ******************************
    # StatsNodeTests
    # ******************************
    def test_total_points(self):
        self.stats_node.total_points()
        # ToDo: more

    # ******************************
    # StatsNodeTests
    # ******************************
    def test_reset(self, save=True):
        assert self.stats_node.true_points() != 0.0
        assert self.stats_node.false_points() != 0.0
        self.stats_node.reset()
        self.assertEqual(self.stats_node.true_points(), 0.0)
        self.assertEqual(self.stats_node.false_points(), 0.0)


# ************************************************************
# StatsFlatNodeTests
#
#
#
#
#
#
# ************************************************************
class StatsFlatNodeTests(TestCase):

    # ******************************
    # StatsFlatNodeTests
    # ******************************
    def setUp(self):

        # setup
        random.seed(0)
        create_groups_and_permissions()
        create_reserved_nodes()
        create_categories()

        # create user(s)
        self.user = create_test_user(username='not_bob', password='1234')
        self.bob = create_test_user(username='bob', password='1234')

        # create data
        self.theory = create_test_theory(created_by=self.user)
        self.subtheory = create_test_subtheory(
            parent_theory=self.theory, created_by=self.user)
        self.evidence = create_test_evidence(
            parent_theory=self.subtheory, created_by=self.user)
        self.fact = create_test_evidence(
            parent_theory=self.theory, title='Fact', fact=True, created_by=self.user)
        self.fiction = create_test_evidence(
            parent_theory=self.theory, title='Fiction', fact=False, created_by=self.user)
        self.opinion = create_test_opinion(
            theory=self.theory, user=self.user, nodes=True)
        self.stats = self.theory.get_stats(Stats.TYPE.ALL)
        self.stats_node = self.stats.get_flat_node(self.fact)

    # ******************************
    # StatsFlatNodeTests
    # ******************************
    def test_url(self):
        stats_node = self.stats.get_flat_node(self.fact)
        self.assertIsNone(stats_node.url())

    # ******************************
    # StatsFlatNodeTests
    # ******************************
    def test_get_root(self):
        stats_node = self.stats.get_flat_node(self.fact)
        self.assertIsNone(stats_node.get_root())

    # ******************************
    # StatsFlatNodeTests
    # ******************************
    def test_true_points(self):
        self.stats_node.true_points()
        # ToDo: more

    # ******************************
    # StatsFlatNodeTests
    # ******************************
    def test_false_points(self):
        self.stats_node.false_points()
        # ToDo: more

    # ******************************
    # StatsFlatNodeTests
    # ******************************
    def test_total_points(self):
        self.stats_node.total_points()
        # ToDo: more

    # ******************************
    # StatsFlatNodeTests
    # ******************************
    def test_reset(self, save=True):
        assert self.stats_node.true_points() != 0.0
        assert self.stats_node.false_points() != 0.0
        self.stats_node.reset()
        self.assertEqual(self.stats_node.true_points(), 0.0)
        self.assertEqual(self.stats_node.false_points(), 0.0)


# ************************************************************
# TheoryPointerBaseTests
#
#
#
#
#
#
#
# ************************************************************
class TheoryPointerBaseTests(TestCase):

    # ******************************
    # TheoryPointerBaseTests
    # ******************************
    def setUp(self):

        # setup
        random.seed(0)
        create_groups_and_permissions()
        create_reserved_nodes()
        create_categories()

        # create user(s)
        self.user = create_test_user(username='not_bob', password='1234')
        self.bob = create_test_user(username='bob', password='1234')

        # create data
        self.theory = create_test_theory(created_by=self.user)
        self.subtheory = create_test_subtheory(
            parent_theory=self.theory, created_by=self.user)
        self.evidence = create_test_evidence(
            parent_theory=self.subtheory, created_by=self.user)
        self.fact = create_test_evidence(
            parent_theory=self.theory, title='Fact', fact=True, created_by=self.user)
        self.fiction = create_test_evidence(
            parent_theory=self.theory, title='Fiction', fact=False, created_by=self.user)
        self.opinion = create_test_opinion(
            theory=self.theory, user=self.user, nodes=True)
        self.stats = self.theory.get_stats(Stats.TYPE.ALL)
        self.stats_node = self.stats.get_flat_node(self.fact)

    # ******************************
    # TheoryPointerBaseTests
    # ******************************
    def test_create(self):
        pass

    # ******************************
    # TheoryPointerBaseTests
    # ******************************

    def test_check_data(self):
        pass

    # ******************************
    # TheoryPointerBaseTests
    # ******************************

    def test_str(self):
        pass

    # ******************************
    # TheoryPointerBaseTests
    # ******************************

    def test_url(self):
        pass

    # ******************************
    # TheoryPointerBaseTests
    # ******************************

    def test_compare_url(self):
        pass

    # ******************************
    # TheoryPointerBaseTests
    # ******************************

    def test_get_node_id(self):
        pass

    # ******************************
    # TheoryPointerBaseTests
    # ******************************

    def test_get_nodes(self):
        pass

    # ******************************
    # TheoryPointerBaseTests
    # ******************************

    def test_get_flat_nodes(self):
        pass

    # ******************************
    # TheoryPointerBaseTests
    # ******************************

    def test_get_point_distribution(self):
        pass

    # ******************************
    # TheoryPointerBaseTests
    # ******************************

    def test_true_points(self):
        pass

    # ******************************
    # TheoryPointerBaseTests
    # ******************************

    def test_false_points(self):
        pass

    # ******************************
    # TheoryPointerBaseTests
    # ******************************

    def test_is_true(self):
        pass

    # ******************************
    # TheoryPointerBaseTests
    # ******************************

    def test_is_false(self):
        pass

    # ******************************
    # TheoryPointerBase
    # ******************************

    def test_get_point_range(self):
        pass


# ************************************************************
# NodePointerBaseTests
#
#
#
#
#
#
#
# ************************************************************
class NodePointerBaseTests(TestCase):

    # ******************************
    # TheoryPointerBaseTests
    # ******************************
    def setUp(self):

        # setup
        random.seed(0)
        create_groups_and_permissions()
        create_reserved_nodes()
        create_categories()

        # create user(s)
        self.user = create_test_user(username='not_bob', password='1234')
        self.bob = create_test_user(username='bob', password='1234')

        # create data
        self.theory = create_test_theory(created_by=self.user)
        self.subtheory = create_test_subtheory(
            parent_theory=self.theory, created_by=self.user)
        self.evidence = create_test_evidence(
            parent_theory=self.subtheory, created_by=self.user)
        self.fact = create_test_evidence(
            parent_theory=self.theory, title='Fact', fact=True, created_by=self.user)
        self.fiction = create_test_evidence(
            parent_theory=self.theory, title='Fiction', fact=False, created_by=self.user)
        self.opinion = create_test_opinion(
            theory=self.theory, user=self.user, nodes=True)
        self.stats = self.theory.get_stats(Stats.TYPE.ALL)
        self.stats_node = self.stats.get_flat_node(self.fact)

    # ******************************
    # NodePointerBaseTests
    # ******************************
    def test_create(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_str(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_get_true_statement(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_get_false_statement(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_get_node_id(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_tag_id(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_about(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_url(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_is_theory(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_is_subtheory(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_is_evidence(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_is_fact(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_is_verifiable(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_true_points(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_false_points(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_total_points(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_true_percent(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_false_percent(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************
    def test_true_ratio(self):
        pass

    # ******************************
    # NodePointerBaseTests
    # ******************************

    def test_false_ratio(self):
        pass