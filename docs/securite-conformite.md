# 🔒 Sécurité, Chiffrement TLS et Standards IETF de Messagerie

> Ce document résume les exigences de sécurité et de conformité aux standards officiels (RFC) régissant les flux de messagerie et l'authentification.

---

## 1. Normes de Chiffrement et Ports : RFC 8314

La [RFC 8314](https://datatracker.ietf.org/doc/html/rfc8314) (*Cleartext Considered Obsolete: Use of Transport Layer Security for Email Submission and Access*) stipule que l'utilisation de protocoles en texte clair non chiffré est obsolète pour l'envoi et la consultation des e-mails.

| Protocole | Port Officiel | Type de Sécurité | Recommandation RFC 8314 |
| :--- | :---: | :--- | :--- |
| **SMTP Submission** | `587` | STARTTLS obligatoire | Standard pour la soumission par les clients de messagerie |
| **SMTPS** | `465` | TLS implicite direct | Recommandé par la RFC 8314 pour une sécurité immédiate |
| **IMAPS** | `993` | TLS implicite direct | Consultation sécurisée des boîtes aux lettres |
| **SMTP Relais (MTA-MTA)** | `25` | STARTTLS opportuniste | Échange chiffré entre serveurs de messagerie sur Internet |

---

## 2. Configuration Sécurisée Postfix (TLS_README)

Selon la [documentation officielle Postfix TLS_README](https://www.postfix.org/TLS_README.html), les paramètres recommandés dans `/etc/postfix/main.cf` sont :

```ini
# Chiffrement TLS pour la réception et l'émission
smtpd_tls_security_level = may
smtp_tls_security_level = dane
smtpd_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1

# Certificats SSL (Let's Encrypt ou autorité interne reconnue)
smtpd_tls_cert_file = /etc/ssl/certs/mail.domaine.local.crt
smtpd_tls_key_file  = /etc/ssl/private/mail.domaine.local.key
```

---

## 3. Authentification et Délivrabilité (SPF, DKIM, DMARC)

Pour garantir la réputation du domaine, prévenir l'usurpation d'identité (*spoofing*) et le hameçonnage (*phishing*) :

1. **SPF - Sender Policy Framework ([RFC 7208](https://datatracker.ietf.org/doc/html/rfc7208)) :**  
   Déclaration DNS spécifiant l'adresse IP flottante autorisée à émettre des e-mails pour le domaine :
   ```dns
   v=spf1 ip4:192.168.1.100 -all
   ```
2. **DKIM - DomainKeys Identified Mail ([RFC 6376](https://datatracker.ietf.org/doc/html/rfc6376)) :**  
   Signature cryptographique asymétrique insérée dans les en-têtes de chaque message sortant par OpenDKIM/Rspamd.
3. **DMARC - Message Authentication, Reporting & Conformance ([RFC 7489](https://datatracker.ietf.org/doc/html/rfc7489)) :**  
   Politique de sécurité instruisant les serveurs destinataires sur la conduite à tenir en cas d'échec SPF/DKIM :
   ```dns
   v=DMARC1; p=reject; rua=mailto:dmarc-reports@domaine.local; pct=100
   ```

---

## 4. Références Officielles IETF
* **RFC 5321 :** [Simple Mail Transfer Protocol (SMTP)](https://datatracker.ietf.org/doc/html/rfc5321)
* **RFC 3501 :** [Internet Message Access Protocol - Version 4rev1](https://datatracker.ietf.org/doc/html/rfc3501)
* **RFC 8314 :** [Use of Transport Layer Security (TLS) for Email Submission and Access](https://datatracker.ietf.org/doc/html/rfc8314)
* **RFC 7208 :** [Sender Policy Framework (SPF)](https://datatracker.ietf.org/doc/html/rfc7208)
* **RFC 6376 :** [DomainKeys Identified Mail (DKIM) Signatures](https://datatracker.ietf.org/doc/html/rfc6376)
* **RFC 7489 :** [Domain-based Message Authentication, Reporting, and Conformance (DMARC)](https://datatracker.ietf.org/doc/html/rfc7489)
* **Postfix Official Documentation :** [postfix.org/TLS_README.html](https://www.postfix.org/TLS_README.html)
