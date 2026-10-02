# 🔄 Synchronisation du Stockage Mails & Réplication Base de Données

> Ce document analyse les mécanismes officiels de réplication pour le stockage de courriels (`Maildir`) et les bases relationnelles, en s'appuyant sur les documentations officielles de Dovecot et MariaDB.

---

## 1. Synchronisation des Boîtes aux Lettres : Dovecot `dsync` vs `rsync`

### 1.1 Pourquoi `rsync` n'est pas recommandé pour la haute disponibilité mail
Bien que `rsync` soit un outil efficace pour la sauvegarde unilatérale de fichiers froids, son utilisation pour synchroniser des boîtes aux lettres en production présente des risques critiques :
1. **Risque de Split-Brain / Perte de données avec `--delete` :** Si un e-mail est reçu par le nœud secondaire pendant une panne temporaire, le prochain passage de `rsync --delete` depuis le nœud principal supprime définitivement cet e-mail.
2. **Corruption d'index :** Dovecot maintient des fichiers d'index binaires (`dovecot.index*`, `dovecot-uidlist`) et des fichiers de verrous. `rsync` copie les fichiers bloc par bloc sans comprendre l'état transactionnel d'un client IMAP connecté, provoquant des corruptions d'index.

### 1.2 La solution officielle : Dovecot `dsync` (Doveadm Synchronization)
Selon la [documentation officielle de Dovecot](https://doc.dovecot.org/):
* **Compréhension native du format Maildir :** `dsync` utilise les GUIDs des messages, les journaux de transactions Dovecot et les drapeaux IMAP (*read, flagged, answered*).
* **Synchronisation bidirectionnelle (Two-way sync) :** Les modifications opérées sur l'un ou l'autre des nœuds sont fusionnées sans perte de courriels.
* **Résolution de conflits :** Si un e-mail est déplacé d'un dossier à un autre sur un nœud alors qu'il est lu sur le second, `dsync` réconcilie l'état final conformément à la RFC 3501.

### 1.3 Configuration officielle du Replicator (`/etc/dovecot/conf.d/90-replication.conf`)
```nginx
# Activation des modules de notification et réplication
mail_plugins = $mail_plugins notify replication

service replicator {
  process_min_avail = 1
  unix_listener replicator-doveadm {
    mode = 0600
    user = vmail
  }
}

service doveadm {
  inet_listener {
    port = 12345
    ssl = yes
  }
}

doveadm_password = SECURE_DSYNC_SECRET_TOKEN
doveadm_port = 12345

plugin {
  # Pointer vers l'adresse IP interne de l'autre nœud
  mail_replica = tcp:192.168.1.11:12345
}
```

---

## 2. Réplication de la Base de Données MariaDB

Les comptes utilisateurs, mots de passe de messagerie, quotas et alias virtuels sont stockés dans MariaDB et consultés par Postfix et Dovecot.

### 2.1 Mode Dual-Master (Maître-Maître)
Pour permettre aux deux nœuds d'effectuer des écritures (ex: mise à jour des dates de dernière connexion ou modifications administrateur) :

```ini
# /etc/mysql/mariadb.conf.d/50-server.cnf (sur mail1)
[mysqld]
server-id               = 1
log_bin                 = /var/log/mysql/mariadb-bin
binlog_format           = ROW
auto_increment_increment = 2
auto_increment_offset    = 1
bind-address            = 0.0.0.0
```

Sur `mail2`, on configure `server-id = 2` et `auto_increment_offset = 2`.  
Cette séparation garantit qu'aucune clé primaire auto-incrémentée n'entrera en collision entre les deux nœuds.

---

## 3. Références Officielles & Sources Communautaires
* **Dovecot Official Documentation :** [doc.dovecot.org](https://doc.dovecot.org/)
* **Dovecot dsync Architecture & Replication :** [doc.dovecot.org/admin_manual/doveadm/doveadm-sync/](https://doc.dovecot.org/admin_manual/doveadm/doveadm-sync/)
* **MariaDB Standard Replication Knowledge Base :** [mariadb.com/kb/en/standard-replication/](https://mariadb.com/kb/en/standard-replication/)
* **MariaDB Galera Cluster Documentation :** [mariadb.com/kb/en/galera-cluster/](https://mariadb.com/kb/en/galera-cluster/)
