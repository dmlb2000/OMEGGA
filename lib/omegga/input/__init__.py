#!/usr/bin/python
import csv
from collections import namedtuple
from pandas import DataFrame

ReactionRelations = namedtuple('ReactionRelations', ['reaction', 'protein', 'transcript', 'metabolite'])

def _build_cpd_to_rxn():
    cpd_to_rxn = {}
    with open('/kb/module/data/reactions.tsv') as rxn_fd:
        rxn_reader = csv.DictReader(rxn_fd, delimiter='\t')
        for rxn_dict in rxn_reader:
            for cpd_id in rxn_dict.get('compound_ids').split(';'):
                if cpd_id not in cpd_to_rxn:
                    cpd_to_rxn[cpd_id] = []
                cpd_to_rxn[cpd_id].append(rxn_dict.get('id'))
    return cpd_to_rxn

CPD_TO_RXN = _build_cpd_to_rxn()

def generate_input(genome_ref, metabolomics_ref, events, transcript_expressionmatrix_ref, protein_expressionmatrix_ref) -> DataFrame:
    data = {}
    # loop over genome proteins and transcripts
    for protein in genome_ref.get('data').get('cdss'):
        for event in events.get('events'):
            if protein.get('id') in event.get('ontology_terms') and 'modelseed_ids' in event.get('ontology_terms').get(protein.get('id'))[0]:
                for reaction in event.get('ontology_terms').get(protein.get('id'))[0].get('modelseed_ids'):
                    rxn_id = reaction.split(':')[1]
                    if rxn_id not in data:
                        data[rxn_id] = ReactionRelations(rxn_id, [], [], [])
                    data[rxn_id].protein.append(protein.get('id'))
                    data[rxn_id].transcript.append(protein.get('parent_mrna'))
    transcript_data = transcript_expressionmatrix_ref.get('data').get('data')
    for rxn_index in range(len(transcript_data.get('row_ids'))):
        for ts_index in range(len(transcript_data.get('col_ids'))):
            rxn_id = transcript_data.get('row_ids')[rxn_index]
            value = transcript_data.get('values')[rxn_index][ts_index]
            if value > 0:
                if rxn_id not in data:
                    data[rxn_id] = ReactionRelations(rxn_id, [], [], [])
                data[rxn_id].transcript.append(transcript_data.get('col_ids')[ts_index])
    protein_data = protein_expressionmatrix_ref.get('data').get('data')
    for rxn_index in range(len(protein_data.get('row_ids'))):
        for protein_index in range(len(protein_data.get('col_ids'))):
            rxn_id = protein_data.get('row_ids')[rxn_index]
            value = protein_data.get('values')[rxn_index][protein_index]
            if value > 0:
                if rxn_id not in data:
                    data[rxn_id] = ReactionRelations(rxn_id, [], [], [])
                data[rxn_id].protein.append(protein_data.get('col_ids')[protein_index])
    for cpd_id in metabolomics_ref.get('data').get('data').get('row_ids'):
        if cpd_id in CPD_TO_RXN:
            for rxn_id in CPD_TO_RXN[cpd_id]:
                if rxn_id not in data:
                    data[rxn_id] = ReactionRelations(rxn_id, [], [], [])
                data[rxn_id].metabolite.append(cpd_id)
    data_list = list(data.values())
    return DataFrame({
        'reaction': [rxn.reaction for rxn in data_list],
        'protein': [';'.join(rxn.protein) for rxn in data_list],
        'transcript': [';'.join(rxn.transcript) for rxn in data_list],
        'metabolite': [';'.join(rxn.metabolite) for rxn in data_list],
    })
