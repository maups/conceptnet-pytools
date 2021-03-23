from conceptnet import ConceptNet

cnet = ConceptNet()

print(cnet.get_embedding('headset'))

print(cnet.query_concept('headset'))

print(cnet.query_concept('headset', directed=True))

print(cnet.query_edge('hand', 'arm'))

print(cnet.query_edge('hand', 'arm', directed=True))

print(cnet.query_edge('arm', 'hand', directed=True))

