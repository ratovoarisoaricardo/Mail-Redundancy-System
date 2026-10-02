#!/bin/bash
# ==============================================================================
# Script de surveillance (Healthcheck) pour Keepalived
# Projet   : Mail Redundancy System (Haute Disponibilité)
# Auteur   : RATOVOARISOA Mendrika Manjaka Ricardo
# Licence  : MIT License
# Copyright (c) RATOVOARISOA Mendrika Manjaka Ricardo - Tous droits réservés
# ==============================================================================

# 1. Vérification du service Postfix (MTA - SMTP)
if ! systemctl is-active --quiet postfix; then
    echo "[CRITICAL] Postfix est inactif ou en échec" >&2
    exit 1
fi

# 2. Vérification du service Dovecot (MDA - IMAP/POP3)
if ! systemctl is-active --quiet dovecot; then
    echo "[CRITICAL] Dovecot est inactif ou en échec" >&2
    exit 1
fi

# 3. Vérification du service MariaDB (Base de données des comptes virtuels)
if ! systemctl is-active --quiet mariadb; then
    echo "[CRITICAL] MariaDB est inactif ou en échec" >&2
    exit 1
fi

# Tous les services critiques sont opérationnels
exit 0
