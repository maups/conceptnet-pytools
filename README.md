# conceptnet-pytools
Python tools to query ConceptNet assertions and NumberBatch embeddings.

## Setup

Get ConceptNet assertions and NumberBatch embeddings:

```
$ python3 get_data.py
```

Check if everything is working:

```
$ python3 test.py
```

## How to use ```conceptnet.py```

Import class and load assertions+embeddings:

```
from conceptnet import ConceptNet
cnet = ConceptNet()
```

Get embedding for a specific concept:

```
embedding = cnet.get_embedding('headset')
```

Get assertions for a specific concept (including assertions originating from other concepts -- *ConceptNet assertions are directed*):

```
assertions = cnet.query_concept('headset')
```

Get assertions originating from a specific concept to any other concept:

```
print(cnet.query_concept('headset', directed=True))
```

Get all assertions between two concepts (in any direction):

```
print(cnet.query_edge('hand', 'arm'))
```

Get all assertions from one concept to another concept:

```
print(cnet.query_edge('hand', 'arm', directed=True))
print(cnet.query_edge('arm', 'hand', directed=True))
```
