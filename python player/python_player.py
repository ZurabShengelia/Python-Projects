import sys
import os
import random
import sqlite3
import datetime

from pathlib import Path


from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QTableView, QHeaderView, QAbstractItemView, QSlider,
    QPushButton, QLabel, QLineEdit, QDialog, QFileDialog, QMenu,
    QAction, QMessageBox, QInputDialog, QFrame, QScrollArea,
    QSizePolicy, QGridLayout, QStyledItemDelegate, QStyleOptionViewItem,
    QStyle, QListWidget, QListWidgetItem, QToolButton, QSpacerItem,
    QDialogButtonBox, QCheckBox, QFormLayout
)

from PyQt5.QtCore import (
    Qt, QTimer, QThread, QObject, pyqtSignal, QSortFilterProxyModel,
    QAbstractTableModel, QModelIndex, QMimeData, QByteArray,
    QDataStream, QIODevice, QPoint, QRect, QSize, QUrl,
    QItemSelectionModel
)

from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QFontDatabase,
    QPalette, QIcon, QPixmap, QCursor, QFontMetrics, QLinearGradient
)

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist


try:

    import mutagen
 
    from mutagen.mp3 import MP3

    from mutagen.flac import FLAC

    from mutagen.oggvorbis import OggVorbis

    from mutagen.mp4 import MP4

    from mutagen.wave import WAVE

    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, TDRC, TCON

    MUTAGEN_AVAILABLE = True

except ImportError:

    MUTAGEN_AVAILABLE = False

BG_PRIMARY    = "#0D0D0D"

BG_SURFACE    = "#161616"

BG_ELEVATED   = "#1E1E1E"

BORDER        = "#2A2A2A"

TEXT_PRIMARY  = "#F0F0F0"

TEXT_SECONDARY= "#888888"

TEXT_MUTED    = "#444444"

ACCENT        = "#1DB954"

ACCENT_HOVER  = "#1ED760"

DANGER        = "#E05252"


SUPPORTED_EXTENSIONS = {'.mp3', '.flac', '.ogg', '.wav', '.m4a'}

def get_app_font():

    platform = sys.platform

    if platform == 'win32':

        return 'Segoe UI'

    elif platform == 'darwin':

        return 'SF Pro Display'

    else:

        db = QFontDatabase()

        families = db.families()

        if 'Inter' in families:

            return 'Inter'

        return 'DejaVu Sans'

APP_FONT = None

def make_font(size=13, weight=QFont.Normal, italic=False):
 
    f = QFont(APP_FONT or 'Segoe UI', size)
 
    f.setWeight(weight)
 
    f.setItalic(italic)
 
    return f
 
 
 
 
 
 
def draw_icon(painter: QPainter, icon_type: str, rect: QRect, color: QColor):
 
    painter.save()
 
    painter.setRenderHint(QPainter.Antialiasing)
 
    pen = QPen(color)
 
    pen.setWidth(2)
 
    pen.setCapStyle(Qt.RoundCap)
 
    pen.setJoinStyle(Qt.RoundJoin)
 
    painter.setPen(pen)
 
    painter.setBrush(QBrush(color))
 
 
    cx = rect.center().x()
 
    cy = rect.center().y()
 
    w = rect.width()
 
    h = rect.height()
 
 
    if icon_type == 'play':
 
 
        pts = [
            QPoint(rect.left() + int(w * 0.2), rect.top() + int(h * 0.15)),
            QPoint(rect.left() + int(w * 0.2), rect.bottom() - int(h * 0.15)),
            QPoint(rect.right() - int(w * 0.1), cy),
        ]
 
        from PyQt5.QtGui import QPolygon
 
        painter.drawPolygon(QPolygon(pts))
 
 
    elif icon_type == 'pause':
 
        bar_w = max(3, w // 4)
 
        gap = max(2, w // 6)
 
        x1 = cx - gap - bar_w
 
        x2 = cx + gap
 
        y1 = rect.top() + int(h * 0.18)
 
        y2 = rect.bottom() - int(h * 0.18)
 
        painter.drawRect(x1, y1, bar_w, y2 - y1)
 
        painter.drawRect(x2, y1, bar_w, y2 - y1)
 
 
    elif icon_type == 'stop':
 
        m = int(w * 0.2)
 
        painter.drawRect(rect.adjusted(m, m, -m, -m))
 
 
    elif icon_type == 'next':
 
 
        bar_w = max(2, w // 8)
 
        x_bar = rect.right() - int(w * 0.15) - bar_w
 
        y1 = rect.top() + int(h * 0.18)
 
        y2 = rect.bottom() - int(h * 0.18)
 
        painter.drawRect(x_bar, y1, bar_w, y2 - y1)
 
        mid = x_bar - int(w * 0.05)
 
        pts = [
            QPoint(rect.left() + int(w * 0.15), y1),
            QPoint(rect.left() + int(w * 0.15), y2),
            QPoint(mid, cy),
        ]
 
        from PyQt5.QtGui import QPolygon
 
        painter.drawPolygon(QPolygon(pts))
 
 
    elif icon_type == 'prev':
 
        bar_w = max(2, w // 8)
 
        x_bar = rect.left() + int(w * 0.15)
 
        y1 = rect.top() + int(h * 0.18)
 
        y2 = rect.bottom() - int(h * 0.18)
 
        painter.drawRect(x_bar, y1, bar_w, y2 - y1)
 
        mid = x_bar + bar_w + int(w * 0.05)
 
        pts = [
            QPoint(rect.right() - int(w * 0.15), y1),
            QPoint(rect.right() - int(w * 0.15), y2),
            QPoint(mid, cy),
        ]
 
        from PyQt5.QtGui import QPolygon
 
        painter.drawPolygon(QPolygon(pts))
 
 
    elif icon_type == 'shuffle':
 
 
        painter.setBrush(Qt.NoBrush)
 
        pen.setWidth(2)
 
        painter.setPen(pen)
 
        m = int(w * 0.15)
 
 
        painter.drawLine(rect.left() + m, rect.top() + m + 2,
                         rect.right() - m, rect.bottom() - m - 2)
 
 
        painter.drawLine(rect.left() + m, rect.bottom() - m - 2,
                         rect.right() - m, rect.top() + m + 2)
 
 
        r = rect.right() - m
 
        t = rect.top() + m + 2
 
        painter.drawLine(r, t, r - 4, t + 3)
 
        painter.drawLine(r, t, r - 4, t - 3)
 
 
    elif icon_type == 'repeat':
 
        painter.setBrush(Qt.NoBrush)
 
        pen.setWidth(2)
 
        painter.setPen(pen)
 
        m = int(w * 0.18)
 
 
        painter.drawRoundedRect(rect.adjusted(m, m, -m, -m), 3, 3)
 
 
        tx = rect.right() - m - 1
 
        ty = rect.top() + m
 
        painter.drawLine(tx - 4, ty - 3, tx, ty)
 
        painter.drawLine(tx, ty, tx - 4, ty + 3)
 
 
    elif icon_type == 'repeat_one':
 
        painter.setBrush(Qt.NoBrush)
 
        pen.setWidth(2)
 
        painter.setPen(pen)
 
        m = int(w * 0.18)
 
        painter.drawRoundedRect(rect.adjusted(m, m, -m, -m), 3, 3)
 
 
        painter.setFont(make_font(7, QFont.Bold))
 
        painter.drawText(rect, Qt.AlignCenter, "1")
 
 
    elif icon_type == 'volume':
 
        painter.setBrush(QBrush(color))
 
 
        x = rect.left() + int(w * 0.1)
 
        pts = [
            QPoint(x, cy - int(h * 0.2)),
            QPoint(x + int(w * 0.25), cy - int(h * 0.2)),
            QPoint(x + int(w * 0.45), cy - int(h * 0.38)),
            QPoint(x + int(w * 0.45), cy + int(h * 0.38)),
            QPoint(x + int(w * 0.25), cy + int(h * 0.2)),
            QPoint(x, cy + int(h * 0.2)),
        ]
 
        from PyQt5.QtGui import QPolygon
 
        painter.drawPolygon(QPolygon(pts))
 
 
        painter.setBrush(Qt.NoBrush)
 
        bx = x + int(w * 0.5)
 
        for i, r_size in enumerate([int(h * 0.25), int(h * 0.4)]):
 
            arc_rect = QRect(bx, cy - r_size, r_size, r_size * 2)
 
            painter.drawArc(arc_rect, -60 * 16, 120 * 16)
 
 
    elif icon_type == 'mute':
 
        painter.setBrush(QBrush(color))
 
        x = rect.left() + int(w * 0.1)
 
        pts = [
            QPoint(x, cy - int(h * 0.2)),
            QPoint(x + int(w * 0.25), cy - int(h * 0.2)),
            QPoint(x + int(w * 0.45), cy - int(h * 0.38)),
            QPoint(x + int(w * 0.45), cy + int(h * 0.38)),
            QPoint(x + int(w * 0.25), cy + int(h * 0.2)),
            QPoint(x, cy + int(h * 0.2)),
        ]
 
        from PyQt5.QtGui import QPolygon
 
        painter.drawPolygon(QPolygon(pts))
 
 
        pen2 = QPen(color)
 
        pen2.setWidth(2)
 
        painter.setPen(pen2)
 
        bx = x + int(w * 0.52)
 
        painter.drawLine(bx, cy - int(h * 0.22), bx + int(w * 0.3), cy + int(h * 0.22))
 
        painter.drawLine(bx + int(w * 0.3), cy - int(h * 0.22), bx, cy + int(h * 0.22))
 
 
    elif icon_type == 'library':
 
        painter.setBrush(Qt.NoBrush)
 
        pen.setWidth(2)
 
        painter.setPen(pen)
 
        m = int(w * 0.15)
 
 
        for i in range(3):
 
            y = rect.top() + m + i * int((h - 2 * m) / 2.5)
 
            painter.drawLine(rect.left() + m, y, rect.right() - m, y)
 
 
    elif icon_type == 'playlist':
 
        painter.setBrush(Qt.NoBrush)
 
        pen.setWidth(2)
 
        painter.setPen(pen)
 
        m = int(w * 0.15)
 
        for i in range(3):
 
            y = rect.top() + m + i * int((h - 2 * m) / 2.5)
 
            xl = rect.left() + m + int(w * 0.25) if i == 0 else rect.left() + m
 
            painter.drawLine(xl, y, rect.right() - m, y)
 
 
        px = rect.left() + int(w * 0.2)
 
        py = rect.bottom() - int(h * 0.25)
 
        painter.drawLine(px - 3, py, px + 3, py)
 
        painter.drawLine(px, py - 3, px, py + 3)
 
 
    elif icon_type == 'album':
 
        painter.setBrush(Qt.NoBrush)
 
        pen.setWidth(2)
 
        painter.setPen(pen)
 
        m = int(w * 0.12)
 
        painter.drawEllipse(rect.adjusted(m, m, -m, -m))
 
        inner = int(w * 0.28)
 
        painter.setBrush(QBrush(color))
 
        painter.drawEllipse(rect.adjusted(inner, inner, -inner, -inner))
 
 
    elif icon_type == 'artist':
 
        painter.setBrush(QBrush(color))
 
        head_r = int(h * 0.2)
 
        painter.drawEllipse(cx - head_r, rect.top() + int(h * 0.08), head_r * 2, head_r * 2)
 
 
        painter.setBrush(Qt.NoBrush)
 
        body_rect = QRect(cx - int(w * 0.3), cy - int(h * 0.05), int(w * 0.6), int(h * 0.55))
 
        painter.drawArc(body_rect, 0, 180 * 16)
 
 
    elif icon_type == 'settings':
 
        painter.setBrush(Qt.NoBrush)
 
        pen.setWidth(2)
 
        painter.setPen(pen)
 
        m = int(w * 0.28)
 
        painter.drawEllipse(rect.adjusted(m, m, -m, -m))
 
 
        for angle in range(0, 360, 45):
 
            import math
 
            rad = math.radians(angle)
 
            r1 = w * 0.38
 
            r2 = w * 0.48
 
            x1 = cx + int(r1 * math.cos(rad))
 
            y1 = cy + int(r1 * math.sin(rad))
 
            x2 = cx + int(r2 * math.cos(rad))
 
            y2 = cy + int(r2 * math.sin(rad))
 
            painter.drawLine(x1, y1, x2, y2)
 
 
 
    elif icon_type == 'heart':
        import math as _math
        painter.setBrush(QBrush(color))
        pts = []
        for i in range(100):
            t = _math.pi * 2 * i / 100
            hx = 16 * (_math.sin(t) ** 3)
            hy = -(13*_math.cos(t) - 5*_math.cos(2*t) - 2*_math.cos(3*t) - _math.cos(4*t))
            pts.append(QPoint(cx + int(hx * w * 0.038), cy + int(hy * h * 0.038) + int(h*0.04)))
        from PyQt5.QtGui import QPolygon
        painter.drawPolygon(QPolygon(pts))
 
    elif icon_type == 'add':
 
        pen.setWidth(2)
 
        painter.setPen(pen)
 
        painter.drawLine(cx, rect.top() + 4, cx, rect.bottom() - 4)
 
        painter.drawLine(rect.left() + 4, cy, rect.right() - 4, cy)
 
 
    elif icon_type == 'remove':
 
        pen.setWidth(2)
 
        painter.setPen(pen)
 
        painter.drawLine(rect.left() + 4, cy, rect.right() - 4, cy)
 
 
    elif icon_type == 'collapse':
 
        pen.setWidth(2)
 
        painter.setPen(pen)
 
        pts = [
            QPoint(rect.left() + 4, cy - 3),
            QPoint(cx, cy + 4),
            QPoint(rect.right() - 4, cy - 3),
        ]
 
        from PyQt5.QtGui import QPolygon
 
        painter.drawPolyline(QPolygon(pts))
 
 
    elif icon_type == 'expand':
 
        pen.setWidth(2)
 
        painter.setPen(pen)
 
        pts = [
            QPoint(rect.left() + 4, cy + 3),
            QPoint(cx, cy - 4),
            QPoint(rect.right() - 4, cy + 3),
        ]
 
        from PyQt5.QtGui import QPolygon
 
        painter.drawPolyline(QPolygon(pts))
 
 
    painter.restore()
 
 
 
def make_icon_pixmap(icon_type: str, size: int = 20,
                     color: str = TEXT_PRIMARY) -> QPixmap:
 
    pix = QPixmap(size, size)
 
    pix.fill(Qt.transparent)
 
    p = QPainter(pix)
 
    draw_icon(p, icon_type, QRect(0, 0, size, size), QColor(color))
 
    p.end()
 
    return pix
 
 
 
 
 
 
 
class Database:
 
    def __init__(self, db_path: str = None):
 
        if db_path is None:
 
            script_dir = Path(__file__).parent.resolve()
 
            db_path = str(script_dir / 'python_player.db')
 
        self.db_path = db_path
 
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
 
        self.conn.row_factory = sqlite3.Row
 
        self.conn.execute("PRAGMA foreign_keys = ON")
 
        self._create_schema()
 
 
    def _create_schema(self):
 
        cur = self.conn.cursor()
 
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS artists (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS albums (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                title     TEXT NOT NULL,
                artist_id INTEGER REFERENCES artists(id),
                year      INTEGER,
                UNIQUE(title, artist_id)
            );
            CREATE TABLE IF NOT EXISTS tracks (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path    TEXT NOT NULL UNIQUE,
                title        TEXT,
                artist_id    INTEGER REFERENCES artists(id),
                album_id     INTEGER REFERENCES albums(id),
                track_number INTEGER,
                duration_ms  INTEGER,
                genre        TEXT,
                date_added   DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS playlists (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS favourites (
                track_id   INTEGER PRIMARY KEY REFERENCES tracks(id) ON DELETE CASCADE,
                added_at   DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS playlist_tracks (
                playlist_id INTEGER REFERENCES playlists(id) ON DELETE CASCADE,
                track_id    INTEGER REFERENCES tracks(id)    ON DELETE CASCADE,
                position    INTEGER NOT NULL,
                PRIMARY KEY (playlist_id, track_id)
            );
        """)
 
        self.conn.commit()
 
 
 
    def get_or_create_artist(self, name: str) -> int:
 
        name = name.strip() if name else 'Unknown Artist'
 
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO artists(name) VALUES(?)", (name,))
 
        self.conn.commit()
 
        row = self.conn.execute(
            "SELECT id FROM artists WHERE name=?", (name,)).fetchone()
 
        return row['id']
 
 
 
    def get_or_create_album(self, title: str, artist_id: int,
                             year: int = None) -> int:
 
        title = title.strip() if title else 'Unknown Album'
 
        self.conn.execute(
            "INSERT OR IGNORE INTO albums(title,artist_id,year) VALUES(?,?,?)",
            (title, artist_id, year))
 
        self.conn.commit()
 
        row = self.conn.execute(
            "SELECT id FROM albums WHERE title=? AND artist_id=?",
            (title, artist_id)).fetchone()
 
        return row['id']
 
 
 
    def upsert_track(self, file_path: str, title: str, artist_id: int,
                     album_id: int, track_number: int,
                     duration_ms: int, genre: str) -> int:
 
        self.conn.execute("""
            INSERT INTO tracks
                (file_path,title,artist_id,album_id,track_number,duration_ms,genre)
            VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(file_path) DO UPDATE SET
                title=excluded.title,
                artist_id=excluded.artist_id,
                album_id=excluded.album_id,
                track_number=excluded.track_number,
                duration_ms=excluded.duration_ms,
                genre=excluded.genre
        """, (file_path, title, artist_id, album_id,
              track_number, duration_ms, genre))
 
        self.conn.commit()
 
        row = self.conn.execute(
            "SELECT id FROM tracks WHERE file_path=?",
            (file_path,)).fetchone()
 
        return row['id']
 
 
    def get_all_tracks(self):
 
        return self.conn.execute("""
            SELECT t.id, t.file_path, t.title, ar.name AS artist,
                   al.title AS album, t.track_number, t.duration_ms,
                   t.genre, al.year
            FROM tracks t
            LEFT JOIN artists ar ON t.artist_id = ar.id
            LEFT JOIN albums  al ON t.album_id  = al.id
            ORDER BY ar.name, al.title, t.track_number, t.title
        """).fetchall()
 
 
    def get_track_by_id(self, track_id: int):
 
        return self.conn.execute("""
            SELECT t.id, t.file_path, t.title, ar.name AS artist,
                   al.title AS album, t.track_number, t.duration_ms,
                   t.genre, al.year
            FROM tracks t
            LEFT JOIN artists ar ON t.artist_id = ar.id
            LEFT JOIN albums  al ON t.album_id  = al.id
            WHERE t.id = ?
        """, (track_id,)).fetchone()
 
 
    def delete_track(self, track_id: int):
 
        self.conn.execute("DELETE FROM tracks WHERE id=?", (track_id,))
 
        self.conn.commit()
 
 
    def get_all_albums(self):
 
        return self.conn.execute("""
            SELECT al.id, al.title, ar.name AS artist, al.year,
                   COUNT(t.id) AS track_count
            FROM albums al
            LEFT JOIN artists ar ON al.artist_id = ar.id
            LEFT JOIN tracks  t  ON t.album_id   = al.id
            GROUP BY al.id
            ORDER BY ar.name, al.title
        """).fetchall()
 
 
    def get_all_artists(self):
 
        return self.conn.execute("""
            SELECT ar.id, ar.name, COUNT(DISTINCT al.id) AS album_count,
                   COUNT(t.id) AS track_count
            FROM artists ar
            LEFT JOIN albums al ON al.artist_id = ar.id
            LEFT JOIN tracks t  ON t.artist_id  = ar.id
            GROUP BY ar.id
            ORDER BY ar.name
        """).fetchall()
 
 
    def get_tracks_for_album(self, album_id: int):
 
        return self.conn.execute("""
            SELECT t.id, t.file_path, t.title, ar.name AS artist,
                   al.title AS album, t.track_number, t.duration_ms,
                   t.genre, al.year
            FROM tracks t
            LEFT JOIN artists ar ON t.artist_id = ar.id
            LEFT JOIN albums  al ON t.album_id  = al.id
            WHERE t.album_id = ?
            ORDER BY t.track_number, t.title
        """, (album_id,)).fetchall()
 
 
    def get_tracks_for_artist(self, artist_id: int):
 
        return self.conn.execute("""
            SELECT t.id, t.file_path, t.title, ar.name AS artist,
                   al.title AS album, t.track_number, t.duration_ms,
                   t.genre, al.year
            FROM tracks t
            LEFT JOIN artists ar ON t.artist_id = ar.id
            LEFT JOIN albums  al ON t.album_id  = al.id
            WHERE t.artist_id = ?
            ORDER BY al.title, t.track_number, t.title
        """, (artist_id,)).fetchall()
 
 
 
    def get_all_playlists(self):
 
        return self.conn.execute(
            "SELECT id, name, created_at FROM playlists ORDER BY name"
        ).fetchall()
 
 
    def create_playlist(self, name: str) -> int:
 
        cur = self.conn.execute(
            "INSERT INTO playlists(name) VALUES(?)", (name,))
 
        self.conn.commit()
 
        return cur.lastrowid
 
 
    def rename_playlist(self, playlist_id: int, name: str):
 
        self.conn.execute(
            "UPDATE playlists SET name=? WHERE id=?", (name, playlist_id))
 
        self.conn.commit()
 
 
    def delete_playlist(self, playlist_id: int):
 
        self.conn.execute(
            "DELETE FROM playlists WHERE id=?", (playlist_id,))
 
        self.conn.commit()
 
 
    def get_playlist_tracks(self, playlist_id: int):
 
        return self.conn.execute("""
            SELECT t.id, t.file_path, t.title, ar.name AS artist,
                   al.title AS album, t.track_number, t.duration_ms,
                   t.genre, pt.position
            FROM playlist_tracks pt
            JOIN tracks  t  ON pt.track_id   = t.id
            LEFT JOIN artists ar ON t.artist_id = ar.id
            LEFT JOIN albums  al ON t.album_id  = al.id
            WHERE pt.playlist_id = ?
            ORDER BY pt.position
        """, (playlist_id,)).fetchall()
 
 
    def add_track_to_playlist(self, playlist_id: int, track_id: int):
 
        row = self.conn.execute("""
            SELECT COALESCE(MAX(position), -1) + 1 AS next_pos
            FROM playlist_tracks WHERE playlist_id=?
        """, (playlist_id,)).fetchone()
 
        next_pos = row['next_pos']
 
        self.conn.execute("""
            INSERT OR IGNORE INTO playlist_tracks(playlist_id,track_id,position)
            VALUES(?,?,?)
        """, (playlist_id, track_id, next_pos))
 
        self.conn.commit()
 
 
    def remove_track_from_playlist(self, playlist_id: int, track_id: int):
 
        self.conn.execute("""
            DELETE FROM playlist_tracks
            WHERE playlist_id=? AND track_id=?
        """, (playlist_id, track_id))
 
        self.conn.commit()
 
        self._reorder_playlist(playlist_id)
 
 
    def reorder_playlist_track(self, playlist_id: int, track_id: int,
                                new_pos: int):
 
        self.conn.execute("""
            UPDATE playlist_tracks SET position=?
            WHERE playlist_id=? AND track_id=?
        """, (new_pos, playlist_id, track_id))
 
        self.conn.commit()
 
        self._reorder_playlist(playlist_id)
 
 
    def _reorder_playlist(self, playlist_id: int):
 
        rows = self.conn.execute("""
            SELECT track_id FROM playlist_tracks
            WHERE playlist_id=? ORDER BY position
        """, (playlist_id,)).fetchall()
 
        for i, row in enumerate(rows):
 
            self.conn.execute("""
                UPDATE playlist_tracks SET position=?
                WHERE playlist_id=? AND track_id=?
            """, (i, playlist_id, row['track_id']))
 
        self.conn.commit()
 
 
 
    def toggle_favourite(self, track_id: int) -> bool:
        exists = self.conn.execute(
            "SELECT 1 FROM favourites WHERE track_id=?", (track_id,)).fetchone()
        if exists:
            self.conn.execute("DELETE FROM favourites WHERE track_id=?", (track_id,))
            self.conn.commit()
            return False
        self.conn.execute(
            "INSERT OR IGNORE INTO favourites(track_id) VALUES(?)", (track_id,))
        self.conn.commit()
        return True
 
    def is_favourite(self, track_id: int) -> bool:
        return bool(self.conn.execute(
            "SELECT 1 FROM favourites WHERE track_id=?", (track_id,)).fetchone())
 
    def get_favourite_tracks(self):
        return self.conn.execute("""
            SELECT t.id, t.file_path, t.title, ar.name AS artist,
                   al.title AS album, t.track_number, t.duration_ms,
                   t.genre, al.year
            FROM favourites fv
            JOIN tracks t ON fv.track_id = t.id
            LEFT JOIN artists ar ON t.artist_id = ar.id
            LEFT JOIN albums  al ON t.album_id  = al.id
            ORDER BY fv.added_at DESC
        """).fetchall()
 
    def track_exists(self, file_path: str) -> bool:
 
        row = self.conn.execute(
            "SELECT 1 FROM tracks WHERE file_path=?", (file_path,)).fetchone()
 
        return row is not None
 
 
    def close(self):
 
        self.conn.close()
 
 
 
 
 
 
 
def read_metadata(file_path: str) -> dict:
 
    meta = {
        'title': None,
        'artist': None,
        'album': None,
        'track_number': None,
        'duration_ms': 0,
        'year': None,
        'genre': None,
    }
 
    path = Path(file_path)
 
    ext = path.suffix.lower()
 
 
 
    meta['title'] = path.stem
 
 
    if not MUTAGEN_AVAILABLE:
 
        return meta
 
 
    try:
 
        if ext == '.mp3':
 
            audio = MP3(file_path)
 
            meta['duration_ms'] = int(audio.info.length * 1000)
 
            tags = audio.tags
 
            if tags:
 
                if 'TIT2' in tags:
 
                    meta['title'] = str(tags['TIT2'])
 
                if 'TPE1' in tags:
 
                    meta['artist'] = str(tags['TPE1'])
 
                if 'TALB' in tags:
 
                    meta['album'] = str(tags['TALB'])
 
                if 'TRCK' in tags:
 
                    tn = str(tags['TRCK']).split('/')[0]
 
                    try:
 
                        meta['track_number'] = int(tn)
 
                    except ValueError:
 
                        pass
 
                for tag in ('TDRC', 'TYER', 'TDRL'):
 
                    if tag in tags:
 
                        try:
 
                            meta['year'] = int(str(tags[tag])[:4])
 
                            break
 
                        except (ValueError, TypeError):
 
                            pass
 
                if 'TCON' in tags:
 
                    meta['genre'] = str(tags['TCON'])
 
 
        elif ext == '.flac':
 
            audio = FLAC(file_path)
 
            meta['duration_ms'] = int(audio.info.length * 1000)
 
            def get_tag(key):
 
                v = audio.get(key, audio.get(key.lower(), [None]))
 
                return v[0] if v else None
 
            meta['title']  = get_tag('TITLE')  or meta['title']
 
            meta['artist'] = get_tag('ARTIST')
 
            meta['album']  = get_tag('ALBUM')
 
            meta['genre']  = get_tag('GENRE')
 
            tn = get_tag('TRACKNUMBER')
 
            if tn:
 
                try:
 
                    meta['track_number'] = int(str(tn).split('/')[0])
 
                except ValueError:
 
                    pass
 
            yr = get_tag('DATE') or get_tag('YEAR')
 
            if yr:
 
                try:
 
                    meta['year'] = int(str(yr)[:4])
 
                except (ValueError, TypeError):
 
                    pass
 
 
        elif ext == '.ogg':
 
            audio = OggVorbis(file_path)
 
            meta['duration_ms'] = int(audio.info.length * 1000)
 
            def get_tag(key):
 
                v = audio.get(key, audio.get(key.lower(), [None]))
 
                return v[0] if v else None
 
            meta['title']  = get_tag('title')  or meta['title']
 
            meta['artist'] = get_tag('artist')
 
            meta['album']  = get_tag('album')
 
            meta['genre']  = get_tag('genre')
 
            tn = get_tag('tracknumber')
 
            if tn:
 
                try:
 
                    meta['track_number'] = int(str(tn).split('/')[0])
 
                except ValueError:
 
                    pass
 
            yr = get_tag('date') or get_tag('year')
 
            if yr:
 
                try:
 
                    meta['year'] = int(str(yr)[:4])
 
                except (ValueError, TypeError):
 
                    pass
 
 
        elif ext == '.m4a':
 
            audio = MP4(file_path)
 
            meta['duration_ms'] = int(audio.info.length * 1000)
 
            tags = audio.tags or {}
 
            if '\xa9nam' in tags:
 
                meta['title'] = str(tags['\xa9nam'][0])
 
            if '\xa9ART' in tags:
 
                meta['artist'] = str(tags['\xa9ART'][0])
 
            if '\xa9alb' in tags:
 
                meta['album'] = str(tags['\xa9alb'][0])
 
            if 'trkn' in tags:
 
                try:
 
                    meta['track_number'] = int(tags['trkn'][0][0])
 
                except (IndexError, TypeError, ValueError):
 
                    pass
 
            if '\xa9day' in tags:
 
                try:
 
                    meta['year'] = int(str(tags['\xa9day'][0])[:4])
 
                except (ValueError, TypeError):
 
                    pass
 
            if '\xa9gen' in tags:
 
                meta['genre'] = str(tags['\xa9gen'][0])
 
 
        elif ext == '.wav':
 
            audio = WAVE(file_path)
 
            meta['duration_ms'] = int(audio.info.length * 1000)
 
            if audio.tags:
 
                tags = audio.tags
 
                if 'TIT2' in tags:
 
                    meta['title'] = str(tags['TIT2'])
 
                if 'TPE1' in tags:
 
                    meta['artist'] = str(tags['TPE1'])
 
                if 'TALB' in tags:
 
                    meta['album'] = str(tags['TALB'])
 
 
    except Exception:
 
        pass
 
 
    return meta
 
 
 
def format_duration(ms: int) -> str:
 
    if not ms:
 
        return '0:00'
 
    s = ms // 1000
 
    m = s // 60
 
    s = s % 60
 
    h = m // 60
 
    m = m % 60
 
    if h:
 
        return f"{h}:{m:02d}:{s:02d}"
 
    return f"{m}:{s:02d}"
 
 
 
 
 
 
 
class ScanWorker(QThread):
 
    progress = pyqtSignal(int, int, str)
 
    finished = pyqtSignal(int)
 
    error    = pyqtSignal(str)
 
 
    def __init__(self, folder: str, db: 'Database'):
 
        super().__init__()
 
        self.folder = folder
 
        self.db = db
 
 
    def run(self):
 
        try:
 
            files = []
 
            for root, dirs, filenames in os.walk(self.folder):
 
                for fn in filenames:
 
                    if Path(fn).suffix.lower() in SUPPORTED_EXTENSIONS:
 
                        files.append(os.path.join(root, fn))
 
 
            added = 0
 
            total = len(files)
 
            for i, fp in enumerate(files):
 
                self.progress.emit(i + 1, total, fp)
 
                meta = read_metadata(fp)
 
                artist_id = self.db.get_or_create_artist(
                    meta['artist'] or 'Unknown Artist')
 
                album_id = self.db.get_or_create_album(
                    meta['album'] or 'Unknown Album',
                    artist_id, meta['year'])
 
                self.db.upsert_track(
                    fp,
                    meta['title'] or Path(fp).stem,
                    artist_id, album_id,
                    meta['track_number'], meta['duration_ms'],
                    meta['genre'])
 
                added += 1
 
            self.finished.emit(added)
 
        except Exception as e:
 
            self.error.emit(str(e))
 
 
 
 
 
 
 
TRACK_COLUMNS = ['#', 'Title', 'Artist', 'Album', 'Duration', 'Genre', 'Year']
 
TRACK_COL_MAP = {
    0: 'track_number',
    1: 'title',
    2: 'artist',
    3: 'album',
    4: 'duration_ms',
    5: 'genre',
    6: 'year',
}
 
 
class TrackTableModel(QAbstractTableModel):
 
    def __init__(self, parent=None):
 
        super().__init__(parent)
 
        self._tracks = []
 
 
    def set_tracks(self, tracks):
 
        self.beginResetModel()
 
        self._tracks = [dict(t) for t in tracks]
 
        self.endResetModel()
 
 
    def rowCount(self, parent=QModelIndex()):
 
        return len(self._tracks)
 
 
    def columnCount(self, parent=QModelIndex()):
 
        return len(TRACK_COLUMNS)
 
 
    def headerData(self, section, orientation, role=Qt.DisplayRole):
 
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
 
            return TRACK_COLUMNS[section]
 
        return None
 
 
    def data(self, index, role=Qt.DisplayRole):
 
        if not index.isValid() or index.row() >= len(self._tracks):
 
            return None
 
        track = self._tracks[index.row()]
 
        col   = index.column()
 
        if role == Qt.DisplayRole:
 
            if col == 0:
 
                tn = track.get('track_number')
 
                return str(tn) if tn else ''
 
            elif col == 1:
 
                return track.get('title') or ''
 
            elif col == 2:
 
                return track.get('artist') or ''
 
            elif col == 3:
 
                return track.get('album') or ''
 
            elif col == 4:
 
                return format_duration(track.get('duration_ms') or 0)
 
            elif col == 5:
 
                return track.get('genre') or ''
 
            elif col == 6:
 
                yr = track.get('year')
 
                return str(yr) if yr else ''
 
        elif role == Qt.TextAlignmentRole:
 
            if col in (0, 4, 6):
 
                return Qt.AlignCenter
 
            return Qt.AlignLeft | Qt.AlignVCenter
 
        elif role == Qt.UserRole:
 
            return track.get('id')
 
        elif role == Qt.UserRole + 1:
 
            return track
 
        return None
 
 
    def get_track(self, row: int):
 
        if 0 <= row < len(self._tracks):
 
            return self._tracks[row]
 
        return None
 
 
    def get_all_track_ids(self):
 
        return [t.get('id') for t in self._tracks]
 
 
 
class PlaylistTrackModel(TrackTableModel):
 
    """Extended model that stores playlist position."""
 
    def set_tracks(self, tracks):
 
        self.beginResetModel()
 
        self._tracks = [dict(t) for t in tracks]
 
        self.endResetModel()
 
 
    def supportedDropActions(self):
 
        return Qt.MoveAction
 
 
    def flags(self, index):
 
        default = super().flags(index)
 
        if index.isValid():
 
            return default | Qt.ItemIsDragEnabled
 
        return default | Qt.ItemIsDropEnabled
 
 
    def mimeTypes(self):
 
        return ['application/x-track-row']
 
 
    def mimeData(self, indexes):
 
        rows = sorted(set(i.row() for i in indexes))
 
        data = QMimeData()
 
        ba = QByteArray()
 
        ds = QDataStream(ba, QIODevice.WriteOnly)
 
        for r in rows:
 
            ds.writeInt32(r)
 
        data.setData('application/x-track-row', ba)
 
        return data
 
 
    def dropMimeData(self, data, action, row, column, parent):
 
        if not data.hasFormat('application/x-track-row'):
 
            return False
 
        ba = data.data('application/x-track-row')
 
        ds = QDataStream(ba, QIODevice.ReadOnly)
 
        source_rows = []
 
        while not ds.atEnd():
 
            source_rows.append(ds.readInt32())
 
        if not source_rows:
 
            return False
 
        dest = row if row >= 0 else len(self._tracks)
 
        moved = [self._tracks[r] for r in source_rows]
 
        remaining = [t for i, t in enumerate(self._tracks)
                     if i not in source_rows]
 
        for i, t in enumerate(moved):
 
            remaining.insert(min(dest + i, len(remaining)), t)
 
        self.beginResetModel()
 
        self._tracks = remaining
 
        self.endResetModel()
 
        return True
 
 
 
 
 
 
 
class AudioPlayer(QObject):
 
    track_changed   = pyqtSignal(dict)
 
    playback_state  = pyqtSignal(str)
 
    position_changed= pyqtSignal(int)
 
    duration_changed= pyqtSignal(int)
 
    queue_changed   = pyqtSignal()
 
 
    REPEAT_NONE = 0
 
    REPEAT_ONE  = 1
 
    REPEAT_ALL  = 2
 
 
    def __init__(self, parent=None):
 
        super().__init__(parent)
 
        self.player = QMediaPlayer()
 
        self.player.stateChanged.connect(self._on_state_changed)
 
        self.player.positionChanged.connect(self._on_position_changed)
 
        self.player.durationChanged.connect(self._on_duration_changed)
 
        self.player.mediaStatusChanged.connect(self._on_media_status)
 
        self.player.error.connect(self._on_error)
 
 
        self._queue        = []
 
        self._queue_index  = -1
 
        self._shuffle      = False
 
        self._repeat       = self.REPEAT_NONE
 
        self._shuffle_order= []
 
        self._current_track= None
 
        self._volume       = 70
 
        self._muted        = False
 
        self.player.setVolume(self._volume)
 
 
 
 
    def set_queue(self, tracks: list, start_index: int = 0):
 
        self._queue = list(tracks)
 
        self._queue_index = start_index
 
        self._rebuild_shuffle()
 
        if self._queue:
 
            self._play_index(start_index)
 
 
    def _rebuild_shuffle(self):
 
        indices = list(range(len(self._queue)))
 
        if self._shuffle and self._queue_index >= 0:
 
            indices.remove(min(self._queue_index, len(indices) - 1))
 
            random.shuffle(indices)
 
            self._shuffle_order = [self._queue_index] + indices
 
        else:
 
            self._shuffle_order = indices
 
 
    def _play_index(self, idx: int):
 
        if not self._queue or idx < 0 or idx >= len(self._queue):
 
            return
 
        self._queue_index = idx
 
        track = self._queue[idx]
 
        self._current_track = track
 
        fp = track.get('file_path', '')
 
        url = QUrl.fromLocalFile(fp)
 
        self.player.setMedia(QMediaContent(url))
 
        self.player.play()
 
        self.track_changed.emit(track)
 
        self.queue_changed.emit()
 
 
    def _effective_index(self, raw_idx: int) -> int:
 
        if self._shuffle and self._shuffle_order:
 
            try:
 
                pos = self._shuffle_order.index(raw_idx)
 
                return pos
 
            except ValueError:
 
                return raw_idx
 
        return raw_idx
 
 
    def play_track(self, track: dict):
 
        if track in self._queue:
 
            idx = self._queue.index(track)
 
        else:
 
            self._queue.append(track)
 
            idx = len(self._queue) - 1
 
            self._rebuild_shuffle()
 
        self._play_index(idx)
 
 
    def play(self):
 
        if self.player.state() == QMediaPlayer.PausedState:
 
            self.player.play()
 
        elif self._current_track:
 
            self.player.play()
 
        elif self._queue:
 
            self._play_index(0)
 
 
    def pause(self):
 
        self.player.pause()
 
 
    def stop(self):
 
        self.player.stop()
 
        self.playback_state.emit('stopped')
 
 
    def next_track(self):
 
        if not self._queue:
 
            return
 
        if self._repeat == self.REPEAT_ONE:
 
            self._play_index(self._queue_index)
 
            return
 
        if self._shuffle:
 
            try:
 
                pos = self._shuffle_order.index(self._queue_index)
 
                next_pos = (pos + 1) % len(self._shuffle_order)
 
                next_idx = self._shuffle_order[next_pos]
 
            except ValueError:
 
                next_idx = 0
 
        else:
 
            next_idx = self._queue_index + 1
 
            if next_idx >= len(self._queue):
 
                if self._repeat == self.REPEAT_ALL:
 
                    next_idx = 0
 
                else:
 
                    self.stop()
 
                    return
 
        self._play_index(next_idx)
 
 
    def prev_track(self):
 
        if not self._queue:
 
            return
 
        pos_ms = self.player.position()
 
        if pos_ms > 3000:
 
            self.player.setPosition(0)
 
            return
 
        if self._shuffle:
 
            try:
 
                pos = self._shuffle_order.index(self._queue_index)
 
                prev_pos = (pos - 1) % len(self._shuffle_order)
 
                prev_idx = self._shuffle_order[prev_pos]
 
            except ValueError:
 
                prev_idx = 0
 
        else:
 
            prev_idx = self._queue_index - 1
 
            if prev_idx < 0:
 
                prev_idx = len(self._queue) - 1 if self._repeat == self.REPEAT_ALL else 0
 
        self._play_index(prev_idx)
 
 
    def seek(self, ms: int):
 
        self.player.setPosition(ms)
 
 
    def set_volume(self, vol: int):
 
        self._volume = vol
 
        if not self._muted:
 
            self.player.setVolume(vol)
 
 
    def toggle_mute(self):
 
        self._muted = not self._muted
 
        if self._muted:
 
            self.player.setVolume(0)
 
        else:
 
            self.player.setVolume(self._volume)
 
        return self._muted
 
 
    def set_shuffle(self, enabled: bool):
 
        self._shuffle = enabled
 
        self._rebuild_shuffle()
 
 
    def set_repeat(self, mode: int):
 
        self._repeat = mode
 
 
    def is_playing(self) -> bool:
 
        return self.player.state() == QMediaPlayer.PlayingState
 
 
    def is_paused(self) -> bool:
 
        return self.player.state() == QMediaPlayer.PausedState
 
 
    def get_position(self) -> int:
 
        return self.player.position()
 
 
    def get_duration(self) -> int:
 
        return self.player.duration()
 
 
    def get_volume(self) -> int:
 
        return self._volume
 
 
    def is_muted(self) -> bool:
 
        return self._muted
 
 
    def get_current_track(self):
 
        return self._current_track
 
 
    def get_queue(self):
 
        return list(self._queue)
 
 
    def get_queue_index(self):
 
        return self._queue_index
 
 
 
 
    def _on_state_changed(self, state):
 
        if state == QMediaPlayer.PlayingState:
 
            self.playback_state.emit('playing')
 
        elif state == QMediaPlayer.PausedState:
 
            self.playback_state.emit('paused')
 
        else:
 
            self.playback_state.emit('stopped')
 
 
    def _on_position_changed(self, pos: int):
 
        self.position_changed.emit(pos)
 
 
    def _on_duration_changed(self, dur: int):
 
        self.duration_changed.emit(dur)
 
 
    def _on_media_status(self, status):
 
        if status == QMediaPlayer.EndOfMedia:
 
            self.next_track()
 
 
    def _on_error(self, error):
 
        pass
 
 
 
 
 
 
 
class WaveformSlider(QSlider):
 
    """Seek bar with accent-colored elapsed portion."""
 
    def __init__(self, orientation=Qt.Horizontal, parent=None):
 
        super().__init__(orientation, parent)
 
        self.setRange(0, 1000)
 
        self.setSingleStep(1)
 
        self.setPageStep(10)
 
        self._track_h = 3
 
        self._handle_r = 6
 
        self.setCursor(Qt.PointingHandCursor)
 
 
    def paintEvent(self, event):
 
        painter = QPainter(self)
 
        painter.setRenderHint(QPainter.Antialiasing)
 
        w = self.width()
 
        h = self.height()
 
        cy = h // 2
 
        track_y = cy - self._track_h // 2
 
 
 
        painter.setPen(Qt.NoPen)
 
        painter.setBrush(QColor(BORDER))
 
        painter.drawRoundedRect(0, track_y, w, self._track_h, 2, 2)
 
 
 
        val  = self.value()
 
        maxv = self.maximum()
 
        if maxv > 0:
 
            elapsed_w = int((val / maxv) * w)
 
            painter.setBrush(QColor(ACCENT))
 
            painter.drawRoundedRect(0, track_y, elapsed_w, self._track_h, 2, 2)
 
 
 
            hx = elapsed_w
 
            painter.setBrush(QColor(TEXT_PRIMARY))
 
            painter.drawEllipse(
                hx - self._handle_r, cy - self._handle_r,
                self._handle_r * 2, self._handle_r * 2)
 
        painter.end()
 
 
    def sizeHint(self):
 
        return QSize(200, 22)
 
 
    def minimumSizeHint(self):
 
        return QSize(50, 22)
 
 
 
class VolumeSlider(QSlider):
 
    def __init__(self, parent=None):
 
        super().__init__(Qt.Horizontal, parent)
 
        self.setRange(0, 100)
 
        self.setValue(70)
 
        self._track_h = 3
 
 
    def paintEvent(self, event):
 
        painter = QPainter(self)
 
        painter.setRenderHint(QPainter.Antialiasing)
 
        w = self.width()
 
        h = self.height()
 
        cy = h // 2
 
        track_y = cy - self._track_h // 2
 
 
        painter.setPen(Qt.NoPen)
 
        painter.setBrush(QColor(BORDER))
 
        painter.drawRoundedRect(0, track_y, w, self._track_h, 2, 2)
 
 
        val = self.value()
 
        maxv = self.maximum()
 
        if maxv > 0:
 
            filled_w = int((val / maxv) * w)
 
            painter.setBrush(QColor(TEXT_SECONDARY))
 
            painter.drawRoundedRect(0, track_y, filled_w, self._track_h, 2, 2)
 
            r = 5
 
            painter.setBrush(QColor(TEXT_PRIMARY))
 
            painter.drawEllipse(filled_w - r, cy - r, r * 2, r * 2)
 
        painter.end()
 
 
    def sizeHint(self):
 
        return QSize(90, 20)
 
 
 
class IconButton(QPushButton):
 
    """Icon-only button using QPainter-drawn icons."""
 
    def __init__(self, icon_type: str, size: int = 20,
                 color: str = TEXT_SECONDARY, active_color: str = ACCENT,
                 parent=None):
 
        super().__init__(parent)
 
        self._icon_type   = icon_type
 
        self._icon_size   = size
 
        self._color       = QColor(color)
 
        self._active_color= QColor(active_color)
 
        self._active      = False
 
        self._hovered     = False
 
        btn_size = size + 16
 
        self.setFixedSize(btn_size, btn_size)
 
        self.setFlat(True)
 
        self.setCursor(Qt.PointingHandCursor)
 
        self.setStyleSheet("background:transparent;border:none;")
 
 
    def set_active(self, active: bool):
 
        self._active = active
 
        self.update()
 
 
    def enterEvent(self, e):
 
        self._hovered = True
 
        self.update()
 
        super().enterEvent(e)
 
 
    def leaveEvent(self, e):
 
        self._hovered = False
 
        self.update()
 
        super().leaveEvent(e)
 
 
    def paintEvent(self, event):
 
        painter = QPainter(self)
 
        painter.setRenderHint(QPainter.Antialiasing)
 
        if self._hovered:
 
            painter.setBrush(QColor(BG_ELEVATED))
 
            painter.setPen(Qt.NoPen)
 
            painter.drawRoundedRect(self.rect(), 4, 4)
 
        color = self._active_color if self._active else self._color
 
        if self._hovered and not self._active:
 
            color = QColor(TEXT_PRIMARY)
 
        margin = (self.width() - self._icon_size) // 2
 
        icon_rect = self.rect().adjusted(margin, margin, -margin, -margin)
 
        draw_icon(painter, self._icon_type, icon_rect, color)
 
        painter.end()
 
 
 
class BigPlayButton(QPushButton):
 
    """Large circular play/pause button."""
 
    def __init__(self, parent=None):
 
        super().__init__(parent)
 
        self._playing = False
 
        self._hovered = False
 
        self.setFixedSize(48, 48)
 
        self.setCursor(Qt.PointingHandCursor)
 
        self.setFlat(True)
 
        self.setStyleSheet("background:transparent;border:none;")
 
 
    def set_playing(self, playing: bool):
 
        self._playing = playing
 
        self.update()
 
 
    def enterEvent(self, e):
 
        self._hovered = True
 
        self.update()
 
 
    def leaveEvent(self, e):
 
        self._hovered = False
 
        self.update()
 
 
    def paintEvent(self, event):
 
        painter = QPainter(self)
 
        painter.setRenderHint(QPainter.Antialiasing)
 
        r = self.rect()
 
 
        bg = QColor(ACCENT_HOVER) if self._hovered else QColor(ACCENT)
 
        painter.setBrush(QBrush(bg))
 
        painter.setPen(Qt.NoPen)
 
        painter.drawEllipse(r.adjusted(2, 2, -2, -2))
 
 
        icon_rect = r.adjusted(12, 12, -12, -12)
 
        icon_type = 'pause' if self._playing else 'play'
 
        draw_icon(painter, icon_type, icon_rect, QColor(BG_PRIMARY))
 
        painter.end()
 
 
 
class SidebarButton(QPushButton):
 
    def __init__(self, label: str, icon_type: str = None, parent=None):
 
        super().__init__(parent)
 
        self._label     = label
 
        self._icon_type = icon_type
 
        self._active    = False
 
        self._hovered   = False
 
        self.setFlat(True)
 
        self.setCursor(Qt.PointingHandCursor)
 
        self.setFixedHeight(36)
 
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
 
        self.setStyleSheet("background:transparent;border:none;text-align:left;")
 
 
    def set_active(self, active: bool):
 
        self._active = active
 
        self.update()
 
 
    def is_active(self):
 
        return self._active
 
 
    def enterEvent(self, e):
 
        self._hovered = True
 
        self.update()
 
 
    def leaveEvent(self, e):
 
        self._hovered = False
 
        self.update()
 
 
    def paintEvent(self, event):
 
        painter = QPainter(self)
 
        painter.setRenderHint(QPainter.Antialiasing)
 
 
        if self._active:
 
            painter.fillRect(self.rect(), QColor(BG_ELEVATED))
 
            painter.fillRect(0, 0, 2, self.height(), QColor(ACCENT))
 
        elif self._hovered:
 
            painter.fillRect(self.rect(), QColor(BG_SURFACE))
 
 
 
        x = 12
 
        if self._icon_type:
 
            icon_color = QColor(ACCENT) if self._active else QColor(TEXT_SECONDARY)
 
            icon_rect = QRect(x, (self.height() - 16) // 2, 16, 16)
 
            draw_icon(painter, self._icon_type, icon_rect, icon_color)
 
            x += 24
 
 
 
        text_color = QColor(TEXT_PRIMARY) if self._active else QColor(TEXT_SECONDARY)
 
        if self._hovered and not self._active:
 
            text_color = QColor(TEXT_PRIMARY)
 
        painter.setPen(text_color)
 
        painter.setFont(make_font(13, QFont.Normal if not self._active else QFont.DemiBold))
 
        text_rect = QRect(x, 0, self.width() - x - 8, self.height())
 
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter,
                         self._label)
 
        painter.end()
 
 
 
class TrackDelegate(QStyledItemDelegate):
 
    """Custom delegate for TrackTableView — 44px rows, accent left border."""
 
    ROW_H = 44
 
 
    def sizeHint(self, option, index):
 
        return QSize(option.rect.width(), self.ROW_H)
 
 
    def paint(self, painter, option, index):
 
        painter.save()
 
        row   = index.row()
 
        is_sel = option.state & QStyle.State_Selected
 
        is_hov = option.state & QStyle.State_MouseOver
 
 
 
        if is_sel:
 
            painter.fillRect(option.rect, QColor(BG_ELEVATED))
 
 
            painter.fillRect(option.rect.x(), option.rect.y(),
                             2, option.rect.height(), QColor(ACCENT))
 
        elif is_hov:
 
            painter.fillRect(option.rect, QColor('#222222'))
 
        elif row % 2 == 0:
 
            painter.fillRect(option.rect, QColor(BG_SURFACE))
 
        else:
 
            painter.fillRect(option.rect, QColor('#1A1A1A'))
 
 
 
        col = index.column()
 
        data = index.data(Qt.DisplayRole)
 
        if data is None:
 
            painter.restore()
 
            return
 
 
        text_color = QColor(TEXT_PRIMARY) if is_sel else QColor(TEXT_SECONDARY)
 
        if col == 1:
 
            text_color = QColor(TEXT_PRIMARY)
 
            painter.setFont(make_font(13, QFont.DemiBold))
 
        else:
 
            painter.setFont(make_font(12))
 
 
        painter.setPen(text_color)
 
        align = Qt.AlignLeft | Qt.AlignVCenter
 
        if col in (0, 4, 6):
 
            align = Qt.AlignCenter
 
 
        left_pad = 2 if is_sel else 0
 
        text_rect = option.rect.adjusted(left_pad + 8, 0, -8, 0)
 
        painter.drawText(text_rect, align,
                         painter.fontMetrics().elidedText(
                             str(data), Qt.ElideRight, text_rect.width()))
 
        painter.restore()
 
 
 
class TrackTableView(QTableView):
 
    track_double_clicked = pyqtSignal(dict)
 
    context_menu_requested = pyqtSignal(QPoint, dict)
 
 
    def __init__(self, parent=None):
 
        super().__init__(parent)
 
        self.setItemDelegate(TrackDelegate())
 
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
 
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
 
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
 
        self.setShowGrid(False)
 
        self.setSortingEnabled(True)
 
        self.setAlternatingRowColors(False)
 
        self.setMouseTracking(True)
 
        self.horizontalHeader().setStretchLastSection(False)
 
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
 
        self.verticalHeader().setVisible(False)
 
        self.verticalHeader().setDefaultSectionSize(44)
 
        self.setContextMenuPolicy(Qt.CustomContextMenu)
 
        self.customContextMenuRequested.connect(self._on_context_menu)
 
        self.doubleClicked.connect(self._on_double_click)
 
        self.setStyleSheet(f"""
            QTableView {{ 
                background-color: {BG_SURFACE};
                color: {TEXT_PRIMARY};
                border: none;
                outline: none;
            }} 
            QHeaderView::section {{ 
                background-color: {BG_PRIMARY};
                color: {TEXT_MUTED};
                border: none;
                border-bottom: 1px solid {BORDER};
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
            }} 
            QScrollBar:vertical {{ 
                background: {BG_PRIMARY};
                width: 6px;
                margin: 0;
            }} 
            QScrollBar::handle:vertical {{ 
                background: {BORDER};
                border-radius: 3px;
                min-height: 20px;
            }} 
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ 
                height: 0;
            }} 
            QScrollBar:horizontal {{ 
                background: {BG_PRIMARY};
                height: 6px;
            }} 
            QScrollBar::handle:horizontal {{ 
                background: {BORDER};
                border-radius: 3px;
            }} 
        """)
 
 
    def _on_double_click(self, index):
 
        model = self.model()
 
        if not model:
 
            return
 
        source_index = model.mapToSource(index) if hasattr(model, 'mapToSource') else index
 
        src_model = model.sourceModel() if hasattr(model, 'sourceModel') else model
 
        track = src_model.data(src_model.index(source_index.row(), 0),
                               Qt.UserRole + 1)
 
        if track:
 
            self.track_double_clicked.emit(track)
 
 
    def _on_context_menu(self, pos: QPoint):
 
        index = self.indexAt(pos)
 
        if not index.isValid():
 
            return
 
        model = self.model()
 
        source_index = model.mapToSource(index) if hasattr(model, 'mapToSource') else index
 
        src_model = model.sourceModel() if hasattr(model, 'sourceModel') else model
 
        track = src_model.data(src_model.index(source_index.row(), 0),
                               Qt.UserRole + 1)
 
        if track:
 
            self.context_menu_requested.emit(self.viewport().mapToGlobal(pos), track)
 
 
    def setup_columns(self):
 
        hh = self.horizontalHeader()
 
        hh.resizeSection(0, 45)
 
        hh.resizeSection(1, 260)
 
        hh.resizeSection(2, 180)
 
        hh.resizeSection(3, 180)
 
        hh.resizeSection(4, 70)
 
        hh.resizeSection(5, 100)
 
        hh.resizeSection(6, 55)
 
 
 
 
 
 
 
class LibraryView(QWidget):
 
    play_track      = pyqtSignal(dict, list)
 
    add_to_playlist = pyqtSignal(dict, int)
 
 
    def __init__(self, db: Database, parent=None):
 
        super().__init__(parent)
 
        self.db = db
 
        self._playlists = []
 
        self._build_ui()
 
 
    def _build_ui(self):
 
        layout = QVBoxLayout(self)
 
        layout.setContentsMargins(0, 0, 0, 0)
 
        layout.setSpacing(0)
 
 
 
        search_container = QWidget()
 
        search_container.setFixedHeight(52)
 
        search_container.setStyleSheet(f"background:{BG_SURFACE};")
 
        sl = QHBoxLayout(search_container)
 
        sl.setContentsMargins(24, 8, 24, 8)
 
 
        self.search_box = QLineEdit()
 
        self.search_box.setPlaceholderText("Search title, artist, album...")
 
        self.search_box.setStyleSheet(f"""
            QLineEdit {{ 
                background: {BG_ELEVATED};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }} 
            QLineEdit:focus {{ 
                border-color: {ACCENT};
            }} 
        """)
 
        self.search_box.setFont(make_font(13))
 
        self.search_box.textChanged.connect(self._on_search)
 
        sl.addWidget(self.search_box)
 
 
        layout.addWidget(search_container)
 
 
 
        self.model       = TrackTableModel()
 
        self.proxy_model = QSortFilterProxyModel()
 
        self.proxy_model.setSourceModel(self.model)
 
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
 
        self.proxy_model.setFilterKeyColumn(-1)
 
 
        self.table = TrackTableView()
 
        self.table.setModel(self.proxy_model)
 
        self.table.setup_columns()
 
        self.table.track_double_clicked.connect(self._on_track_activated)
 
        self.table.context_menu_requested.connect(self._on_context_menu)
 
 
        layout.addWidget(self.table)
 
 
    def refresh(self):
 
        tracks = self.db.get_all_tracks()
 
        self.model.set_tracks(tracks)
 
        self._playlists = list(self.db.get_all_playlists())
 
 
    def _on_search(self, text: str):
 
        self.proxy_model.setFilterFixedString(text)
 
 
    def _on_track_activated(self, track: dict):
 
        all_ids = self.model.get_all_track_ids()
 
        all_tracks = [self.model.get_track(i)
                      for i in range(self.model.rowCount())]
 
        self.play_track.emit(track, all_tracks)
 
 
    def _on_context_menu(self, pos: QPoint, track: dict):
 
        menu = QMenu(self)
 
        menu.setStyleSheet(self._menu_style())
 
        play_act = menu.addAction("Play")
 
        play_act.triggered.connect(lambda: self._on_track_activated(track))
 
        menu.addSeparator()
 
 
        if self._playlists:
 
            add_menu = menu.addMenu("Add to Playlist")
 
            add_menu.setStyleSheet(self._menu_style())
 
            for pl in self._playlists:
 
                act = add_menu.addAction(pl['name'])
 
                pl_id = pl['id']
 
                act.triggered.connect(
                    lambda checked, pid=pl_id: self.add_to_playlist.emit(track, pid))
 
        menu.exec_(pos)
 
 
    def _menu_style(self):
 
        return f"""
            QMenu {{ 
                background: {BG_ELEVATED};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 4px 0;
            }} 
            QMenu::item {{ 
                padding: 6px 20px;
                font-size: 13px;
            }} 
            QMenu::item:selected {{ 
                background: {BG_SURFACE};
                color: {ACCENT};
            }} 
            QMenu::separator {{ 
                height: 1px;
                background: {BORDER};
                margin: 4px 0;
            }} 
        """
 
 
    def update_playlists(self, playlists):
 
        self._playlists = list(playlists)
 
 
 
 
 
 
 
class AlbumView(QWidget):
 
    play_track = pyqtSignal(dict, list)
 
 
    def __init__(self, db: Database, parent=None):
 
        super().__init__(parent)
 
        self.db = db
 
        self._build_ui()
 
 
    def _build_ui(self):
 
        layout = QVBoxLayout(self)
 
        layout.setContentsMargins(0, 0, 0, 0)
 
        layout.setSpacing(0)
 
 
 
        search_container = QWidget()
 
        search_container.setFixedHeight(52)
 
        search_container.setStyleSheet(f"background:{BG_SURFACE};")
 
        sl = QHBoxLayout(search_container)
 
        sl.setContentsMargins(24, 8, 24, 8)
 
        self.search_box = QLineEdit()
 
        self.search_box.setPlaceholderText("Search albums...")
 
        self.search_box.setStyleSheet(f"""
            QLineEdit {{ 
                background: {BG_ELEVATED};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }} 
            QLineEdit:focus {{  border-color: {ACCENT}; }} 
        """)
 
        self.search_box.textChanged.connect(self._on_search)
 
        sl.addWidget(self.search_box)
 
        layout.addWidget(search_container)
 
 
 
        splitter = QSplitter(Qt.Horizontal)
 
        splitter.setStyleSheet(f"""
            QSplitter::handle {{ 
                background: {BORDER};
                width: 1px;
            }} 
        """)
 
 
        self.album_list = QListWidget()
 
        self.album_list.setStyleSheet(self._list_style())
 
        self.album_list.currentRowChanged.connect(self._on_album_selected)
 
        splitter.addWidget(self.album_list)
 
 
        self.track_model = TrackTableModel()
 
        self.track_proxy = QSortFilterProxyModel()
 
        self.track_proxy.setSourceModel(self.track_model)
 
        self.track_table = TrackTableView()
 
        self.track_table.setModel(self.track_proxy)
 
        self.track_table.setup_columns()
 
        self.track_table.track_double_clicked.connect(self._on_track_activated)
 
        splitter.addWidget(self.track_table)
 
 
        splitter.setSizes([280, 600])
 
        layout.addWidget(splitter)
 
 
        self._albums = []
 
 
    def _list_style(self):
 
        return f"""
            QListWidget {{ 
                background: {BG_PRIMARY};
                color: {TEXT_PRIMARY};
                border: none;
                border-right: 1px solid {BORDER};
                outline: none;
            }} 
            QListWidget::item {{ 
                padding: 10px 16px;
                border-bottom: 1px solid {BORDER};
                font-size: 13px;
            }} 
            QListWidget::item:selected {{ 
                background: {BG_ELEVATED};
                color: {ACCENT};
                border-left: 2px solid {ACCENT};
            }} 
            QListWidget::item:hover:!selected {{ 
                background: {BG_SURFACE};
            }} 
            QScrollBar:vertical {{ 
                background: {BG_PRIMARY};
                width: 6px;
            }} 
            QScrollBar::handle:vertical {{ 
                background: {BORDER};
                border-radius: 3px;
            }} 
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{  height: 0; }} 
        """
 
 
    def refresh(self):
 
        albums = self.db.get_all_albums()
 
        self._albums = [dict(a) for a in albums]
 
        self._populate_list(self._albums)
 
 
    def _populate_list(self, albums):
 
        self.album_list.clear()
 
        for al in albums:
 
            label = al['title']
 
            if al.get('artist'):
 
                label += f"\n{al['artist']}"
 
            item = QListWidgetItem(label)
 
            item.setData(Qt.UserRole, al['id'])
 
            self.album_list.addItem(item)
 
 
    def _on_search(self, text: str):
 
        text = text.lower()
 
        filtered = [a for a in self._albums
                    if text in (a.get('title') or '').lower() or
                       text in (a.get('artist') or '').lower()]
 
        self._populate_list(filtered)
 
 
    def _on_album_selected(self, row: int):
 
        item = self.album_list.item(row)
 
        if not item:
 
            return
 
        album_id = item.data(Qt.UserRole)
 
        tracks = self.db.get_tracks_for_album(album_id)
 
        self.track_model.set_tracks(tracks)
 
 
    def _on_track_activated(self, track: dict):
 
        all_tracks = [self.track_model.get_track(i)
                      for i in range(self.track_model.rowCount())]
 
        self.play_track.emit(track, all_tracks)
 
 
 
 
 
 
 
class ArtistView(QWidget):
 
    play_track = pyqtSignal(dict, list)
 
 
    def __init__(self, db: Database, parent=None):
 
        super().__init__(parent)
 
        self.db = db
 
        self._build_ui()
 
 
    def _build_ui(self):
 
        layout = QVBoxLayout(self)
 
        layout.setContentsMargins(0, 0, 0, 0)
 
        layout.setSpacing(0)
 
 
        search_container = QWidget()
 
        search_container.setFixedHeight(52)
 
        search_container.setStyleSheet(f"background:{BG_SURFACE};")
 
        sl = QHBoxLayout(search_container)
 
        sl.setContentsMargins(24, 8, 24, 8)
 
        self.search_box = QLineEdit()
 
        self.search_box.setPlaceholderText("Search artists...")
 
        self.search_box.setStyleSheet(f"""
            QLineEdit {{ 
                background: {BG_ELEVATED};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }} 
            QLineEdit:focus {{  border-color: {ACCENT}; }} 
        """)
 
        self.search_box.textChanged.connect(self._on_search)
 
        sl.addWidget(self.search_box)
 
        layout.addWidget(search_container)
 
 
        splitter = QSplitter(Qt.Horizontal)
 
        splitter.setStyleSheet(f"""
            QSplitter::handle {{  background: {BORDER}; width: 1px; }} 
        """)
 
 
        self.artist_list = QListWidget()
 
        self.artist_list.setStyleSheet(self._list_style())
 
        self.artist_list.currentRowChanged.connect(self._on_artist_selected)
 
        splitter.addWidget(self.artist_list)
 
 
        self.track_model = TrackTableModel()
 
        self.track_proxy = QSortFilterProxyModel()
 
        self.track_proxy.setSourceModel(self.track_model)
 
        self.track_table = TrackTableView()
 
        self.track_table.setModel(self.track_proxy)
 
        self.track_table.setup_columns()
 
        self.track_table.track_double_clicked.connect(self._on_track_activated)
 
        splitter.addWidget(self.track_table)
 
 
        splitter.setSizes([280, 600])
 
        layout.addWidget(splitter)
 
        self._artists = []
 
 
    def _list_style(self):
 
        return f"""
            QListWidget {{ 
                background: {BG_PRIMARY};
                color: {TEXT_PRIMARY};
                border: none;
                border-right: 1px solid {BORDER};
                outline: none;
            }} 
            QListWidget::item {{ 
                padding: 10px 16px;
                border-bottom: 1px solid {BORDER};
                font-size: 13px;
            }} 
            QListWidget::item:selected {{ 
                background: {BG_ELEVATED};
                color: {ACCENT};
                border-left: 2px solid {ACCENT};
            }} 
            QListWidget::item:hover:!selected {{ 
                background: {BG_SURFACE};
            }} 
            QScrollBar:vertical {{ 
                background: {BG_PRIMARY};
                width: 6px;
            }} 
            QScrollBar::handle:vertical {{ 
                background: {BORDER};
                border-radius: 3px;
            }} 
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{  height: 0; }} 
        """
 
 
    def refresh(self):
 
        artists = self.db.get_all_artists()
 
        self._artists = [dict(a) for a in artists]
 
        self._populate_list(self._artists)
 
 
    def _populate_list(self, artists):
 
        self.artist_list.clear()
 
        for ar in artists:
 
            tc = ar.get('track_count', 0)
 
            label = ar['name']
 
            item = QListWidgetItem(label)
 
            item.setData(Qt.UserRole, ar['id'])
 
            self.artist_list.addItem(item)
 
 
    def _on_search(self, text: str):
 
        text = text.lower()
 
        filtered = [a for a in self._artists
                    if text in (a.get('name') or '').lower()]
 
        self._populate_list(filtered)
 
 
    def _on_artist_selected(self, row: int):
 
        item = self.artist_list.item(row)
 
        if not item:
 
            return
 
        artist_id = item.data(Qt.UserRole)
 
        tracks = self.db.get_tracks_for_artist(artist_id)
 
        self.track_model.set_tracks(tracks)
 
 
    def _on_track_activated(self, track: dict):
 
        all_tracks = [self.track_model.get_track(i)
                      for i in range(self.track_model.rowCount())]
 
        self.play_track.emit(track, all_tracks)
 
 
 
 
 
 
 
class PlaylistView(QWidget):
 
    play_track      = pyqtSignal(dict, list)
 
    playlist_renamed= pyqtSignal(int, str)
 
    playlist_deleted= pyqtSignal(int)
 
    track_removed   = pyqtSignal(int, int)
 
    order_changed   = pyqtSignal(int, list)
 
 
    def __init__(self, db: Database, parent=None):
 
        super().__init__(parent)
 
        self.db = db
 
        self._playlist_id   = None
 
        self._playlist_name = ''
 
        self._build_ui()
 
 
    def _build_ui(self):
 
        layout = QVBoxLayout(self)
 
        layout.setContentsMargins(0, 0, 0, 0)
 
        layout.setSpacing(0)
 
 
 
        header = QWidget()
 
        header.setFixedHeight(52)
 
        header.setStyleSheet(f"background:{BG_SURFACE};border-bottom:1px solid {BORDER};")
 
        hl = QHBoxLayout(header)
 
        hl.setContentsMargins(24, 8, 24, 8)
 
 
        self.title_label = QLabel("Playlist")
 
        self.title_label.setFont(make_font(15, QFont.DemiBold))
 
        self.title_label.setStyleSheet(f"color:{TEXT_PRIMARY};background:transparent;")
 
        hl.addWidget(self.title_label)
 
        hl.addStretch()
 
 
        self.search_box = QLineEdit()
 
        self.search_box.setPlaceholderText("Search...")
 
        self.search_box.setFixedWidth(200)
 
        self.search_box.setStyleSheet(f"""
            QLineEdit {{ 
                background: {BG_ELEVATED};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 13px;
            }} 
            QLineEdit:focus {{  border-color: {ACCENT}; }} 
        """)
 
        self.search_box.textChanged.connect(self._on_search)
 
        hl.addWidget(self.search_box)
 
 
        layout.addWidget(header)
 
 
 
        self.model = PlaylistTrackModel()
 
        self.proxy = QSortFilterProxyModel()
 
        self.proxy.setSourceModel(self.model)
 
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
 
        self.proxy.setFilterKeyColumn(-1)
 
 
        self.table = TrackTableView()
 
        self.table.setModel(self.proxy)
 
        self.table.setup_columns()
 
        self.table.setDragEnabled(True)
 
        self.table.setAcceptDrops(True)
 
        self.table.setDropIndicatorShown(True)
 
        self.table.setDragDropMode(QAbstractItemView.InternalMove)
 
        self.table.track_double_clicked.connect(self._on_track_activated)
 
        self.table.context_menu_requested.connect(self._on_context_menu)
 
        layout.addWidget(self.table)
 
 
        self.model.rowsMoved.connect(self._on_rows_moved)
 
 
    def load_playlist(self, playlist_id: int, name: str):
 
        self._playlist_id   = playlist_id
 
        self._playlist_name = name
 
        self.title_label.setText(name)
 
        tracks = self.db.get_playlist_tracks(playlist_id)
 
        self.model.set_tracks(tracks)
 
 
    def _on_search(self, text: str):
 
        self.proxy.setFilterFixedString(text)
 
 
    def _on_track_activated(self, track: dict):
 
        all_tracks = [self.model.get_track(i)
                      for i in range(self.model.rowCount())]
 
        self.play_track.emit(track, all_tracks)
 
 
    def _on_context_menu(self, pos: QPoint, track: dict):
 
        menu = QMenu(self)
 
        menu.setStyleSheet(self._menu_style())
 
        play_act = menu.addAction("Play")
 
        play_act.triggered.connect(lambda: self._on_track_activated(track))
 
        menu.addSeparator()
 
        rm_act = menu.addAction("Remove from Playlist")
 
        rm_act.triggered.connect(
            lambda: self._remove_track(track))
 
        menu.exec_(pos)
 
 
    def _remove_track(self, track: dict):
 
        if self._playlist_id is None:
 
            return
 
        self.track_removed.emit(self._playlist_id, track['id'])
 
        tracks = self.db.get_playlist_tracks(self._playlist_id)
 
        self.model.set_tracks(tracks)
 
 
    def _on_rows_moved(self):
 
        if self._playlist_id is None:
 
            return
 
        track_ids = [self.model.get_track(i)['id']
                     for i in range(self.model.rowCount())]
 
        self.order_changed.emit(self._playlist_id, track_ids)
 
 
    def _menu_style(self):
 
        return f"""
            QMenu {{ 
                background: {BG_ELEVATED};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 4px 0;
            }} 
            QMenu::item {{  padding: 6px 20px; font-size: 13px; }} 
            QMenu::item:selected {{ 
                background: {BG_SURFACE};
                color: {ACCENT};
            }} 
            QMenu::separator {{ 
                height: 1px;
                background: {BORDER};
                margin: 4px 0;
            }} 
        """
 
 
 
 
 
 
 
 
class FavouritesView(QWidget):
    play_track = pyqtSignal(dict, list)
 
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._build_ui()
 
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        search_container = QWidget()
        search_container.setFixedHeight(52)
        search_container.setStyleSheet(f"background:{BG_SURFACE};")
        sl = QHBoxLayout(search_container)
        sl.setContentsMargins(24, 8, 24, 8)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search favourites...")
        self.search_box.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_ELEVATED};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT}; }}
        """)
        self.search_box.textChanged.connect(self._on_search)
        sl.addWidget(self.search_box)
        layout.addWidget(search_container)
        self.model = TrackTableModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)
        self.table = TrackTableView()
        self.table.setModel(self.proxy_model)
        self.table.setup_columns()
        self.table.track_double_clicked.connect(self._on_track_activated)
        self.table.context_menu_requested.connect(self._on_context_menu)
        layout.addWidget(self.table)
 
    def refresh(self):
        tracks = self.db.get_favourite_tracks()
        self.model.set_tracks(tracks)
 
    def _on_search(self, text):
        self.proxy_model.setFilterFixedString(text)
 
    def _on_track_activated(self, track):
        all_tracks = [self.model.get_track(i) for i in range(self.model.rowCount())]
        self.play_track.emit(track, all_tracks)
 
    def _on_context_menu(self, pos, track):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {BG_ELEVATED};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 4px 0;
            }}
            QMenu::item {{ padding: 6px 20px; font-size: 13px; }}
            QMenu::item:selected {{ background: {BG_SURFACE}; color: {ACCENT}; }}
            QMenu::separator {{ height: 1px; background: {BORDER}; margin: 4px 0; }}
        """)
        play_act = menu.addAction("Play")
        play_act.triggered.connect(lambda: self._on_track_activated(track))
        menu.addSeparator()
        rem_act = menu.addAction("Remove from Favourites")
        tid = track.get('id')
        rem_act.triggered.connect(lambda checked=False, t=tid: (self.db.toggle_favourite(t), self.refresh()))
        menu.exec_(pos)
 
 
class SidebarWidget(QWidget):
 
    section_selected  = pyqtSignal(str)
 
    playlist_selected = pyqtSignal(int, str)
 
    create_playlist   = pyqtSignal()
 
    delete_playlist   = pyqtSignal(int)
 
    rename_playlist   = pyqtSignal(int)
 
 
    NAV_SECTIONS = [
        ('library',    'Library',    'library'),
        ('albums',     'Albums',     'album'),
        ('favourites', 'Favourites', 'heart'),
    ]
 
 
    def __init__(self, parent=None):
 
        super().__init__(parent)
 
        self.setFixedWidth(220)
 
        self.setStyleSheet(f"""
            QWidget {{ 
                background: {BG_PRIMARY};
                border-right: 1px solid {BORDER};
            }} 
        """)
 
        self._playlist_buttons = {}
 
        self._active_section   = 'library'
 
        self._build_ui()
 
 
    def _build_ui(self):
 
        layout = QVBoxLayout(self)
 
        layout.setContentsMargins(0, 0, 0, 0)
 
        layout.setSpacing(0)
 
 
 
        title_widget = QWidget()
 
        title_widget.setFixedHeight(60)
 
        title_widget.setStyleSheet(f"background:{BG_PRIMARY};border-bottom:1px solid {BORDER};")
 
        tl = QHBoxLayout(title_widget)
 
        tl.setContentsMargins(16, 0, 16, 0)
 
        title_lbl = QLabel("PYTHON PLAYER")
 
        title_lbl.setFont(make_font(11, QFont.Bold))
 
        title_lbl.setStyleSheet(f"color:{ACCENT};letter-spacing:2px;background:transparent;border:none;")
 
        tl.addWidget(title_lbl)
 
        layout.addWidget(title_widget)
 
 
 
        nav_header = QLabel("NAVIGATION")
 
        nav_header.setFont(make_font(9, QFont.Bold))
 
        nav_header.setStyleSheet(
            f"color:{TEXT_MUTED};padding:16px 16px 6px 16px;"
            f"letter-spacing:1.5px;background:transparent;border:none;")
 
        layout.addWidget(nav_header)
 
 
 
        self._nav_buttons = {}
 
        for key, label, icon in self.NAV_SECTIONS:
 
            btn = SidebarButton(label, icon)
 
            btn.clicked.connect(self._make_nav_slot(key))
 
            layout.addWidget(btn)
 
            self._nav_buttons[key] = btn
 
 
 
        div = QFrame()
 
        div.setFrameShape(QFrame.HLine)
 
        div.setStyleSheet(f"color:{BORDER};background:{BORDER};max-height:1px;border:none;")
 
        layout.addWidget(div)
 
 
 
        pl_header_widget = QWidget()
 
        pl_header_widget.setFixedHeight(36)
 
        pl_header_widget.setStyleSheet("background:transparent;border:none;")
 
        plhl = QHBoxLayout(pl_header_widget)
 
        plhl.setContentsMargins(16, 0, 8, 0)
 
 
        pl_lbl = QLabel("PLAYLISTS")
 
        pl_lbl.setFont(make_font(9, QFont.Bold))
 
        pl_lbl.setStyleSheet(
            f"color:{TEXT_MUTED};letter-spacing:1.5px;background:transparent;border:none;")
 
        plhl.addWidget(pl_lbl)
 
        plhl.addStretch()
 
 
        add_pl_btn = IconButton('add', 14, TEXT_MUTED, ACCENT)
 
        add_pl_btn.setToolTip("New Playlist")
 
        add_pl_btn.clicked.connect(self.create_playlist.emit)
 
        plhl.addWidget(add_pl_btn)
 
        layout.addWidget(pl_header_widget)
 
 
 
        self.pl_scroll = QScrollArea()
 
        self.pl_scroll.setWidgetResizable(True)
 
        self.pl_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
 
        self.pl_scroll.setStyleSheet(f"""
            QScrollArea {{ 
                background: transparent;
                border: none;
            }} 
            QScrollBar:vertical {{ 
                background: {BG_PRIMARY};
                width: 4px;
            }} 
            QScrollBar::handle:vertical {{ 
                background: {BORDER};
                border-radius: 2px;
            }} 
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{  height: 0; }} 
        """)
 
 
        self.pl_container = QWidget()
 
        self.pl_container.setStyleSheet("background:transparent;border:none;")
 
        self.pl_layout = QVBoxLayout(self.pl_container)
 
        self.pl_layout.setContentsMargins(0, 0, 0, 0)
 
        self.pl_layout.setSpacing(0)
 
        self.pl_layout.addStretch()
 
 
        self.pl_scroll.setWidget(self.pl_container)
 
        layout.addWidget(self.pl_scroll)
 
 
 
        layout.addStretch()
 
        settings_btn = SidebarButton("Settings", "settings")
 
        settings_btn.clicked.connect(self._make_nav_slot('settings'))
 
        layout.addWidget(settings_btn)
 
        self._nav_buttons['settings'] = settings_btn
 
 
 
        self._set_active('library')
 
 
    def _make_nav_slot(self, key: str):
 
        def slot():
 
            self._set_active(key)
 
            self.section_selected.emit(key)
 
        return slot
 
 
    def _set_active(self, key: str):
 
        self._active_section = key
 
        for k, btn in self._nav_buttons.items():
 
            btn.set_active(k == key)
 
 
        for pid, btn in self._playlist_buttons.items():
 
            btn.set_active(False)
 
 
    def set_playlists(self, playlists: list):
 
 
        for pid, btn in self._playlist_buttons.items():
 
            self.pl_layout.removeWidget(btn)
 
            btn.deleteLater()
 
        self._playlist_buttons.clear()
 
 
        stretch = self.pl_layout.takeAt(0) if self.pl_layout.count() > 0 else None
 
 
        for pl in playlists:
 
            btn = SidebarButton(pl['name'], 'playlist')
 
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
 
            pl_id   = pl['id']
 
            pl_name = pl['name']
 
            btn.clicked.connect(self._make_pl_slot(pl_id, pl_name))
 
            btn.customContextMenuRequested.connect(
                self._make_pl_context(pl_id))
 
            self.pl_layout.addWidget(btn)
 
            self._playlist_buttons[pl_id] = btn
 
 
        self.pl_layout.addStretch()
 
 
    def _make_pl_slot(self, pl_id: int, pl_name: str):
 
        def slot():
 
            for k, btn in self._nav_buttons.items():
 
                btn.set_active(False)
 
            for pid, btn in self._playlist_buttons.items():
 
                btn.set_active(pid == pl_id)
 
            self.playlist_selected.emit(pl_id, pl_name)
 
        return slot
 
 
    def _make_pl_context(self, pl_id: int):
 
        def slot(pos: QPoint):
 
            menu = QMenu(self)
 
            menu.setStyleSheet(f"""
                QMenu {{ 
                    background: {BG_ELEVATED};
                    color: {TEXT_PRIMARY};
                    border: 1px solid {BORDER};
                    border-radius: 4px;
                    padding: 4px 0;
                }} 
                QMenu::item {{  padding: 6px 20px; font-size: 13px; }} 
                QMenu::item:selected {{ 
                    background: {BG_SURFACE};
                    color: {ACCENT};
                }} 
            """)
 
            ren = menu.addAction("Rename")
 
            ren.triggered.connect(lambda: self.rename_playlist.emit(pl_id))
 
            dlt = menu.addAction("Delete")
 
            dlt.triggered.connect(lambda: self.delete_playlist.emit(pl_id))
 
            btn = self._playlist_buttons.get(pl_id)
 
            if btn:
 
                menu.exec_(btn.mapToGlobal(pos))
 
        return slot
 
 
 
 
 
 
 
class NowPlayingBar(QWidget):
 
    def __init__(self, audio: AudioPlayer, db=None, parent=None):
 
        super().__init__(parent)
 
        self.audio = audio
        self.db = db
 
        self.setFixedHeight(80)
 
        self._dragging_seek  = False
 
        self._dragging_vol   = False
 
        self._build_ui()
 
        self._connect_signals()
 
 
    def _build_ui(self):
 
        self.setStyleSheet(f"""
            NowPlayingBar {{ 
                background: {BG_PRIMARY};
                border-top: 1px solid {BORDER};
            }} 
        """)
 
        main_layout = QVBoxLayout(self)
 
        main_layout.setContentsMargins(0, 0, 0, 0)
 
        main_layout.setSpacing(0)
 
 
 
        seek_row = QWidget()
 
        seek_row.setFixedHeight(18)
 
        seek_row.setStyleSheet("background:transparent;")
 
        seek_rl = QHBoxLayout(seek_row)
 
        seek_rl.setContentsMargins(0, 0, 0, 0)
 
        seek_rl.setSpacing(0)
 
 
        self.pos_label = QLabel("0:00")
 
        self.pos_label.setFixedWidth(38)
 
        self.pos_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
 
        self.pos_label.setFont(make_font(10))
 
        self.pos_label.setStyleSheet(f"color:{TEXT_MUTED};background:transparent;")
 
 
        self.seek_slider = WaveformSlider(Qt.Horizontal)
 
        self.seek_slider.sliderPressed.connect(self._seek_pressed)
 
        self.seek_slider.sliderReleased.connect(self._seek_released)
 
        self.seek_slider.sliderMoved.connect(self._seek_moved)
 
 
        self.dur_label = QLabel("0:00")
 
        self.dur_label.setFixedWidth(38)
 
        self.dur_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
 
        self.dur_label.setFont(make_font(10))
 
        self.dur_label.setStyleSheet(f"color:{TEXT_MUTED};background:transparent;")
 
 
        seek_rl.addWidget(self.pos_label)
 
        seek_rl.addWidget(self.seek_slider)
 
        seek_rl.addWidget(self.dur_label)
 
        main_layout.addWidget(seek_row)
 
 
 
        controls_row = QWidget()
 
        controls_row.setStyleSheet("background:transparent;")
 
        cl = QHBoxLayout(controls_row)
 
        cl.setContentsMargins(16, 0, 16, 0)
 
        cl.setSpacing(0)
 
 
 
        self.info_widget = QWidget()
 
        self.info_widget.setStyleSheet("background:transparent;")
 
        info_l = QVBoxLayout(self.info_widget)
 
        info_l.setContentsMargins(0, 0, 0, 0)
 
        info_l.setSpacing(2)
 
 
        self.track_label = QLabel("No track selected")
 
        self.track_label.setFont(make_font(14, QFont.DemiBold))
 
        self.track_label.setStyleSheet(
            f"color:{TEXT_PRIMARY};background:transparent;")
 
 
        self.artist_label = QLabel("")
 
        self.artist_label.setFont(make_font(12))
 
        self.artist_label.setStyleSheet(
            f"color:{TEXT_SECONDARY};background:transparent;")
 
 
        info_row = QWidget()
        info_row.setStyleSheet("background:transparent;")
        info_hl = QHBoxLayout(info_row)
        info_hl.setContentsMargins(0, 0, 0, 0)
        info_hl.setSpacing(8)
        info_hl.addWidget(self.track_label)
        self.btn_heart = IconButton('heart', 18, TEXT_MUTED, '#E05252')
        self.btn_heart.setToolTip("Add to Favourites")
        self.btn_heart._is_fav = False
        self.btn_heart.clicked.connect(self._toggle_favourite)
        info_hl.addWidget(self.btn_heart)
        info_hl.addStretch()
        info_l.addWidget(info_row)
        info_l.addWidget(self.artist_label)
 
 
 
        center_widget = QWidget()
 
        center_widget.setStyleSheet("background:transparent;")
 
        center_l = QHBoxLayout(center_widget)
 
        center_l.setContentsMargins(0, 0, 0, 0)
 
        center_l.setSpacing(4)
 
        center_l.setAlignment(Qt.AlignCenter)
 
 
        self.btn_shuffle = IconButton('shuffle', 18, TEXT_MUTED, ACCENT)
 
        self.btn_shuffle.setToolTip("Shuffle")
 
        self.btn_shuffle.clicked.connect(self._toggle_shuffle)
 
 
        self.btn_prev = IconButton('prev', 20, TEXT_SECONDARY, TEXT_PRIMARY)
 
        self.btn_prev.setToolTip("Previous")
 
        self.btn_prev.clicked.connect(self.audio.prev_track)
 
 
        self.btn_play = BigPlayButton()
 
        self.btn_play.setToolTip("Play / Pause")
 
        self.btn_play.clicked.connect(self._toggle_play)
 
 
        self.btn_next = IconButton('next', 20, TEXT_SECONDARY, TEXT_PRIMARY)
 
        self.btn_next.setToolTip("Next")
 
        self.btn_next.clicked.connect(self.audio.next_track)
 
 
        self.btn_repeat = IconButton('repeat', 18, TEXT_MUTED, ACCENT)
 
        self.btn_repeat.setToolTip("Repeat")
 
        self.btn_repeat.clicked.connect(self._cycle_repeat)
 
 
        center_l.addWidget(self.btn_shuffle)
 
        center_l.addSpacing(8)
 
        center_l.addWidget(self.btn_prev)
 
        center_l.addSpacing(4)
 
        center_l.addWidget(self.btn_play)
 
        center_l.addSpacing(4)
 
        center_l.addWidget(self.btn_next)
 
        center_l.addSpacing(8)
 
        center_l.addWidget(self.btn_repeat)
 
 
 
        vol_widget = QWidget()
 
        vol_widget.setStyleSheet("background:transparent;")
 
        vol_l = QHBoxLayout(vol_widget)
 
        vol_l.setContentsMargins(0, 0, 0, 0)
 
        vol_l.setSpacing(6)
 
        vol_l.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
 
 
        self.btn_mute = IconButton('volume', 18, TEXT_MUTED, TEXT_SECONDARY)
 
        self.btn_mute.setToolTip("Mute / Unmute")
 
        self.btn_mute.clicked.connect(self._toggle_mute)
 
 
        self.vol_slider = VolumeSlider()
 
        self.vol_slider.setFixedWidth(90)
 
        self.vol_slider.setValue(self.audio.get_volume())
 
        self.vol_slider.valueChanged.connect(self._on_volume_changed)
 
 
        vol_l.addWidget(self.btn_mute)
 
        vol_l.addWidget(self.vol_slider)
 
 
        cl.addWidget(self.info_widget, 1)
 
        cl.addWidget(center_widget, 0)
 
        cl.addWidget(vol_widget, 1)
 
 
        main_layout.addWidget(controls_row)
 
 
    def _connect_signals(self):
 
        self.audio.track_changed.connect(self._on_track_changed)
 
        self.audio.playback_state.connect(self._on_playback_state)
 
        self.audio.position_changed.connect(self._on_position_changed)
 
        self.audio.duration_changed.connect(self._on_duration_changed)
 
 
 
 
    def _on_track_changed(self, track: dict):
 
        title  = track.get('title')  or 'Unknown Title'
 
        artist = track.get('artist') or 'Unknown Artist'
 
        album  = track.get('album')  or ''
 
        self.track_label.setText(title)
 
        artist_text = artist
 
        if album:
 
            artist_text += f"  —  {album}"
 
        self.artist_label.setText(artist_text)
 
 
    def _on_playback_state(self, state: str):
 
        self.btn_play.set_playing(state == 'playing')
 
 
    def _on_position_changed(self, pos: int):
 
        if not self._dragging_seek:
 
            dur = self.audio.get_duration()
 
            if dur > 0:
 
                self.seek_slider.setValue(int((pos / dur) * 1000))
 
            self.pos_label.setText(format_duration(pos))
 
 
    def _on_duration_changed(self, dur: int):
 
        self.dur_label.setText(format_duration(dur))
 
 
    def _seek_pressed(self):
 
        self._dragging_seek = True
 
 
    def _seek_released(self):
 
        self._dragging_seek = False
 
        val = self.seek_slider.value()
 
        dur = self.audio.get_duration()
 
        if dur > 0:
 
            self.audio.seek(int((val / 1000) * dur))
 
 
    def _seek_moved(self, val: int):
 
        dur = self.audio.get_duration()
 
        if dur > 0:
 
            ms = int((val / 1000) * dur)
 
            self.pos_label.setText(format_duration(ms))
 
 
    def _toggle_favourite(self):
        track = self.audio.get_current_track()
        if not track:
            return
        tid = track.get('id')
        if tid is None or self.db is None:
            return
        is_fav = self.db.toggle_favourite(tid)
        self._set_heart_state(is_fav)
        mw = self.window()
        if hasattr(mw, 'favourites_view'):
            mw.favourites_view.refresh()
 
    def _set_heart_state(self, is_fav: bool):
        self.btn_heart._color = QColor('#E05252') if is_fav else QColor(TEXT_MUTED)
        self.btn_heart._active_color = QColor('#FF6B6B') if is_fav else QColor('#E05252')
        self.btn_heart._active = is_fav
        self.btn_heart.update()
 
    def _toggle_play(self):
 
        if self.audio.is_playing():
 
            self.audio.pause()
 
        else:
 
            self.audio.play()
 
 
    def _toggle_shuffle(self):
 
        current = self.btn_shuffle.is_active() if hasattr(self.btn_shuffle, 'is_active') else False
 
        current = self.audio._shuffle
 
        self.audio.set_shuffle(not current)
 
        self.btn_shuffle.set_active(not current)
 
 
    def _cycle_repeat(self):
 
        current = self.audio._repeat
 
        next_mode = (current + 1) % 3
 
        self.audio.set_repeat(next_mode)
 
        self.btn_repeat.set_active(next_mode != AudioPlayer.REPEAT_NONE)
 
        if next_mode == AudioPlayer.REPEAT_ONE:
 
            self.btn_repeat._icon_type = 'repeat_one'
 
        else:
 
            self.btn_repeat._icon_type = 'repeat'
 
        self.btn_repeat.update()
 
 
    def _toggle_mute(self):
 
        muted = self.audio.toggle_mute()
 
        self.btn_mute._icon_type = 'mute' if muted else 'volume'
 
        self.btn_mute.update()
 
 
    def _on_volume_changed(self, val: int):
 
        self.audio.set_volume(val)
 
 
 
 
 
 
 
class SettingsDialog(QDialog):
 
    scan_requested = pyqtSignal(str)
 
 
    def __init__(self, parent=None):
 
        super().__init__(parent)
 
        self.setWindowTitle("Settings")
 
        self.setFixedSize(480, 300)
 
        self.setModal(True)
 
        self.setStyleSheet(f"""
            QDialog {{ 
                background: {BG_ELEVATED};
                color: {TEXT_PRIMARY};
            }} 
            QLabel {{ 
                color: {TEXT_PRIMARY};
                background: transparent;
            }} 
            QPushButton {{ 
                background: {BG_SURFACE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 13px;
            }} 
            QPushButton:hover {{ 
                background: {BG_ELEVATED};
                border-color: {ACCENT};
                color: {ACCENT};
            }} 
            QPushButton:pressed {{ 
                background: {BG_PRIMARY};
            }} 
            QLineEdit {{ 
                background: {BG_SURFACE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }} 
            QLineEdit:focus {{ 
                border-color: {ACCENT};
            }} 
        """)
 
        self._build_ui()
 
 
    def _build_ui(self):
 
        layout = QVBoxLayout(self)
 
        layout.setContentsMargins(28, 24, 28, 24)
 
        layout.setSpacing(20)
 
 
 
        title = QLabel("Settings")
 
        title.setFont(make_font(18, QFont.DemiBold))
 
        layout.addWidget(title)
 
 
 
        scan_lbl = QLabel("Import Music Folder")
 
        scan_lbl.setFont(make_font(12, QFont.DemiBold))
 
        scan_lbl.setStyleSheet(f"color:{TEXT_SECONDARY};")
 
        layout.addWidget(scan_lbl)
 
 
        path_row = QHBoxLayout()
 
        self.folder_edit = QLineEdit()
 
        self.folder_edit.setPlaceholderText("Select a folder to scan for music...")
 
        path_row.addWidget(self.folder_edit)
 
 
        browse_btn = QPushButton("Browse")
 
        browse_btn.clicked.connect(self._browse_folder)
 
        path_row.addWidget(browse_btn)
 
 
        layout.addLayout(path_row)
 
 
        self.progress_label = QLabel("")
 
        self.progress_label.setFont(make_font(11))
 
        self.progress_label.setStyleSheet(f"color:{TEXT_MUTED};")
 
        layout.addWidget(self.progress_label)
 
 
        layout.addStretch()
 
 
 
        btn_row = QHBoxLayout()
 
        btn_row.addStretch()
 
 
        cancel_btn = QPushButton("Cancel")
 
        cancel_btn.clicked.connect(self.reject)
 
        btn_row.addWidget(cancel_btn)
 
 
        self.scan_btn = QPushButton("Scan Folder")
 
        self.scan_btn.setStyleSheet(f"""
            QPushButton {{ 
                background: {ACCENT};
                color: {BG_PRIMARY};
                border: none;
                border-radius: 4px;
                padding: 6px 20px;
                font-size: 13px;
                font-weight: 600;
            }} 
            QPushButton:hover {{ 
                background: {ACCENT_HOVER};
            }} 
        """)
 
        self.scan_btn.clicked.connect(self._do_scan)
 
        btn_row.addWidget(self.scan_btn)
 
 
        layout.addLayout(btn_row)
 
 
    def _browse_folder(self):
 
        folder = QFileDialog.getExistingDirectory(
            self, "Select Music Folder",
            str(Path.home() / 'Music'))
 
        if folder:
 
            self.folder_edit.setText(folder)
 
 
    def _do_scan(self):
 
        folder = self.folder_edit.text().strip()
 
        if not folder or not os.path.isdir(folder):
 
            QMessageBox.warning(self, "Invalid Folder",
                                "Please select a valid folder.")
 
            return
 
        self.scan_btn.setEnabled(False)
 
        self.progress_label.setText("Scanning...")
 
        self.scan_requested.emit(folder)
 
 
    def update_progress(self, current: int, total: int, file: str):
 
        fn = Path(file).name
 
        self.progress_label.setText(f"[{current}/{total}] {fn}")
 
 
    def scan_done(self, count: int):
 
        self.progress_label.setText(f"Done. {count} tracks imported.")
 
        self.scan_btn.setEnabled(True)
 
 
 
 
 
 
 
class MainWindow(QMainWindow):
 
    def __init__(self):
 
        super().__init__()
 
        global APP_FONT
 
        APP_FONT = get_app_font()
 
 
        self.db    = Database()
 
        self.audio = AudioPlayer(self)
 
        self._scan_worker = None
 
        self._settings_dialog = None
 
        self._current_playlist_id = None
 
 
        self.setWindowTitle("Python Player")
 
        self.setMinimumSize(1100, 660)
 
        self.resize(1280, 760)
 
        self._apply_palette()
 
        self._build_ui()
 
        self._connect_signals()
 
        self._load_library()
 
 
    def _apply_palette(self):
 
        palette = QPalette()
 
        palette.setColor(QPalette.Window,      QColor(BG_PRIMARY))
 
        palette.setColor(QPalette.Base,        QColor(BG_SURFACE))
 
        palette.setColor(QPalette.AlternateBase, QColor(BG_ELEVATED))
 
        palette.setColor(QPalette.Text,        QColor(TEXT_PRIMARY))
 
        palette.setColor(QPalette.ButtonText,  QColor(TEXT_PRIMARY))
 
        palette.setColor(QPalette.Button,      QColor(BG_ELEVATED))
 
        palette.setColor(QPalette.Highlight,   QColor(ACCENT))
 
        palette.setColor(QPalette.HighlightedText, QColor(BG_PRIMARY))
 
        self.setPalette(palette)
 
        self.setStyleSheet(f"""
            QMainWindow {{ 
                background: {BG_PRIMARY};
            }} 
            QToolTip {{ 
                background: {BG_ELEVATED};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 12px;
            }} 
        """)
 
 
    def _build_ui(self):
 
        central = QWidget()
 
        self.setCentralWidget(central)
 
        root_layout = QVBoxLayout(central)
 
        root_layout.setContentsMargins(0, 0, 0, 0)
 
        root_layout.setSpacing(0)
 
 
 
        top_widget = QWidget()
 
        top_layout = QHBoxLayout(top_widget)
 
        top_layout.setContentsMargins(0, 0, 0, 0)
 
        top_layout.setSpacing(0)
 
 
 
        self.sidebar = SidebarWidget()
 
        top_layout.addWidget(self.sidebar)
 
 
 
        self.content_area = QWidget()
 
        self.content_area.setStyleSheet(f"background:{BG_SURFACE};")
 
        self.content_layout = QVBoxLayout(self.content_area)
 
        self.content_layout.setContentsMargins(0, 0, 0, 0)
 
        self.content_layout.setSpacing(0)
 
 
 
        self.library_view  = LibraryView(self.db)
 
        self.album_view    = AlbumView(self.db)
 
        self.playlist_view = PlaylistView(self.db)
 
        self.favourites_view = FavouritesView(self.db)
 
 
        self.section_header = QWidget()
 
        self.section_header.setFixedHeight(56)
 
        shl = QHBoxLayout(self.section_header)
 
        shl.setContentsMargins(24, 0, 24, 0)
 
        self.section_title = QLabel("Library")
 
        self.section_title.setFont(make_font(20, QFont.Bold))
 
        self.section_title.setStyleSheet(
            f"color:{TEXT_PRIMARY};background:transparent;")
 
        shl.addWidget(self.section_title)
 
        shl.addStretch()
 
        self.track_count_label = QLabel("")
 
        self.track_count_label.setFont(make_font(12))
 
        self.track_count_label.setStyleSheet(
            f"color:{TEXT_MUTED};background:transparent;")
 
        shl.addWidget(self.track_count_label)
 
 
        self.content_layout.addWidget(self.section_header)
 
        self.content_layout.addWidget(self.library_view)
 
 
 
        self.album_view.hide()
 
        self.playlist_view.hide()
 
        self.favourites_view.hide()
 
        self.content_layout.addWidget(self.album_view)
 
        self.content_layout.addWidget(self.playlist_view)
 
        self.content_layout.addWidget(self.favourites_view)
 
        top_layout.addWidget(self.content_area, 1)
 
        root_layout.addWidget(top_widget, 1)
 
        self.player_bar = NowPlayingBar(self.audio, self.db)
 
        root_layout.addWidget(self.player_bar)
 
 
    def _connect_signals(self):
 
 
        self.sidebar.section_selected.connect(self._on_section_selected)
 
        self.sidebar.playlist_selected.connect(self._on_playlist_selected)
 
        self.sidebar.create_playlist.connect(self._create_playlist)
 
        self.sidebar.delete_playlist.connect(self._delete_playlist)
 
        self.sidebar.rename_playlist.connect(self._rename_playlist)
 
 
 
        self.library_view.play_track.connect(self._on_play_track)
 
        self.library_view.add_to_playlist.connect(self._on_add_to_playlist)
 
 
 
        self.album_view.play_track.connect(self._on_play_track)
 
 
 
        self.playlist_view.play_track.connect(self._on_play_track)
 
        self.playlist_view.track_removed.connect(self._on_remove_from_playlist)
 
        self.playlist_view.order_changed.connect(self._on_playlist_order_changed)
 
 
    def _show_view(self, view_name: str):
 
        views = {
            'library'    : self.library_view,
            'albums'     : self.album_view,
            'favourites' : self.favourites_view,
            'playlist'   : self.playlist_view,
        }
 
        for name, w in views.items():
 
            w.setVisible(name == view_name)
 
 
    def _load_library(self):
 
        self.library_view.refresh()
 
        count = len(self.db.get_all_tracks())
 
        self.track_count_label.setText(f"{count} tracks")
 
        self._refresh_playlists()
 
 
    def _refresh_playlists(self):
 
        playlists = list(self.db.get_all_playlists())
 
        self.sidebar.set_playlists(playlists)
 
        self.library_view.update_playlists(playlists)
 
 
 
 
    def _on_section_selected(self, key: str):
 
        if key == 'library':
 
            self._show_view('library')
 
            self.section_title.setText("Library")
 
            count = len(self.db.get_all_tracks())
 
            self.track_count_label.setText(f"{count} tracks")
 
 
        elif key == 'albums':
 
            self._show_view('albums')
 
            self.section_title.setText("Albums")
 
            self.album_view.refresh()
 
            count = len(self.db.get_all_albums())
 
            self.track_count_label.setText(f"{count} albums")
 
 
        elif key == 'favourites':
 
            self._show_view('favourites')
 
            self.section_title.setText("Favourites")
 
            self.favourites_view.refresh()
 
            count = len(self.db.get_favourite_tracks())
 
            self.track_count_label.setText(f"{count} tracks")
 
 
        elif key == 'settings':
 
            self._open_settings()
 
 
    def _on_playlist_selected(self, pl_id: int, pl_name: str):
 
        self._current_playlist_id = pl_id
 
        self._show_view('playlist')
 
        self.section_title.setText(pl_name)
 
        self.playlist_view.load_playlist(pl_id, pl_name)
 
        tracks = self.db.get_playlist_tracks(pl_id)
 
        self.track_count_label.setText(f"{len(tracks)} tracks")
 
 
 
 
    def _on_play_track(self, track: dict, queue: list):
 
        self.audio.set_queue(queue if queue else [track],
                             queue.index(track) if track in queue else 0)
 
 
 
 
    def _create_playlist(self):
 
        name, ok = QInputDialog.getText(
            self, "New Playlist", "Playlist name:",
            QLineEdit.Normal, "New Playlist")
 
        if ok and name.strip():
 
            self.db.create_playlist(name.strip())
 
            self._refresh_playlists()
 
 
    def _delete_playlist(self, pl_id: int):
 
        reply = QMessageBox.question(
            self, "Delete Playlist",
            "Are you sure you want to delete this playlist?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
 
        if reply == QMessageBox.Yes:
 
            self.db.delete_playlist(pl_id)
 
            self._refresh_playlists()
 
 
            if self._current_playlist_id == pl_id:
 
                self._current_playlist_id = None
 
                self._show_view('library')
 
                self.section_title.setText("Library")
 
 
    def _rename_playlist(self, pl_id: int):
 
 
        playlists = {pl['id']: pl['name']
                     for pl in self.db.get_all_playlists()}
 
        current_name = playlists.get(pl_id, '')
 
        name, ok = QInputDialog.getText(
            self, "Rename Playlist", "New name:",
            QLineEdit.Normal, current_name)
 
        if ok and name.strip():
 
            self.db.rename_playlist(pl_id, name.strip())
 
            self._refresh_playlists()
 
            if self._current_playlist_id == pl_id:
 
                self.section_title.setText(name.strip())
 
 
    def _on_add_to_playlist(self, track: dict, pl_id: int):
 
        self.db.add_track_to_playlist(pl_id, track['id'])
 
        if self._current_playlist_id == pl_id:
 
            self.playlist_view.load_playlist(
                pl_id,
                self.playlist_view._playlist_name)
 
 
    def _on_remove_from_playlist(self, pl_id: int, track_id: int):
 
        self.db.remove_track_from_playlist(pl_id, track_id)
 
 
    def _on_playlist_order_changed(self, pl_id: int, track_ids: list):
 
        for pos, tid in enumerate(track_ids):
 
            self.db.reorder_playlist_track(pl_id, tid, pos)
 
 
 
 
    def _open_settings(self):
 
        if self._settings_dialog is None or not self._settings_dialog.isVisible():
 
            self._settings_dialog = SettingsDialog(self)
 
            self._settings_dialog.scan_requested.connect(self._start_scan)
 
        self._settings_dialog.show()
 
        self._settings_dialog.raise_()
 
 
    def _start_scan(self, folder: str):
 
        if self._scan_worker and self._scan_worker.isRunning():
 
            return
 
        self._scan_worker = ScanWorker(folder, self.db)
 
        self._scan_worker.progress.connect(self._on_scan_progress)
 
        self._scan_worker.finished.connect(self._on_scan_finished)
 
        self._scan_worker.error.connect(self._on_scan_error)
 
        self._scan_worker.start()
 
 
    def _on_scan_progress(self, current: int, total: int, file: str):
 
        if self._settings_dialog:
 
            self._settings_dialog.update_progress(current, total, file)
 
 
    def _on_scan_finished(self, count: int):
 
        if self._settings_dialog:
 
            self._settings_dialog.scan_done(count)
 
        self.library_view.refresh()
 
        track_count = len(self.db.get_all_tracks())
 
        self.track_count_label.setText(f"{track_count} tracks")
 
 
    def _on_scan_error(self, msg: str):
 
        QMessageBox.critical(self, "Scan Error", f"Error during scan:\n{msg}")
 
        if self._settings_dialog:
 
            self._settings_dialog.scan_btn.setEnabled(True)
 
            self._settings_dialog.progress_label.setText("Error.")
 
 
    def closeEvent(self, event):
 
        self.audio.stop()
 
        if self._scan_worker and self._scan_worker.isRunning():
 
            self._scan_worker.terminate()
 
            self._scan_worker.wait(2000)
 
        self.db.close()
 
        event.accept()
 
 
 
 
 
 
 
def main():
 
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        pass
    app = QApplication(sys.argv)
 
    app.setApplicationName("Python Player")
 
    app.setApplicationVersion("1.0.0")
 
    app.setOrganizationName("PythonPlayer")
 
 
    global APP_FONT
 
    APP_FONT = get_app_font()
 
    font = QFont(APP_FONT, 13)
 
    app.setFont(font)
 
 
    window = MainWindow()
 
    window.show()
 
    sys.exit(app.exec_())
 
 
 
if __name__ == '__main__':
 
    main()