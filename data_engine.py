#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Engine - Modulo di persistenza dati.

Gestisce la connessione al database SQLite, le operazioni CRUD
su Prezzario e Preventivi, assicurando l'integrità dei dati.
"""

__date__ = "2026-02-21"
__version__ = "1.0.0"
__author__ = "Gemini CLI"

import sqlite3
import csv
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

DB_FILENAME = "computa_ai.db"

# --- Modelli Dati (Semplificati per compatibilità con Tkinter) ---

@dataclass
class PriceItem:
    """Modello per una voce di prezzario."""
    id: Optional[int]
    code: str
    description: str
    unit: str
    price: float
    category: str

@dataclass
class QuoteHeader:
    """Modello per la testata di un preventivo."""
    id: Optional[int]
    customer_name: str
    date_created: str
    total_amount: float
    notes: str

@dataclass
class QuoteLineItem:
    """Modello per una riga di preventivo."""
    id: Optional[int]
    quote_id: int
    item_code: str
    description: str
    quantity: float
    unit_price: float
    total_price: float
    unit: str


class DataManager:
    """Gestore centrale delle operazioni su database."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Inizializza il DataManager.
        
        Args:
            db_path: Percorso del file database. Se None, usa il locale in data/.
        """
        if db_path is None:
            # Crea il DB nella cartella data/ all'interno di prv/
            base_dir = Path(__file__).parent
            data_dir = base_dir / "data"
            if not data_dir.exists():
                data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = data_dir / DB_FILENAME
        else:
            self.db_path = db_path
            
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Ottiene una connessione al DB con row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Crea le tabelle se non esistono."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabella Prezzario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                unit TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT
            )
        """)
        
        # Tabella Testate Preventivi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                date_created TEXT NOT NULL,
                total_amount REAL DEFAULT 0.0,
                notes TEXT
            )
        """)
        
        # Tabella Righe Preventivi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quote_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id INTEGER NOT NULL,
                item_code TEXT,
                description TEXT,
                quantity REAL NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                unit TEXT,
                FOREIGN KEY (quote_id) REFERENCES quotes (id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()

    # --- CRUD PREZZARIO ---

    def add_price_item(self, item: PriceItem) -> bool:
        """Aggiunge una voce al prezzario."""
        conn = self._get_connection()
        cursor = conn.cursor()
        success = False
        
        try:
            cursor.execute("""
                INSERT INTO price_list (code, description, unit, price, category)
                VALUES (?, ?, ?, ?, ?)
            """, (item.code, item.description, item.unit, item.price, item.category))
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            print(f"ERRORE: Codice {item.code} già esistente.")
            success = False
        except Exception as e:
            print(f"ERRORE DB: {e}")
            success = False
        finally:
            conn.close()
            
        return success

    def update_price_item(self, item: PriceItem) -> bool:
        """Aggiorna una voce esistente."""
        conn = self._get_connection()
        cursor = conn.cursor()
        success = False
        
        try:
            cursor.execute("""
                UPDATE price_list 
                SET description=?, unit=?, price=?, category=?
                WHERE code=?
            """, (item.description, item.unit, item.price, item.category, item.code))
            conn.commit()
            success = True
        except Exception as e:
            print(f"ERRORE DB Update: {e}")
            success = False
        finally:
            conn.close()
            
        return success
    
    def delete_price_item(self, code: str) -> bool:
        """Elimina una voce dal prezzario."""
        conn = self._get_connection()
        cursor = conn.cursor()
        success = False
        
        try:
            cursor.execute("DELETE FROM price_list WHERE code=?", (code,))
            conn.commit()
            success = True
        except Exception as e:
            print(f"ERRORE DB Delete: {e}")
            success = False
        finally:
            conn.close()
            
        return success

    def clear_price_list(self) -> bool:
        """Svuota completamente il prezzario."""
        conn = self._get_connection()
        cursor = conn.cursor()
        success = False
        try:
            cursor.execute("DELETE FROM price_list")
            conn.commit()
            success = True
        except Exception as e:
            print(f"ERRORE DB Clear: {e}")
            success = False
        finally:
            conn.close()
        return success

    def get_all_price_items(self) -> List[PriceItem]:
        """Restituisce tutte le voci del prezzario."""
        conn = self._get_connection()
        cursor = conn.cursor()
        items = []
        
        try:
            cursor.execute("SELECT * FROM price_list ORDER BY category, code")
            rows = cursor.fetchall()
            for row in rows:
                item = PriceItem(
                    id=row['id'],
                    code=row['code'],
                    description=row['description'],
                    unit=row['unit'],
                    price=row['price'],
                    category=row['category']
                )
                items.append(item)
        except Exception as e:
            print(f"ERRORE DB Select: {e}")
            items = []
        finally:
            conn.close()
            
        return items
    
    def search_price_items(self, query: str) -> List[PriceItem]:
        """Cerca voci per codice o descrizione."""
        conn = self._get_connection()
        cursor = conn.cursor()
        items = []
        search_term = f"%{query}%"
        
        try:
            cursor.execute("""
                SELECT * FROM price_list 
                WHERE code LIKE ? OR description LIKE ? OR category LIKE ?
                ORDER BY code
            """, (search_term, search_term, search_term))
            
            rows = cursor.fetchall()
            for row in rows:
                item = PriceItem(
                    id=row['id'],
                    code=row['code'],
                    description=row['description'],
                    unit=row['unit'],
                    price=row['price'],
                    category=row['category']
                )
                items.append(item)
        finally:
            conn.close()
            
        return items

    # --- CRUD PREVENTIVI ---

    def create_quote(self, customer_name: str, notes: str = "") -> Optional[int]:
        """Crea una nuova testata preventivo."""
        conn = self._get_connection()
        cursor = conn.cursor()
        quote_id = None
        
        try:
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO quotes (customer_name, date_created, total_amount, notes)
                VALUES (?, ?, 0.0, ?)
            """, (customer_name, date_str, notes))
            conn.commit()
            quote_id = cursor.lastrowid
        except Exception as e:
            print(f"ERRORE DB Create Quote: {e}")
            quote_id = None
        finally:
            conn.close()
            
        return quote_id
        
    def add_quote_item(self, line_item: QuoteLineItem) -> bool:
        """Aggiunge una riga al preventivo e ricalcola il totale."""
        conn = self._get_connection()
        cursor = conn.cursor()
        success = False
        
        try:
            # 1. Inserisci riga
            cursor.execute("""
                INSERT INTO quote_items (quote_id, item_code, description, quantity, unit_price, total_price, unit)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (line_item.quote_id, line_item.item_code, line_item.description, 
                  line_item.quantity, line_item.unit_price, line_item.total_price, line_item.unit))
            
            # 2. Aggiorna totale testata
            cursor.execute("""
                UPDATE quotes 
                SET total_amount = (SELECT SUM(total_price) FROM quote_items WHERE quote_id = ?)
                WHERE id = ?
            """, (line_item.quote_id, line_item.quote_id))
            
            conn.commit()
            success = True
        except Exception as e:
            print(f"ERRORE DB Add Quote Item: {e}")
            success = False
        finally:
            conn.close()
            
        return success
        
    def get_quotes(self) -> List[QuoteHeader]:
        """Restituisce la lista dei preventivi."""
        conn = self._get_connection()
        cursor = conn.cursor()
        quotes = []
        
        try:
            cursor.execute("SELECT * FROM quotes ORDER BY date_created DESC")
            rows = cursor.fetchall()
            for row in rows:
                quote = QuoteHeader(
                    id=row['id'],
                    customer_name=row['customer_name'],
                    date_created=row['date_created'],
                    total_amount=row['total_amount'],
                    notes=row['notes']
                )
                quotes.append(quote)
        finally:
            conn.close()
            
        return quotes
        
    def get_quote_details(self, quote_id: int) -> Tuple[Optional[QuoteHeader], List[QuoteLineItem]]:
        """Restituisce testata e righe di un preventivo."""
        conn = self._get_connection()
        cursor = conn.cursor()
        header = None
        items = []
        
        try:
            # Recupera Testata
            cursor.execute("SELECT * FROM quotes WHERE id = ?", (quote_id,))
            row = cursor.fetchone()
            if row:
                header = QuoteHeader(
                    id=row['id'],
                    customer_name=row['customer_name'],
                    date_created=row['date_created'],
                    total_amount=row['total_amount'],
                    notes=row['notes']
                )
                
                # Recupera Righe
                cursor.execute("SELECT * FROM quote_items WHERE quote_id = ?", (quote_id,))
                rows_items = cursor.fetchall()
                for ri in rows_items:
                    item = QuoteLineItem(
                        id=ri['id'],
                        quote_id=ri['quote_id'],
                        item_code=ri['item_code'],
                        description=ri['description'],
                        quantity=ri['quantity'],
                        unit_price=ri['unit_price'],
                        total_price=ri['total_price'],
                        unit=ri['unit']
                    )
                    items.append(item)
                    
        except Exception as e:
            print(f"ERRORE DB Get Quote Details: {e}")
            header = None
            items = []
        finally:
            conn.close()
            
        return header, items

    def delete_quote(self, quote_id: int) -> bool:
        """Elimina un preventivo e le sue righe (CASCADE gestito da DB o manuale)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        success = False
        
        try:
            # Cancellazione righe esplicita per sicurezza
            cursor.execute("DELETE FROM quote_items WHERE quote_id = ?", (quote_id,))
            cursor.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
            conn.commit()
            success = True
        except Exception as e:
            print(f"ERRORE DB Delete Quote: {e}")
            success = False
        finally:
            conn.close()
            
        return success
        
    def delete_quote_item(self, item_id: int, quote_id: int) -> bool:
        """Elimina una riga e ricalcola il totale."""
        conn = self._get_connection()
        cursor = conn.cursor()
        success = False
        
        try:
            cursor.execute("DELETE FROM quote_items WHERE id = ?", (item_id,))
            
            # Ricalcola totale
            cursor.execute("""
                UPDATE quotes 
                SET total_amount = COALESCE((SELECT SUM(total_price) FROM quote_items WHERE quote_id = ?), 0)
                WHERE id = ?
            """, (quote_id, quote_id))
            
            conn.commit()
            success = True
        except Exception as e:
            print(f"ERRORE DB Delete Item: {e}")
            success = False
        finally:
            conn.close()
            
        return success

    def import_from_csv(self, csv_path: str) -> int:
        """
        Importa voci di prezzario da un file CSV in modo robusto.
        Utilizza indici fissi per evitare problemi con header multi-riga.
        """
        path_obj = Path(csv_path)
        if not path_obj.exists():
            return 0
            
        count = 0
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            with path_obj.open("r", encoding="utf-8") as f:
                # Usa reader semplice per evitare problemi con i nomi delle colonne
                reader = csv.reader(f, delimiter='|')
                
                # Salta l'intestazione (che può essere su più righe nel file originale)
                header_skipped = False
                
                for row in reader:
                    # Salta la prima riga se contiene 'Tariffa' o se è la prima del ciclo
                    if not header_skipped:
                        header_skipped = True
                        if row and "Tariffa" in row[0]:
                            continue
                    
                    if len(row) < 4:
                        continue
                        
                    code = row[0].strip()
                    desc = row[1].strip()
                    unit = row[2].strip()
                    price_str = row[3].replace(",", ".").strip()
                    
                    if not code or not desc:
                        continue
                        
                    try:
                        price = float(price_str)
                    except ValueError:
                        price = 0.0
                        
                    cursor.execute("""
                        INSERT OR IGNORE INTO price_list (code, description, unit, price, category)
                        VALUES (?, ?, ?, ?, ?)
                    """, (code, desc, unit, price, "Edile"))
                    
                    if cursor.rowcount > 0:
                        count += 1
                        
            conn.commit()
        except Exception as e:
            print(f"ERRORE Import CSV: {e}")
        finally:
            conn.close()
            
        return count

    def get_stats(self) -> Dict[str, int]:
        """Restituisce il numero totale di voci e preventivi."""
        conn = self._get_connection()
        cursor = conn.cursor()
        stats = {"prices": 0, "quotes": 0}
        
        try:
            cursor.execute("SELECT COUNT(*) FROM price_list")
            stats["prices"] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM quotes")
            stats["quotes"] = cursor.fetchone()[0]
        finally:
            conn.close()
            
        return stats
