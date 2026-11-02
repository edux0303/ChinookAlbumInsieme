from database.DB_connect import DBConnect
from model.album import Album


class DAO():

    @staticmethod
    def getGeneri():
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT g.GenreId AS id, g.Name AS nome
                FROM Genre g
                ORDER BY g.Name
                """

        cursor.execute(query)

        for row in cursor:
            results.append((row["id"], row["nome"]))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getNodi(genere):
        # album con almeno un brano del genere venduto + numero di vendite
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT ab.AlbumId AS id, ab.Title AS titolo, ab.ArtistId AS artista, COUNT(*) AS numeroVendi
                FROM Album ab, Track t, InvoiceLine il
                WHERE ab.AlbumId = t.AlbumId AND t.TrackId = il.TrackId AND t.GenreId = %s
                GROUP BY ab.AlbumId, ab.Title, ab.ArtistId
                ORDER BY ab.AlbumId
                """

        cursor.execute(query, (genere,))

        for row in cursor:
            a = Album(int(row["id"]), row["titolo"], int(row["artista"]), int(row["numeroVendi"]))
            results.append(a)

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getCoppie(genere):
        # coppie (album, fattura) per costruire gli archi
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT DISTINCT t.AlbumId AS id1, il.InvoiceId AS id2
                FROM Track t, InvoiceLine il
                WHERE t.TrackId = il.TrackId AND t.GenreId = %s
                """

        cursor.execute(query, (genere,))

        for row in cursor:
            results.append((int(row["id1"]), int(row["id2"])))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getDurata(genere):
        # durata (in minuti) e numero di brani del genere, sul catalogo
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT t.AlbumId AS id1, SUM(t.Milliseconds) AS durata, COUNT(*) AS num
                FROM Track t
                WHERE t.GenreId = %s
                GROUP BY t.AlbumId
                """

        cursor.execute(query, (genere,))

        for row in cursor:
            results.append((int(row["id1"]), float(row["durata"]) / 60000, int(row["num"])))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getNomiArtisti():
        conn = DBConnect.get_connection()
        if conn is None:
            return {}

        results = {}

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT ar.ArtistId, ar.Name
                FROM Artist ar
                """

        cursor.execute(query)

        for row in cursor:
            results[row["ArtistId"]] = row["Name"]

        cursor.close()
        conn.close()
        return results
