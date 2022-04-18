# -*- coding: utf-8 -*-
import os
import time
import unittest
import shutil
from configparser import ConfigParser
from unittest.mock import MagicMock

from omegga.omeggaImpl import omegga
from omegga.omeggaServer import MethodContext
from omegga.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class omeggaTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('omegga'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'omegga',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = omegga(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_your_method(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        print('='*80)
        print(self.scratch)
        self.serviceImpl.dfu.download_staging_file = MagicMock(
            side_effect=[
                '/kb/module/test/test_data/protein_reaction_map.csv',
                '/kb/module/test/test_data/transcript_reaction_map.csv'
            ]
        )
        ret = self.serviceImpl.run_omegga(self.ctx, {
            'workspace_name': self.wsName,
            'genome_ref': '66294/5/3',
            'metabolomics_ref': '65432/19/4',
            'staging_file_path_proteins': 'protein_reaction_map.csv',
            'staging_file_path_transcripts': 'transcript_reaction_map.csv',
        })
