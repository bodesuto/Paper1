# Classifier Module — Question Cllassification for Memory Retrieval

## Overview

The **Classifier module** performs structured question understanding to support memory retrieval in the dual-memory architecture.

Its purpose is to extract lightweight semantic metadata from a question so that the memory layer can retrieve relevant prior reasoning traces and knowledge graph nodes.

It produces descriptors (intent, attributes, entities) that improve memory selection.

This module corresponds to the **Vocabulary-Based query and data classification** section.

## Outputs

For each question the module returns metadata:

```python
{
  "intent": "...",        # reasoning pattern label
  "attributes": [...],    # semantic/domain tags
  "entities": [...]       # key concepts
}
```

This metadata is stored alongside traces and used during retrieval.

## Directory Structure

```
classifier/
├── src/
│   └── classifier.py
└── prompts/
    └── classifier_prompts.py
```

## Usage Examples

option 1. Use the script `scripts/run_classify.py`.
```
scripts/run_classify.py
```

option 2. Code

```
from classifier.prompts.classifier import classify_hotpot_vocab

vocab = classify_hotpot_vocab(question)
```