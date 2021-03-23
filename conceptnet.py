#################
# author: maups #
#################
import os
import numpy as np
from tqdm import tqdm

# ConceptNet & NumberBatch query tools
class ConceptNet:
	# constructor
	def __init__(self, conceptnet_filename='conceptnet-en-5.7.0.txt', numberbatch_filename='numberbatch-en-19.08.txt', remove_duplicate=False, remove_dangling=True):
		self.valid_assertions = set([
			'RelatedTo', 'FormOf', 'PartOf', 'HasA', 'UsedFor', 'CapableOf', 'AtLocation', 'Causes', 'HasSubevent',
			'HasFirstSubevent', 'HasLastSubevent', 'HasPrerequisite', 'HasProperty', 'MotivatedByGoal',
			'ObstructedBy', 'Desires', 'CreatedBy', 'Synonym', 'Antonym', 'DistinctFrom', 'DerivedFrom', 'SymbolOf',
			'DefinedAs', 'MannerOf', 'LocatedNear', 'HasContext', 'SimilarTo', 'EtymologicallyRelatedTo',
			'EtymologicallyDerivedFrom', 'CausesDesire', 'MadeOf', 'ReceivesAction', 'ExternalURL', 'NotIsA',
			'NotDesires', 'NotUsedFor', 'NotCapableOf', 'NotHasProperty'
		])
		self.symmetric_assertions = set([
			'RelatedTo', 'Synonym', 'Antonym', 'DistinctFrom', 'LocatedNear', 'SimilarTo', 'EtymologicallyRelatedTo'
		])

		# NumberBatch embeddings for concepts
		self.concepts = {}

		# ConceptNet graph structure
		self.inbonds = {}
		self.outbonds = {}
		self.edge_weights = {}

		# Load NumberBatch
		print('Loading NumberBatch embeddings...')
		self.__load_numberbatch(numberbatch_filename, remove_duplicate)
		print('Done!\n')

		# Load ConceptNet
		print('Loading ConceptNet edges...')
		self.__load_conceptnet(conceptnet_filename, remove_dangling)
		print('Done!\n')

	###########
	# PRIVATE #
	###########

	# NumberBatch stuff
	def __load_numberbatch(self, filename, remove_duplicate):
		with open(filename, 'r') as f_in:
			known_embeddings = {}
			num_concepts, embedding_size = [int(x) for x in f_in.readline().split()]
			for i in tqdm(range(num_concepts)):
				elem = f_in.readline().split()

				# parse concept & embedding
				concept = elem[0]
				embedding = np.asarray(elem[1:], dtype=np.float32)
				assert embedding_size == len(embedding)

				# keep 1st concept per embedding, discard the rest
				if remove_duplicate:
					# use first element of array as 'hash'
					if embedding[0] not in known_embeddings:
						known_embeddings[embedding[0]] = [concept]
						self.concepts[concept] = embedding
					else:
						flag = True
						for c in known_embeddings[embedding[0]]:
							if np.array_equal(embedding, self.concepts[c]):
								flag = False
								break
						if flag:
							known_embeddings[embedding[0]].append(concept)
							self.concepts[concept] = embedding
				# keep all embeddings
				else:
					self.concepts[concept] = embedding

	# ConceptNet stuff
	def __add_outbond(self, elem):
		if elem[1] not in self.outbonds:
			self.outbonds[elem[1]] = {}
		if elem[2] not in self.outbonds[elem[1]]:
			self.outbonds[elem[1]][elem[2]] = {}
		if elem[0] not in self.outbonds[elem[1]][elem[2]]:
			self.outbonds[elem[1]][elem[2]][elem[0]] = 0.0
		# for duplicate edges, keep the one with maximum weight
		self.outbonds[elem[1]][elem[2]][elem[0]] = max(self.outbonds[elem[1]][elem[2]][elem[0]], float(elem[3]))

	def __add_inbond(self, elem):
		if elem[1] not in self.inbonds:
			self.inbonds[elem[1]] = {}
		if elem[2] not in self.inbonds[elem[1]]:
			self.inbonds[elem[1]][elem[2]] = {}
		if elem[0] not in self.inbonds[elem[1]][elem[2]]:
			self.inbonds[elem[1]][elem[2]][elem[0]] = 0.0
		# for duplicate edges, keep the one with maximum weight
		self.inbonds[elem[1]][elem[2]][elem[0]] = max(self.inbonds[elem[1]][elem[2]][elem[0]], float(elem[3]))

	def __load_conceptnet(self, filename, remove_dangling):
		size = os.stat(filename).st_size
		with open(filename, 'r') as f_in:
			pbar = tqdm(total=size)
			line = f_in.readline()
			while line:
				elem = line.split('\t')

				# if 'remove_dangling' is True, ignore edges for concepts without a NumberBatch embedding
				if elem[0] in self.valid_assertions and (not remove_dangling or (elem[1] in self.concepts and elem[2] in self.concepts)):
					self.__add_outbond(elem)
					if elem[0] in self.symmetric_assertions:
						self.__add_outbond([elem[0],elem[2],elem[1],elem[3]])
					else:
						self.__add_inbond([elem[0],elem[2],elem[1],elem[3]])

				pbar.update(len(line))
				line = f_in.readline()
			pbar.close()

	# convert edge tree to list
	def __edge_list(self, concept1, edges, flip=False):
		l = []
		for concept2, rels in edges.items():
			for rel, w in rels.items():
				if flip:
					l.append([concept2, rel, concept1, w])
				else:
					l.append([concept1, rel, concept2, w])
		return l

	# return ConceptNet edges 'from' a query concept to any other concept
	def __get_outbonds(self, concept):
		if concept in self.outbonds:
			return self.__edge_list(concept, self.outbonds[concept])
		else:
			return []

	# return ConceptNet edges from any other concept 'to' a query concept (excluding symmetric edges, which appear as outbonds)
	def __get_inbonds(self, concept):
		if concept in self.inbonds:
			return self.__edge_list(concept, self.inbonds[concept], True)
		else:
			return []

	##########
	# PUBLIC #
	##########

	# return NumberBatch embedding for a query concept
	def get_embedding(self, concept):
		if concept not in self.concepts:
			return None
		return self.concepts[concept]

	# get all edges for a concept
	def query_concept(self, concept, directed=False):
		if directed:
			return {'out': self.__get_outbonds(concept)}
		else:
			return {'out': self.__get_outbonds(concept), 'in': self.__get_inbonds(concept)}

	# get all edges between two concepts
	def query_edge(self, concept1, concept2, directed=False):
		l = []
		if concept1 in self.outbonds and concept2 in self.outbonds[concept1]:
			for rel, w in self.outbonds[concept1][concept2].items():
				l.append([concept1, rel, concept2, w])
		# this function does not repeat symmetric edges
		if not directed and concept1 in self.inbonds and concept2 in self.inbonds[concept1]:
			for rel, w in self.inbonds[concept1][concept2].items():
				l.append([concept2, rel, concept1, w])
		return l

