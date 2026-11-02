import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    # ---------- PUNTO 1 ----------

    def fillDDGeneri(self):
        self._view._ddGenere.options.clear()
        for idG, nome in self._model.getGeneri():
            self._view._ddGenere.options.append(ft.dropdown.Option(key=str(idG), text=nome))
        self._view.update_page()

    def handleCreaGrafo(self, e):
        self._view._txt_result.controls.clear()

        # 1. genere
        if self._view._ddGenere.value is None:
            self._errore("Seleziona un genere!")
            return
        idGenere = int(self._view._ddGenere.value)

        # 2. grafo
        self._model.buildGraph(idGenere)

        if self._model.getNumNodi() == 0:
            self._errore("Nessun album venduto per questo genere.")
            return

        # 3. stampo
        self._view._txt_result.controls.append(ft.Text("Grafo creato correttamente!", color="green"))
        self._view._txt_result.controls.append(ft.Text(f"Numero di nodi: {self._model.getNumNodi()}"))
        self._view._txt_result.controls.append(ft.Text(f"Numero di archi: {self._model.getNumArchi()}"))

        # 4. dropdown album
        self.fillDDAlbum()

        self._view.update_page()

    def fillDDAlbum(self):
        self._view._ddAlbum.options.clear()
        self._view._ddAlbum.value = None
        for a in self._model.getNodiOrdinati():
            self._view._ddAlbum.options.append(ft.dropdown.Option(key=str(a.id), text=a.title))

    def handleStampaInfo(self, e):
        self._view._txt_result.controls.clear()

        if self._model.getNumNodi() == 0:
            self._errore("Crea prima il grafo!")
            return

        res = self._view._txt_result.controls

        # a) album con più brani
        album, n = self._model.getAlbumBrani()
        res.append(ft.Text(f"a) Album con più brani: {album} ({n} brani)"))

        # b) album più lungo
        album, durata = self._model.getAlbumLungo()
        res.append(ft.Text(f"b) Album più lungo: {album} ({durata:.2f} minuti)"))

        # c) album con più vendite
        lista, n = self._model.getVendite()
        res.append(ft.Text(f"c) Album con più vendite ({n}): {', '.join(str(a) for a in lista)}"))

        # d) grado maggiore e somma dei pesi
        lista, grado = self._model.getGradoMaggiore()
        res.append(ft.Text(f"d) Album con grado maggiore ({grado}): {', '.join(str(a) for a in lista)}"))
        album, peso = self._model.getSommaPesi()
        res.append(ft.Text(f"   Album con somma dei pesi incidenti massima: {album} ({peso})"))

        # e) top 5 archi
        res.append(ft.Text("e) I 5 archi di peso maggiore:"))
        for t1, t2, p in self._model.getTop5Archi():
            res.append(ft.Text(f"     {t1} – {t2}: {p}"))

        # f) componenti
        nComp, dimMax, isolati = self._model.getInfoComponenti()
        res.append(ft.Text(f"f) Componenti connesse: {nComp}"))
        res.append(ft.Text(f"     Dimensione della più grande: {dimMax}"))
        res.append(ft.Text(f"     Album isolati: {isolati}"))

        # g) artista con più album
        nomi, nAlbum = self._model.getArtistaPiuAlbum()
        res.append(ft.Text(f"g) Artista con più album nel grafo ({nAlbum}): {', '.join(nomi)}"))

        self._view.update_page()

    # ---------- PUNTO 2 ----------

    def handleGruppo(self, e):
        self._view._txt_result.controls.clear()

        # 1. grafo creato?
        if self._model.getNumNodi() == 0:
            self._errore("Crea prima il grafo!")
            return

        # 2. album di partenza
        if self._view._ddAlbum.value is None:
            self._errore("Seleziona un album di partenza!")
            return
        partenza = self._model.getAlbum(int(self._view._ddAlbum.value))
        if partenza is None:
            self._errore("Album non presente nel grafo!")
            return

        # 3. N
        try:
            N = int(self._view._txtInN.value)
        except (ValueError, TypeError):
            self._errore("N deve essere un numero intero!")
            return
        if N < 2:
            self._errore("N deve essere almeno 2!")
            return

        # 4. ricorsione
        gruppo, durata, brani = self._model.getGruppo(partenza, N)

        if len(gruppo) == 0:
            self._errore(f"Nessun gruppo di {N} album a partire da {partenza}.")
            return

        # 5. stampo
        res = self._view._txt_result.controls
        res.append(ft.Text(f"Gruppo di {N} album a partire da {partenza}:", color="green"))
        for a in sorted(gruppo, key=lambda x: x.title):
            artista = self._model.getNomeArtista(a.artistId)
            res.append(ft.Text(f"     {a.title} ({artista}) – {a.durataTotale:.2f} min – {a.numeroBrani} brani"))
        res.append(ft.Text(f"Durata totale: {durata:.2f} minuti"))
        res.append(ft.Text(f"Totale brani: {brani}"))

        self._view.update_page()

    # ---------- UTILITY ----------

    def _errore(self, messaggio):
        self._view._txt_result.controls.append(ft.Text(messaggio, color="red"))
        self._view.update_page()