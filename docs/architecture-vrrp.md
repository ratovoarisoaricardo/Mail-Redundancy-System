# 📡 Architecture Haute Disponibilité avec Keepalived (VRRP)

> Ce document détaille les fondements théoriques, protocolaires et de configuration pour la haute disponibilité par adresse IP flottante (VIP), conformément aux standards officiels de l'IETF et à la documentation de Keepalived.

---

## 1. Fondements Protocolaires : RFC 5798 (VRRPv3)

Le **Virtual Router Redundancy Protocol (VRRP)**, normalisé dans la [RFC 5798](https://datatracker.ietf.org/doc/html/rfc5798), est un protocole de couche réseau conçu pour éliminer le point unique de défaillance (*Single Point of Failure - SPoF*) sur les passerelles et services IP.

### Mécanismes clés :
1. **Élection du Master :**  
   Les nœuds s'échangent des paquets d'annonce VRRP (*advertisements*) par multicast (`224.0.0.18` en IPv4). Le nœud ayant la priorité la plus élevée (ici `mail1` avec priorité 100) s'attribue l'adresse IP virtuelle (`192.168.1.100`).
2. **Heartbeat et Détection de Panne :**  
   L'intervalle d'annonce est configuré à `1 seconde` (`advert_int 1`). Si le nœud `BACKUP` (`mail2`) ne reçoit pas d'annonce pendant `3 * advert_int + Skew_Time` (environ 3,6 secondes), il déclare le Master défaillant et prend le relais.
3. **Gratuitous ARP :**  
   Dès l'élévation au statut `MASTER`, Keepalived émet des trames **Gratuitous ARP (GARP)** sur le réseau local. Tous les commutateurs (switches) et équipements clients mettent immédiatement à jour leur table ARP pour associer l'adresse `192.168.1.100` à l'adresse MAC physique de la nouvelle interface active.

---

## 2. Configuration Avancée Keepalived

D'après la documentation officielle [`keepalived.conf(5)`](https://www.keepalived.org/manpage.html), plusieurs directives critiques garantissent la résilience et préviennent les comportements indésirables :

### 2.1 Directive `nopreempt` (Anti-Flapping)
```text
nopreempt
state BACKUP
```
* **Principe :** Par défaut, en mode préemptif, dès que `mail1` redémarre et retrouve sa priorité 100, il reprend de force la VIP à `mail2`. Si le service de `mail1` oscille (crash en boucle), cela provoque des bascules répétées (*flapping*) désastreuses pour les connexions TCP.
* **Bonne pratique officielle :** Configurer les deux serveurs en `state BACKUP` avec `nopreempt`. Le serveur secondaire conserve la VIP jusqu'à ce qu'un administrateur valide le retour ou qu'un nouvel incident survienne.

### 2.2 Script de Tracking et Gestion du Poids (`weight`)
```text
vrrp_script chk_mail_services {
    script "/usr/local/bin/check_mail_health.sh"
    interval 2
    weight -20
    fall 2
    rise 2
    timeout 5
}
```
* **`weight -20` :** Si le script échoue (code de sortie != 0), la priorité de `mail1` chute de 100 à 80. Comme `mail2` a une priorité de 90, `mail2` devient prioritaire sans coupure violente.
* **`fall 2` / `rise 2` :** Exige deux échecs consécutifs pour déclencher la dégradation (évite les faux positifs), et deux succès consécutifs pour valider la réparation.

### 2.3 Liaison IP Non-Locale (`ip_nonlocal_bind`)
Sur Debian, pour permettre à Postfix et Dovecot de démarrer et d'écouter sur la VIP même lorsqu'elle n'est pas encore assignée localement :
```ini
# /etc/sysctl.d/99-keepalived.conf
net.ipv4.ip_nonlocal_bind = 1
```
Appliqué via `sysctl --system`.

---

## 3. Références Officielles
* **IETF RFC 5798 :** [Virtual Router Redundancy Protocol (VRRP) Version 3](https://datatracker.ietf.org/doc/html/rfc5798)
* **Keepalived Official Website & Manpages :** [keepalived.org](https://www.keepalived.org/)
* **Debian Wiki - Keepalived :** [wiki.debian.org/Keepalived](https://wiki.debian.org/Keepalived)
