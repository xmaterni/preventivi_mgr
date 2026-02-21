#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Preventivi Manager - Versione Professionale Definitiva v1.5.0.
Standalone, Dialoghi SÌ/NO Colorati, Selettore File Navigabile Senza Campi Testo.
"""

__date__ = "2026-02-21"
__version__ = "1.5.0"
__author__ = "Gemini CLI"

import sys
import os
import tkinter as tk
from tkinter import ttk, simpledialog
from pathlib import Path
from typing import Optional, List, Any, Dict, Callable

# Import locali diretti
import gui_config as cfg
from data_engine import DataManager, PriceItem, QuoteHeader, QuoteLineItem


class PreventiviApp:
    """Classe principale dell'applicazione GUI."""

    def __init__(self, root: tk.Tk, db_manager: DataManager):
        """Inizializza l'interfaccia."""
        self.root = root
        self.db = db_manager
        
        # Configurazione Finestra
        self.root.title(f"Computa.AI - Gestione Preventivi v{__version__}")
        self.root.geometry("1150x850")
        self.root.configure(bg=cfg.COLOR_BG_MAIN)
        
        # Stato Ordinamento
        self.sort_order = {
            "prices": {"col": None, "reverse": False},
            "quotes": {"col": None, "reverse": False},
            "items": {"col": None, "reverse": False}
        }
        
        # Percorso corrente per il selettore file personalizzato
        self.current_browser_path = Path(__file__).parent
        
        self._setup_styles()
        self._create_header()
        self._create_widgets()

    def _setup_styles(self) -> None:
        """Configura il tema scuro."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=cfg.COLOR_BG_MAIN, foreground=cfg.COLOR_FG_TEXT, font=cfg.FONT_MAIN)
        style.configure("TNotebook", background=cfg.COLOR_BG_MAIN, borderwidth=0)
        style.configure("TNotebook.Tab", background=cfg.COLOR_BG_PANEL, foreground=cfg.COLOR_FG_TEXT, padding=[15, 8], font=cfg.FONT_HEADER)
        style.map("TNotebook.Tab", background=[("selected", cfg.COLOR_ACCENT)], foreground=[("selected", cfg.COLOR_BG_MAIN)])
        style.configure("Treeview", background="#222222", foreground="white", fieldbackground="#222222", font=cfg.FONT_MONO, rowheight=28)
        style.configure("Treeview.Heading", background="black", foreground=cfg.COLOR_ACCENT, font=cfg.FONT_HEADER)
        style.map("Treeview", background=[("selected", cfg.COLOR_ACCENT)], foreground=[("selected", "black")])

    def _create_header(self) -> None:
        """Barra superiore con Help e Esci."""
        header = tk.Frame(self.root, bg="#111111", height=60)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="  GESTIONALE PREVENTIVI EDILE ", bg="#111111", fg=cfg.COLOR_ACCENT, font=cfg.FONT_TITLE).pack(side=tk.LEFT, padx=10)
        
        # Pulsanti Uscita (Rosso) e Guida (Grigio)
        tk.Button(header, text=" ESCI ", command=self.root.quit, bg="#AA0000", fg="white", font=cfg.FONT_HEADER, relief="flat", padx=20).pack(side=tk.RIGHT, padx=10, pady=10)
        tk.Button(header, text=" GUIDA ", command=self._show_help, bg="#444444", fg=cfg.COLOR_WARN, font=cfg.FONT_HEADER, relief="flat", padx=20).pack(side=tk.RIGHT, padx=5, pady=10)

    def _custom_confirm(self, title: str, message: str, callback_yes: Callable) -> None:
        """Finestra di conferma con pulsanti grandi SÌ (VERDE) a sinistra e NO (ROSSO) a destra."""
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("450x220")
        win.configure(bg=cfg.COLOR_BG_PANEL)
        win.transient(self.root)
        win.grab_set()
        win.geometry(f"+{self.root.winfo_x() + 350}+{self.root.winfo_y() + 300}")
        
        tk.Label(win, text=message, bg=cfg.COLOR_BG_PANEL, fg="white", font=cfg.FONT_HEADER, pady=25, wraplength=400).pack()
        
        btn_frame = tk.Frame(win, bg=cfg.COLOR_BG_PANEL)
        btn_frame.pack(fill=tk.X, pady=10)
        
        def on_yes(): win.destroy(); callback_yes()
        def on_no(): win.destroy()

        # SÌ a sinistra (Verde), NO a destra (Rosso)
        tk.Button(btn_frame, text="  SÌ  ", command=on_yes, bg="#008800", fg="white", font=cfg.FONT_HEADER, width=12).pack(side=tk.LEFT, padx=40)
        tk.Button(btn_frame, text="  NO  ", command=on_no, bg="#AA0000", fg="white", font=cfg.FONT_HEADER, width=12).pack(side=tk.RIGHT, padx=40)

    def _create_widgets(self) -> None:
        """Crea i widget principali."""
        self.status_bar = tk.Label(self.root, text="Inizializzazione...", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg=cfg.COLOR_BG_PANEL, fg=cfg.COLOR_ACCENT)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tab_prices = ttk.Frame(self.notebook); self.notebook.add(self.tab_prices, text="  GESTIONE PREZZARIO  ")
        self._build_prices_tab()
        
        self.tab_quotes = ttk.Frame(self.notebook); self.notebook.add(self.tab_quotes, text="  GESTIONE PREVENTIVI  ")
        self._build_quotes_tab()
        
        self._update_status()

    def _update_status(self) -> None:
        stats = self.db.get_stats()
        self.status_bar.config(text=f" Database Attivo | Voci: {stats['prices']} | Preventivi: {stats['quotes']}")

    def _show_help(self) -> None:
        """Manuale tecnico dell'applicazione."""
        h_win = tk.Toplevel(self.root); h_win.title("Guida Tecnica"); h_win.geometry("750x650"); h_win.configure(bg="#000000")
        txt = tk.Text(h_win, bg="#000000", fg="#FFFFFF", font=cfg.FONT_MONO, padx=30, pady=30, wrap=tk.WORD)
        txt.pack(fill=tk.BOTH, expand=True)
        h_txt = """MANUALE OPERATIVO - GESTIONALE PREVENTIVI
======================================================================

1. GESTIONE PREZZARIO
----------------------------------------------------------------------
• IMPORTA CSV: Scegli un file CSV dal tuo computer. Puoi navigare tra 
  le cartelle cliccando sui nomi e selezionare il file desiderato. 
  Non c'è alcun campo di testo "Nome File" superfluo.
• ORDINAMENTO: Clicca sull'intestazione di una colonna per ordinare 
  i dati (A-Z / Z-A).
• AZIONI RIGA: NUOVO, SALVA e ELIMINA SINGOLA VOCE.
• AZIONI TABELLA: IMPORTA CSV e CANCELLA PREZZARIO.

2. GESTIONE PREVENTIVI
----------------------------------------------------------------------
• NUOVO PREVENTIVO: Inserisci il nome cliente.
• AGGIUNGI VOCE: Seleziona la lavorazione e indica la quantità.
• ESPORTA TXT: Salva il preventivo formattato in 'exports/'.

3. COMANDI DI SISTEMA
----------------------------------------------------------------------
• ESCI: Chiude il programma (tasto rosso in alto).
• CONFERME: Usa SÌ (VERDE) a sinistra o NO (ROSSO) a destra.

======================================================================
"""
        txt.insert(tk.END, h_txt); txt.config(state=tk.DISABLED)
        tk.Button(h_win, text="CHIUDI", command=h_win.destroy, bg="#333333", fg="white").pack(pady=15)

    def _build_prices_tab(self) -> None:
        """Costruisce la scheda prezzario con scrollbar e pulsanti ordinati."""
        left = tk.Frame(self.tab_prices, bg=cfg.COLOR_BG_MAIN); left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=10)
        t_frame = tk.Frame(left, bg=cfg.COLOR_BG_MAIN); t_frame.pack(fill=tk.BOTH, expand=True)
        cols = ("Codice", "Categoria", "Descrizione", "U.M.", "Prezzo")
        self.tree_prices = ttk.Treeview(t_frame, columns=cols, show="headings")
        w = {"Codice": 90, "Categoria": 110, "Descrizione": 500, "U.M.": 60, "Prezzo": 80}
        for c in cols:
            self.tree_prices.heading(c, text=c, command=lambda x=c: self._sort_tree("prices", self.tree_prices, x))
            self.tree_prices.column(c, width=w[c], anchor="w" if c == "Descrizione" else "center")
        vsb = ttk.Scrollbar(t_frame, orient="vertical", command=self.tree_prices.yview); hsb = ttk.Scrollbar(t_frame, orient="horizontal", command=self.tree_prices.xview)
        self.tree_prices.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree_prices.grid(row=0, column=0, sticky='nsew'); vsb.grid(row=0, column=1, sticky='ns'); hsb.grid(row=1, column=0, sticky='ew')
        t_frame.grid_rowconfigure(0, weight=1); t_frame.grid_columnconfigure(0, weight=1)
        self.tree_prices.bind("<<TreeviewSelect>>", self._on_price_select)

        right = tk.Frame(self.tab_prices, bg=cfg.COLOR_BG_PANEL, width=320); right.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=10); right.pack_propagate(False)
        tk.Label(right, text="DETTAGLIO VOCE", bg=cfg.COLOR_BG_PANEL, fg=cfg.COLOR_ACCENT, font=cfg.FONT_TITLE).pack(pady=15)
        self.form_vars = {"code": tk.StringVar(), "cat": tk.StringVar(), "desc": tk.StringVar(), "um": tk.StringVar(), "price": tk.DoubleVar(value=0.0)}
        labels = [("Codice:", "code"), ("Categoria:", "cat"), ("Descrizione:", "desc"), ("U.M.:", "um"), ("Prezzo €:", "price")]
        for l_t, v_n in labels:
            tk.Label(right, text=l_t, bg=cfg.COLOR_BG_PANEL, fg="white").pack(anchor="w", padx=15)
            tk.Entry(right, textvariable=self.form_vars[v_n], **cfg.get_entry_style()).pack(fill=tk.X, padx=15, pady=(0, 10))
            
        b_frame = tk.Frame(right, bg=cfg.COLOR_BG_PANEL); b_frame.pack(fill=tk.X, padx=15, pady=10)
        b_style = cfg.get_button_style()
        
        # --- LOGICA PULSANTI: DISTINZIONE RIGA / TABELLA ---
        # Gruppo Azioni su Riga
        tk.Button(b_frame, text="NUOVO", command=self._clear_price_form, **b_style).pack(fill=tk.X, pady=2)
        tk.Button(b_frame, text="SALVA / AGGIORNA", command=self._save_price, **b_style).pack(fill=tk.X, pady=2)
        tk.Button(b_frame, text="ELIMINA SINGOLA VOCE", command=self._delete_price, **b_style).pack(fill=tk.X, pady=2)
        
        tk.Frame(b_frame, height=40, bg=cfg.COLOR_BG_PANEL).pack() # Separatore
        
        # Gruppo Azioni su Tabella
        tk.Button(b_frame, text="IMPORTA CSV", command=self._custom_file_browser, **b_style).pack(fill=tk.X, pady=2)
        tk.Button(b_frame, text="CANCELLA PREZZARIO", command=lambda: self._custom_confirm("Reset Totale", "Svuotare TUTTO il prezzario?", self._do_clear_table), bg="#660000", fg="white", font=cfg.FONT_HEADER).pack(fill=tk.X, pady=10)
        self._load_prices()

    def _custom_file_browser(self) -> None:
        """Selettore file navigabile senza alcun campo 'Nome File' inutile."""
        win = tk.Toplevel(self.root); win.title("Naviga e Seleziona CSV"); win.geometry("600x500"); win.configure(bg=cfg.COLOR_BG_PANEL)
        win.transient(self.root); win.grab_set(); win.geometry(f"+{self.root.winfo_x() + 250}+{self.root.winfo_y() + 150}")
        
        # Variabile per il percorso attuale
        path_var = tk.StringVar(value=str(self.current_browser_path))
        tk.Label(win, textvariable=path_var, bg=cfg.COLOR_BG_PANEL, fg=cfg.COLOR_ACCENT, wraplength=550).pack(pady=5)
        
        lb = tk.Listbox(win, bg="#111111", fg="#FFFFFF", font=cfg.FONT_MONO, borderwidth=0, highlightthickness=1)
        lb.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        def refresh_lb():
            lb.delete(0, tk.END)
            lb.insert(tk.END, ".. [Torna Su]")
            try:
                # Cartelle
                for p in sorted(self.current_browser_path.iterdir()):
                    if p.is_dir() and not p.name.startswith("."):
                        lb.insert(tk.END, f"DIR: {p.name}")
                # File CSV
                for p in sorted(self.current_browser_path.glob("*.csv")):
                    lb.insert(tk.END, p.name)
            except Exception as e:
                lb.insert(tk.END, f"ERRORE: {e}")

        def on_double_click(event):
            sel = lb.curselection()
            if not sel: return
            name = lb.get(sel[0])
            if name == ".. [Torna Su]":
                self.current_browser_path = self.current_browser_path.parent
                path_var.set(str(self.current_browser_path)); refresh_lb()
            elif name.startswith("DIR: "):
                dir_name = name[5:]
                self.current_browser_path = self.current_browser_path / dir_name
                path_var.set(str(self.current_browser_path)); refresh_lb()
            elif name.endswith(".csv"):
                do_load() # Carica se doppio clic su CSV

        def do_load():
            sel = lb.curselection()
            if not sel: return
            name = lb.get(sel[0])
            if name.endswith(".csv") and not name.startswith("DIR: "):
                full_path = self.current_browser_path / name
                win.destroy()
                count = self.db.import_from_csv(str(full_path))
                if count > 0:
                    self._load_prices(); self._update_status()
                    self._custom_confirm("Import Successo", f"Importate {count} voci correttamente.", lambda: None)
            elif name.startswith("DIR: ") or name == ".. [Torna Su]":
                # Navigazione con tasto carica se cartella selezionata
                if name == ".. [Torna Su]": self.current_browser_path = self.current_browser_path.parent
                else: self.current_browser_path = self.current_browser_path / name[5:]
                path_var.set(str(self.current_browser_path)); refresh_lb()

        lb.bind("<Double-Button-1>", on_double_click); refresh_lb()
        
        f = tk.Frame(win, bg=cfg.COLOR_BG_PANEL); f.pack(fill=tk.X, pady=15)
        # CARICA (Verde) e ANNULLA (Rosso)
        tk.Button(f, text="  CARICA SELEZIONATO  ", command=do_load, bg="#008800", fg="white", font=cfg.FONT_HEADER).pack(side=tk.LEFT, padx=30)
        tk.Button(f, text="  ANNULLA  ", command=win.destroy, bg="#AA0000", fg="white", font=cfg.FONT_HEADER).pack(side=tk.RIGHT, padx=30)

    def _sort_tree(self, group: str, tree: ttk.Treeview, col: str) -> None:
        rev = False
        if self.sort_order[group]["col"] == col: rev = not self.sort_order[group]["reverse"]
        self.sort_order[group]["col"] = col; self.sort_order[group]["reverse"] = rev
        data = [(tree.set(k, col), k) for k in tree.get_children('')]
        try: data.sort(key=lambda t: float(t[0].replace(',', '.')), reverse=rev)
        except ValueError: data.sort(reverse=rev)
        for i, (v, k) in enumerate(data): tree.move(k, '', i)

    def _do_clear_table(self): self.db.clear_price_list(); self._load_prices()

    def _load_prices(self, items: Optional[List[PriceItem]] = None) -> None:
        for r in self.tree_prices.get_children(): self.tree_prices.delete(r)
        data = items if items else self.db.get_all_price_items()
        for i in data: self.tree_prices.insert("", tk.END, values=(i.code, i.category, i.description, i.unit, f"{i.price:.2f}"))
        self._update_status()

    def _on_price_select(self, e) -> None:
        s = self.tree_prices.selection()
        if not s: return
        v = self.tree_prices.item(s[0])['values']
        self.form_vars["code"].set(v[0]); self.form_vars["cat"].set(v[1]); self.form_vars["desc"].set(v[2]); self.form_vars["um"].set(v[3]); self.form_vars["price"].set(float(v[4]))

    def _clear_price_form(self) -> None:
        for k in self.form_vars: self.form_vars[k].set(0.0 if k == "price" else "")

    def _save_price(self) -> None:
        it = PriceItem(None, self.form_vars["code"].get(), self.form_vars["desc"].get(), self.form_vars["um"].get(), self.form_vars["price"].get(), self.form_vars["cat"].get())
        if not it.code: return
        if self.db.add_price_item(it): self._load_prices(); self._clear_price_form()
        else:
            def upd(): self.db.update_price_item(it); self._load_prices()
            self._custom_confirm("Update", "Voce esistente. Aggiornare?", upd)

    def _delete_price(self) -> None:
        c = self.form_vars["code"].get()
        if c: self._custom_confirm("Elimina", f"Eliminare voce {c}?", lambda: [self.db.delete_price_item(c), self._load_prices(), self._clear_price_form()])

    # --- TAB PREVENTIVI ---

    def _build_quotes_tab(self) -> None:
        paned = tk.PanedWindow(self.tab_quotes, orient=tk.HORIZONTAL, bg=cfg.COLOR_BG_MAIN)
        paned.pack(fill=tk.BOTH, expand=True)
        f_list = tk.Frame(paned, bg=cfg.COLOR_BG_MAIN, width=380); paned.add(f_list)
        tk.Button(f_list, text="+ NUOVO PREVENTIVO", command=self._new_quote_dialog, **cfg.get_button_style()).pack(fill=tk.X, padx=10, pady=10)
        cols_q = ("ID", "Cliente", "Data", "Totale €")
        self.tree_quotes = ttk.Treeview(f_list, columns=cols_q, show="headings")
        qw = {"ID": 40, "Cliente": 140, "Data": 90, "Totale €": 90}
        for c in cols_q: self.tree_quotes.heading(c, text=c, command=lambda x=c: self._sort_tree("quotes", self.tree_quotes, x)); self.tree_quotes.column(c, width=qw[c], anchor="center")
        self.tree_quotes.pack(fill=tk.BOTH, expand=True, padx=10); self.tree_quotes.bind("<<TreeviewSelect>>", self._on_quote_select)
        
        self.frame_detail = tk.Frame(paned, bg=cfg.COLOR_BG_PANEL); paned.add(self.frame_detail)
        self.lbl_quote_title = tk.Label(self.frame_detail, text="Seleziona un preventivo", font=cfg.FONT_TITLE, bg=cfg.COLOR_BG_PANEL, fg=cfg.COLOR_ACCENT)
        self.lbl_quote_title.pack(pady=15)
        tool = tk.Frame(self.frame_detail, bg=cfg.COLOR_BG_PANEL); tool.pack(fill=tk.X, padx=15)
        tk.Button(tool, text="AGGIUNGI VOCE", command=self._add_item_dialog, **cfg.get_button_style()).pack(side=tk.LEFT, padx=5)
        tk.Button(tool, text="ESPORTA TXT", command=self._export_quote, bg="#005500", fg="white", font=cfg.FONT_HEADER).pack(side=tk.LEFT, padx=5)
        tk.Button(tool, text="ELIMINA RIGA", command=lambda: self._custom_confirm("Elimina Riga", "Rimuovere riga selezionata?", self._do_delete_quote_item), bg="#880000", fg="white", font=cfg.FONT_HEADER).pack(side=tk.RIGHT, padx=5)
        
        i_frame = tk.Frame(self.frame_detail, bg=cfg.COLOR_BG_PANEL); i_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        cols_i = ("ID", "Codice", "Descrizione", "Q.tà", "UM", "Prezzo Unit.", "Totale")
        self.tree_items = ttk.Treeview(i_frame, columns=cols_i, show="headings")
        iw = {"ID": 30, "Codice": 90, "Descrizione": 380, "Q.tà": 60, "UM": 40, "Prezzo Unit.": 90, "Totale": 90}
        for c in cols_i: self.tree_items.heading(c, text=c, command=lambda x=c: self._sort_tree("items", self.tree_items, x)); self.tree_items.column(c, width=iw[c])
        iv = ttk.Scrollbar(i_frame, orient="vertical", command=self.tree_items.yview); ih = ttk.Scrollbar(i_frame, orient="horizontal", command=self.tree_items.xview)
        self.tree_items.configure(yscrollcommand=iv.set, xscrollcommand=ih.set)
        self.tree_items.grid(row=0, column=0, sticky='nsew'); iv.grid(row=0, column=1, sticky='ns'); ih.grid(row=1, column=0, sticky='ew')
        i_frame.grid_rowconfigure(0, weight=1); i_frame.grid_columnconfigure(0, weight=1)
        self._load_quotes_list(); self.current_quote_id = None

    def _load_quotes_list(self) -> None:
        for r in self.tree_quotes.get_children(): self.tree_quotes.delete(r)
        for q in self.db.get_quotes(): self.tree_quotes.insert("", tk.END, values=(q.id, q.customer_name, q.date_created.split()[0], f"{q.total_amount:.2f}"))
        self._update_status()

    def _new_quote_dialog(self) -> None:
        n = simpledialog.askstring("Nuovo Preventivo", "Nome Cliente:")
        if n and n.strip():
            if self.db.create_quote(n.strip()): self._load_quotes_list()

    def _on_quote_select(self, e) -> None:
        s = self.tree_quotes.selection()
        if s: self.current_quote_id = int(self.tree_quotes.item(s[0])['values'][0]); self._load_quote_detail(self.current_quote_id)

    def _load_quote_detail(self, q_id: int) -> None:
        for r in self.tree_items.get_children(): self.tree_items.delete(r)
        h, items = self.db.get_quote_details(q_id)
        if h:
            self.lbl_quote_title.config(text=f"CLIENTE: {h.customer_name.upper()} | TOTALE: € {h.total_amount:.2f}")
            for i in items: self.tree_items.insert("", tk.END, values=(i.id, i.item_code, i.description, i.quantity, i.unit, f"{i.unit_price:.2f}", f"{i.total_price:.2f}"))

    def _add_item_dialog(self) -> None:
        if not self.current_quote_id: return
        top = tk.Toplevel(self.root); top.title("Selettore Voci"); top.geometry("750x550"); top.configure(bg=cfg.COLOR_BG_MAIN)
        cols = ("Codice", "Descrizione", "Prezzo")
        t = ttk.Treeview(top, columns=cols, show="headings", height=15)
        for c in cols: t.heading(c, text=c, command=lambda x=c: self._sort_tree("popup", t, x)); t.column(c, width=100 if c != "Descrizione" else 500)
        t.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        all_it = self.db.get_all_price_items()
        for r in all_it: t.insert("", tk.END, values=(r.code, r.description, f"{r.price:.2f}"))
        f = tk.Frame(top, bg=cfg.COLOR_BG_PANEL); f.pack(fill=tk.X, pady=15)
        tk.Label(f, text="Quantità:", bg=cfg.COLOR_BG_PANEL, fg="white").pack(side=tk.LEFT, padx=15)
        eq = tk.Entry(f, width=12, **cfg.get_entry_style()); eq.pack(side=tk.LEFT); eq.insert(0, "1.0")
        def confirm():
            s = t.selection()
            if not s: return
            code = t.item(s[0])['values'][0]
            it = next((x for x in all_it if x.code == code), None)
            if it:
                try:
                    q = float(eq.get())
                    if self.db.add_quote_item(QuoteLineItem(None, self.current_quote_id, it.code, it.description, q, it.price, it.price * q, it.unit)):
                        self._load_quote_detail(self.current_quote_id); self._load_quotes_list(); top.destroy()
                except: pass
        tk.Button(f, text="  AGGIUNGI  ", command=confirm, bg="#008800", fg="white", font=cfg.FONT_HEADER).pack(side=tk.RIGHT, padx=15)

    def _do_delete_quote_item(self):
        s = self.tree_items.selection()
        if s: self.db.delete_quote_item(int(self.tree_items.item(s[0])['values'][0]), self.current_quote_id); self._load_quote_detail(self.current_quote_id); self._load_quotes_list()

    def _export_quote(self) -> None:
        if not self.current_quote_id: return
        h, items = self.db.get_quote_details(self.current_quote_id)
        if not h: return
        ed = Path(__file__).parent / "exports"; ed.mkdir(exist_ok=True); fp = ed / f"Preventivo_{h.id}_{h.customer_name.replace(' ', '_')}.txt"
        l = ["="*85, f"PREVENTIVO N. {h.id:04d} | CLIENTE: {h.customer_name.upper()} | DATA: {h.date_created}", "="*85, ""]
        l.append(f"{'CODICE':<12} | {'DESCRIZIONE':<35} | {'UM':<4} | {'QTA':<7} | {'UNITARIO':<10} | {'TOTALE':<10}")
        l.append("-" * 95)
        for i in items: l.append(f"{i.item_code:<12} | {(i.description[:32]+'..') if len(i.description)>32 else i.description:<35} | {i.unit:<4} | {i.quantity:<7.2f} | {i.unit_price:<10.2f} | {i.total_price:<10.2f}")
        l.append("-" * 95); l.append(f"{'TOTALE COMPLESSIVO:':<80} € {h.total_amount:.2f}"); l.append("="*85)
        try:
            with open(fp, "w", encoding="utf-8") as f: f.write("\n".join(l))
            self._custom_confirm("Export", f"Creato: {fp.name}\nAprire cartella?", lambda: os.system(f"xdg-open {ed}"))
        except: pass


def do_main() -> None:
    db = DataManager(); root = tk.Tk()
    try: root.tk.call('tk', 'scaling', 1.3)
    except: pass
    app = PreventiviApp(root, db); root.mainloop()

if __name__ == "__main__": do_main()
