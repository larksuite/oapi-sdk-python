from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.document: Document = Document(config)
        self.document_block: DocumentBlock = DocumentBlock(config)
        self.document_block_children: DocumentBlockChildren = DocumentBlockChildren(config)
        self.document_block_descendant: DocumentBlockDescendant = DocumentBlockDescendant(config)
