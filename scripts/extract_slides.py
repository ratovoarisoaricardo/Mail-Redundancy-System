#!/usr/bin/env python3
"""
Script d'extraction des diapositives pertinentes du mémoire
pour le dépôt GitHub de messagerie redondante (Caisse d'Épargne de Madagascar).
"""

import os
import sys

def extract_with_pymupdf(pdf_path, output_dir):
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("[!] PyMuPDF non installé. Installez-le avec : pip install pymupdf")
        return False

    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)

    # Correspondance entre numéro de page (1-indexé) et nom de fichier cible
    slides_mapping = {
        1: "slide-01-titre.png",
        6: "slide-06-historique-institut.png",
        8: "slide-08-historique-cem.png",
        9: "slide-09-organigramme.png",
        11: "slide-11-methode.png",
        12: "slide-12-outils1.png",
        13: "slide-13-outils2.png",
        15: "slide-15-limites.png",
        16: "slide-16-perspectives.png",
    }

    print(f"[*] Traitement du fichier : {pdf_path}")
    for page_num, filename in slides_mapping.items():
        if page_num <= len(doc):
            page = doc[page_num - 1]
            pix = page.get_pixmap(dpi=200) # Haute résolution 200 DPI
            target_path = os.path.join(output_dir, filename)
            pix.save(target_path)
            print(f"[+] Page {page_num:02d} extraite vers : {target_path}")
        else:
            print(f"[-] Page {page_num} introuvable (total pages : {len(doc)})")

    print("[✓] Extraction terminée avec succès !")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_slides.py <chemin_vers_votre_fichier.pdf>")
        sys.exit(1)

    pdf_file = sys.argv[1]
    output_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "images")
    extract_with_pymupdf(pdf_file, output_directory)
