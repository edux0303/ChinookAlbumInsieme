from dataclasses import dataclass, field


@dataclass
class Album:
    id: int
    title: str
    artistId: int
    numeroVendite: int
    numeroBrani: int = 0
    durataTotale: float = 0          # in minuti, la riempie getDurata
    fatture: set = field(default_factory=set)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return self.title
