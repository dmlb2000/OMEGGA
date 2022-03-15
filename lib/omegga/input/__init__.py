#!/usr/bin/python
import csv
from collections import namedtuple
from pandas import DataFrame

ReactionRelations = namedtuple('ReactionRelations', ['reaction', 'protein', 'transcript', 'metabolite'])

def generate_input(genome_ref, metabolomics_ref, events) -> DataFrame:
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
    
    cpd_to_rxn = {}
    with open('/kb/module/data/reactions.tsv') as rxn_fd:
        rxn_reader = csv.DictReader(rxn_fd, delimiter='\t')
        for rxn_dict in rxn_reader:
            for cpd_id in rxn_dict.get('compound_ids').split(';'):
                if cpd_id not in cpd_to_rxn:
                    cpd_to_rxn[cpd_id] = []
                cpd_to_rxn[cpd_id].append(rxn_dict.get('id'))
    for cpd_id in metabolomics_ref.get('data').get('data').get('row_ids'):
        if cpd_id in cpd_to_rxn:
            for rxn_id in cpd_to_rxn[cpd_id]:
                if rxn_id not in data:
                    data[rxn_id] = ReactionRelations(rxn_id, [], [], [])
                data[rxn_id].metabolite.append(cpd_id)
    return DataFrame({
        'reaction': [rxn.reaction for rxn in data.values()],
        'protein': [';'.join(rxn.protein) for rxn in data.values()],
        'transcript': [';'.join(rxn.transcript) for rxn in data.values()],
        'metabolite': [';'.join(rxn.metabolite) for rxn in data.values()],
    })
