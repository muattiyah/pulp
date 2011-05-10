#!/usr/bin/python
#
# Copyright (c) 2010 Red Hat, Inc.
#
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.

# Python
import os
import sys
import unittest

# Pulp
srcdir = os.path.abspath(os.path.dirname(__file__)) + "/../../src/"
sys.path.insert(0, srcdir)

commondir = os.path.abspath(os.path.dirname(__file__)) + '/../common/'
sys.path.insert(0, commondir)

import mocks
import pulp.server.api.repo
import pulp.server.api.repo_sync as repo_sync
import pulp.server.crontab
import testutil

class TestRepoPublish(unittest.TestCase):

    def setUp(self):
        mocks.install()
        self.config = testutil.load_test_config()
        self.repo_api = pulp.server.api.repo.RepoApi()
        self.data_path = \
            os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")

    def tearDown(self):
        self.repo_api.clean()
        testutil.common_cleanup()

    def test_repo_publish(self):
        # Setup
        repo_id = 'test_repo_publish'
        repo_path = os.path.join(self.data_path, "repo_resync_a")
        repo = self.repo_api.create(repo_id, 'Repo Publish', 'noarch', 
                'file://%s' % (repo_path))
        # Verify that repo 'published' defaulted to whatever is in config
        self.assertEquals(repo["publish"], 
                self.config.getboolean('repos', 'default_to_published'))
        # Sync Repo
        self.repo_api._sync(repo["id"])
        repo = self.repo_api.repository(repo_id)

        # Ensure Repo is Published
        if not repo["publish"]:
            self.repo_api.publish(repo, True)
        repo = self.repo_api.repository(repo_id)
        self.assertTrue(repo["publish"])
        # Verify symlink exists for published repo
        expected_link = os.path.join(self.repo_api.published_path,
            repo['relative_path'])
        self.assertTrue(os.path.islink(expected_link))

        # Disable publish on repo
        self.repo_api.publish(repo_id, False)
        repo = self.repo_api.repository(repo_id)
        self.assertFalse(repo["publish"])
        # Verify symlink does not exist
        self.assertFalse(os.path.islink(expected_link))

