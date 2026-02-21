#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI Configuration - Costanti per lo stile visivo.

Definisce i colori, i font e i parametri di stile
per l'interfaccia utente "Geometra Dark Mode".
"""

__date__ = "2026-02-21"
__version__ = "1.0.0"
__author__ = "Gemini CLI"

from typing import Dict, Tuple, Any

# --- PALETTE COLORI (Dark High-Contrast) ---
COLOR_BG_MAIN = "#222222"      # Sfondo principale (Grigio scuro)
COLOR_BG_PANEL = "#333333"     # Sfondo pannelli/frame
COLOR_FG_TEXT = "#FFFFFF"      # Testo principale (Bianco puro)
COLOR_ACCENT = "#00FF00"       # Accento azioni/menu (Verde "Matrix")
COLOR_WARN = "#FFFF00"         # Avvisi/Log (Giallo)
COLOR_ERROR = "#FF0000"        # Errori/Cursore (Rosso)
COLOR_ENTRY_BG = "#000000"     # Sfondo campi input
COLOR_ENTRY_FG = "#FFFFFF"     # Testo campi input
COLOR_SELECT_BG = "#00FF00"    # Sfondo selezione
COLOR_SELECT_FG = "#000000"    # Testo selezione

# --- FONT ---
FONT_MAIN: Tuple[str, int, str] = ("Helvetica", 12, "normal")
FONT_HEADER: Tuple[str, int, str] = ("Helvetica", 14, "bold")
FONT_TITLE: Tuple[str, int, str] = ("Helvetica", 16, "bold")
FONT_MONO: Tuple[str, int, str] = ("Courier New", 11, "normal")  # Per tabelle e log

# --- CONFIGURAZIONE WIDGET GENERICI ---
DEFAULT_PADX = 10
DEFAULT_PADY = 5

def get_entry_style() -> Dict[str, Any]:
    """
    Restituisce lo stile standard per i campi di input.
    
    Returns:
        Dizionario con parametri di configurazione per Entry/Text.
    """
    style = {
        "bg": COLOR_ENTRY_BG,
        "fg": COLOR_ENTRY_FG,
        "insertbackground": COLOR_ERROR,  # Cursore rosso
        "insertwidth": 2,
        "font": FONT_MAIN,
        "relief": "flat",
        "bd": 2
    }
    return style

def get_button_style() -> Dict[str, Any]:
    """
    Restituisce lo stile base per i pulsanti.
    
    Returns:
        Dizionario con parametri di configurazione per Button.
    """
    style = {
        "bg": COLOR_BG_PANEL,
        "fg": COLOR_ACCENT,
        "activebackground": COLOR_ACCENT,
        "activeforeground": COLOR_BG_MAIN,
        "font": FONT_HEADER,
        "relief": "raised",
        "bd": 2,
        "cursor": "hand2"
    }
    return style
