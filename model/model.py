import networkx as nx
from itertools import combinations
from database.DAO import DAO


class Model:
    def __init__(self):
        self._grafo = nx.Graph()
        self._idMap = {}
        self._nomiArtisti = {}
        # punto 2
        self._N = 0
        self._solBest = []
        self._durataBest = -1
        self._braniBest = -1
        self._visti = set()

    # ==================== PUNTO 1 ====================

    def getGeneri(self):
        return DAO.getGeneri()

    def buildGraph(self, genere):
        self._grafo.clear()
        self._idMap = {}

        # nodi: album con almeno un brano del genere venduto
        nodi = DAO.getNodi(genere)
        self._idMap = {a.id: a for a in nodi}
        self._grafo.add_nodes_from(nodi)

        # numero di brani e durata (catalogo)
        for idA, durata, numero in DAO.getDurata(genere):
            if idA in self._idMap:
                self._idMap[idA].numeroBrani = numero
                self._idMap[idA].durataTotale = durata

        # set delle fatture di ogni album
        for idA, idF in DAO.getCoppie(genere):
            if idA in self._idMap:
                self._idMap[idA].fatture.add(idF)

        # archi: almeno una fattura in comune
        for a1, a2 in combinations(nodi, 2):
            comuni = a1.fatture & a2.fatture
            if len(comuni) > 0:
                self._grafo.add_edge(a1, a2, weight=len(comuni))

    def getNumNodi(self):
        return self._grafo.number_of_nodes()

    def getNumArchi(self):
        return self._grafo.number_of_edges()

    def getNodiOrdinati(self):
        return sorted(self._grafo.nodes, key=lambda a: a.title)

    def getAlbum(self, idA):
        return self._idMap.get(idA)

    def getNomeArtista(self, idArtista):
        if len(self._nomiArtisti) == 0:
            self._nomiArtisti = DAO.getNomiArtisti()     # {ArtistId: nome}
        return self._nomiArtisti.get(idArtista, "sconosciuto")

    # a) album con più brani
    def getAlbumBrani(self):
        best = max(self._grafo.nodes, key=lambda a: a.numeroBrani)
        return best, best.numeroBrani

    # b) album più lungo
    def getAlbumLungo(self):
        best = max(self._grafo.nodes, key=lambda a: a.durataTotale)
        return best, best.durataTotale

    # c) album con più vendite (anche a pari merito)
    def getVendite(self):
        maxV = max(a.numeroVendite for a in self._grafo.nodes)
        migliori = [a for a in self._grafo.nodes if a.numeroVendite == maxV]
        migliori.sort(key=lambda a: a.title)
        return migliori, maxV

    # d) album con grado maggiore (anche a pari merito)
    def getGradoMaggiore(self):
        maxGrado = max(self._grafo.degree(a) for a in self._grafo.nodes)
        migliori = [a for a in self._grafo.nodes if self._grafo.degree(a) == maxGrado]
        migliori.sort(key=lambda a: a.title)
        return migliori, maxGrado

    # d) album con somma dei pesi incidenti massima
    def getSommaPesi(self):
        best = max(self._grafo.nodes, key=lambda a: self._grafo.degree(a, weight="weight"))
        return best, self._grafo.degree(best, weight="weight")

    # e) 5 archi di peso maggiore
    def getTop5Archi(self):
        archi = []
        for u, v, dati in self._grafo.edges(data=True):
            titoli = sorted([u.title, v.title])
            archi.append((titoli[0], titoli[1], dati["weight"]))
        archi.sort(key=lambda x: (-x[2], x[0], x[1]))
        return archi[:5]

    # f) componenti connesse
    def getInfoComponenti(self):
        componenti = list(nx.connected_components(self._grafo))
        piuGrande = max(componenti, key=len)
        isolati = 0
        for comp in componenti:
            if len(comp) == 1:
                isolati += 1
        return len(componenti), len(piuGrande), isolati

    # g) artista con più album nel grafo
    def getArtistaPiuAlbum(self):
        conta = {}
        for a in self._grafo.nodes:
            conta[a.artistId] = conta.get(a.artistId, 0) + 1
        maxAlbum = max(conta.values())
        migliori = sorted([self.getNomeArtista(idA) for idA in conta if conta[idA] == maxAlbum])
        return migliori, maxAlbum

    # ==================== PUNTO 2 ====================

    def getGruppo(self, partenza, N):
        self._N = N
        self._solBest = []
        self._durataBest = -1
        self._braniBest = -1
        self._visti = set()
        self._ricorsione([partenza])
        return self._solBest, self._durataBest, self._braniBest

    def _ricorsione(self, parziale):
        # 0. gruppo già visto in un altro ordine -> mi fermo
        chiave = frozenset(parziale)
        if chiave in self._visti:
            return
        self._visti.add(chiave)

        # 1. caso terminale: il gruppo ha N album
        if len(parziale) == self._N:
            durata = sum(a.durataTotale for a in parziale)
            brani = sum(a.numeroBrani for a in parziale)
            if (durata > self._durataBest or
                    (durata == self._durataBest and brani > self._braniBest)):
                self._durataBest = durata
                self._braniBest = brani
                self._solBest = list(parziale)
            return

        # 2. candidati: vicini degli album già nel gruppo
        candidati = set()
        for p in parziale:
            for v in self._grafo.neighbors(p):
                if self._ammissibile(v, parziale):
                    candidati.add(v)

        # 3. provo ad aggiungere ogni candidato
        for c in candidati:
            parziale.append(c)
            self._ricorsione(parziale)
            parziale.pop()

    def _ammissibile(self, c, parziale):
        if c in parziale:
            return False
        for p in parziale:
            if p.artistId == c.artistId:      # artisti tutti diversi
                return False
        return True