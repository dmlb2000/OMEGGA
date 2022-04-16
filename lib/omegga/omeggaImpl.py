# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.annotation_ontology_apiClient import annotation_ontology_api
from .report import generate_report
from .input import generate_input
#END_HEADER


class omegga:
    '''
    Module Name:
    omegga

    Module Description:
    A KBase module: omegga
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "ssh://git@gitlab.pnnl.gov:2222/sfa-omegga/omegga.git"
    GIT_COMMIT_HASH = "64736ef69ba5f23fdc138236d2ec76253c71ff36"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        self.workspace_url = config['workspace-url']
        self.scratch = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_omegga(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_omegga
        dfu = DataFileUtil(self.callback_url)
        genome_ref, metabolomics_ref = dfu.get_objects({'object_refs':
            [params['genome_ref'], params['metabolomics_ref']]
        })['data']
        protein_reaction_file_path = None
        if 'staging_file_path_proteins' in params:
            protein_reaction_file_path = dfu.download_staging_file({
                "staging_file_subdir_path": params['staging_file_path_proteins']
            })
        transcript_reaction_file_path = None
        if 'staging_file_path_transcripts' in params:
            transcript_reaction_file_path = dfu.download_staging_file({
                "staging_file_subdir_path": params['staging_file_path_transcripts']
            })
        
        # When the app becomes released production 'service_ver' will be removed...
        events = annotation_ontology_api(service_ver='dev').get_annotation_ontology_events(params={
                "input_ref": params['genome_ref'],
                "input_workspace": params['workspace_name'],
                "workspace-url"  : self.workspace_url
        })
        input_df = generate_input(genome_ref, metabolomics_ref, events)
        report = KBaseReport(self.callback_url)
        report_info = report.create_extended_report({
            'objects_created':[],
            'html_links': generate_report(dfu, self.scratch, {
                'rows': input_df.to_dict(orient='records'),
                'columns': input_df.columns.to_list()
            }),
            'direct_html_link_index': 0,
            'workspace_name': params['workspace_name'],
        })
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END run_omegga

        # At some point might do deeper type checking...
        if not isinstance(output, dict):  # pragma: no cover
            raise ValueError('Method run_omegga return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):  # pragma: no cover
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
