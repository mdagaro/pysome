# Come back later to see what things in particular we need
from maybe import maybe
from collections.abc import Mapping


class SomeTrie(Mapping):
    """
    A basic trie class.
    """

    def __init__(self, subtries=None):
        if subtries is None:
            subtries = {}
        self.subtries = maybe(subtries)

    def __len__(self):
        return len(self.subtries)

    def __iter__(self):
        return iter(self.subtries)

    def __getitem__(self, char):
        if len(char) <= 1:
            return self.subtries[char]
        return self.subtries[char[0]][char[1:]]

    def __contains__(self, word):
        return self[word].is_some()

    def _getsubtrie(self, char):
        return self.subtries[char]

    @staticmethod
    def from_list(words):
        this = SomeTrie()
        for word in words:
            this.insert(word)
        return this

    def insert(self, word):
        if word == "":
            return self
        subtrie = self._getsubtrie(word[0]).some_or_else(SomeTrie())
        subtrie = subtrie.insert(word[1:])
        self.subtries[word[0]] = subtrie
        return self

    def __str__(self):
        return str(self.subtries)

    __repr__ = __str__
