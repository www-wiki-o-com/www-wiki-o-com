"""  __      __    __               ___
    /  \    /  \__|  | _ __        /   \
    \   \/\/   /  |  |/ /  |  __  |  |  |
     \        /|  |    <|  | |__| |  |  |
      \__/\__/ |__|__|__\__|       \___/

Copyright (C) 2018 Wiki-O, Frank Imeson

This source code is licensed under the GPL license found in the
LICENSE.md file in the root directory of this source tree.
"""

# *******************************************************************************
# Imports
# *******************************************************************************
from .views00 import *


# ************************************************************
# Max level user
#
#
#
#
#
# ************************************************************
class Level04UserViews(TestCase, ViewsTestBase):
    fixtures = ['groups.json']

    # ******************************
    # Setup - Level04User
    # ******************************
    def setUp(self):
        # create user(s)
        self.user = create_test_user(username='testuser', password='1234', level=4)
        self.client.login(username='testuser', password='1234')

        # create data
        super().create_data(user=self.user)

    # ******************************
    # Login - Level04User
    # ******************************
    def test_login(self):
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user, self.user)
        self.assertTrue(user.has_perm('theories.add_theorynode'))
        self.assertTrue(user.has_perm('theories.change_theorynode'))
        self.assertTrue(user.has_perm('theories.delete_theorynode'))

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_index(self):
        super().test_get_index(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_index_category(self):
        super().test_get_index_category(
            override=True,
            category='legal',
        )

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_activity(self):
        super().test_get_activity(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_theory_create(self):
        super().test_get_theory_create(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_theory_detail(self):
        super().test_get_theory_detail(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_theory_edit(self):
        super().test_get_theory_edit(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_theory_merge(self):
        super().test_get_theory_merge(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_theory_backup(self):
        super().test_get_theory_backup(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_theory_restore(self):
        super().test_get_theory_restore(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_theory_activity(self):
        super().test_get_theory_activity(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_theory_edit_evidence(self):
        super().test_get_theory_edit_evidence(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_theory_edit_subtheories(self):
        super().test_get_theory_edit_subtheories(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_theory_inherit(self):
        pass  # TODO
        # super().test_get_theory_inherit(
        #     override=True,
        # )

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_evidence_detail(self):
        super().test_get_evidence_detail(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_evidence_edit(self):
        super().test_get_evidence_edit(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_evidence_merge(self):
        super().test_get_evidence_merge(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_evidence_restore(self):
        super().test_get_evidence_restore(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_evidence_activity(self):
        super().test_get_evidence_activity(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_opinion_demo(self):
        super().test_get_opinion_demo(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_opinion_detail(self):
        super().test_get_opinion_detail(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_my_opinion(self):
        super().test_get_my_opinion(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_opinion_edit(self):
        super().test_get_opinion_edit(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_opinion_slug(self):
        super().test_get_opinion_slug(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_user_vs_user(self):
        super().test_get_user_vs_user(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_user_vs_slug(self):
        super().test_get_user_vs_slug(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_slug_vs_user(self):
        super().test_get_slug_vs_user(override=True,)

    # ******************************
    # Get - Level04User
    # ******************************
    def test_get_slug_vs_slug(self):
        super().test_get_slug_vs_slug(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_create(self):
        super().test_post_theory_create(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_edit(self):
        super().test_post_theory_edit(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_merge(self):
        super().test_post_theory_merge(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_backup(self):
        super().test_post_theory_backup(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_delete_backup(self):
        super().test_post_theory_delete_backup(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_edit_evidence(self):
        super().test_post_theory_edit_evidence(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_edit_subtheories(self):
        super().test_post_theory_edit_subtheories(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_new_evidence(self):
        super().test_post_theory_new_evidence(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_new_subtheories(self):
        super().test_post_theory_new_subtheories(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_inherit(self):
        pass  # TODO
        # super().test_post_theory_inherit(
        #     override=True,
        # )

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_delete(self):
        super().test_post_theory_delete(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_convert01(self):
        super().test_post_theory_convert01(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_convert02(self):
        super().test_post_theory_convert02(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_revert(self):
        super().test_post_theory_revert(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_add_to_home(self):
        super().test_post_theory_add_to_home(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_theory_remove_from_home(self):
        super().test_post_theory_remove_from_home(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_evidence_edit(self):
        super().test_post_evidence_edit(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_evidence_merge(self):
        super().test_post_evidence_merge(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_evidence_delete_backup(self):
        super().test_post_evidence_delete_backup(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_evidence_delete(self):
        super().test_post_evidence_delete(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_evidence_backup(self):
        super().test_post_evidence_backup(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_evidence_convert(self):
        super().test_post_evidence_convert(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_evidence_revert(self):
        super().test_post_evidence_revert(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_opinion_new(self):
        super().test_post_opinion_new(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_opinion_edit(self):
        super().test_post_opinion_edit(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_delete_my_opinion(self):
        super().test_post_delete_my_opinion(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_delete_bobs_opinion(self):
        super().test_post_delete_bobs_opinion(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_opinion_copy(self):
        super().test_post_opinion_copy(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_hide_my_opinion(self):
        super().test_post_hide_my_opinion(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_hide_bobs_opinion(self):
        super().test_post_hide_bobs_opinion(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_reveal_my_opinion(self):
        super().test_post_reveal_my_opinion(override=True,)

    # ******************************
    # Post - Level04User
    # ******************************
    def test_post_reveal_bobs_opinion(self):
        super().test_post_reveal_bobs_opinion(override=True,)
