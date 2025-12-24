# 🏥 Système Intelligent d’Orientation et de Prise de Rendez-vous
### Clinique intelligente – Projet de stage d’application (ENSA Agadir)

## 📌 Description
Ce projet consiste en la conception et le développement d’une **plateforme intelligente**
permettant d’automatiser l’orientation des patients et la gestion des rendez-vous médicaux
au sein d’une clinique.

La solution vise à remplacer la gestion manuelle des rendez-vous par un système
numérique intelligent intégrant l’automatisation des workflows et un assistant IA
(chatbot) pour améliorer l’expérience utilisateur et optimiser l’organisation interne
de la clinique :contentReference[oaicite:2]{index=2}.

---

## 🎯 Objectifs du projet
- Automatiser la prise et l’annulation des rendez-vous médicaux
- Orienter intelligemment les patients vers le service ou le médecin adapté
- Centraliser la gestion des données patients et rendez-vous
- Réduire les erreurs de planification et les délais de traitement
- Intégrer un assistant IA pour faciliter la navigation et réduire le nombre de clics :contentReference[oaicite:3]{index=3}

---

## 👥 Profils utilisateurs
- **Patient** : prise et gestion des rendez-vous, consultation de l’historique
- **Médecin** : gestion des disponibilités et suivi des patients
- **Administrateur / Staff** : gestion des comptes, statistiques et supervision
- **Assistant IA (Chatbot)** : orientation intelligente et FAQ :contentReference[oaicite:4]{index=4}

---

## ⚙️ Architecture générale
L’architecture repose sur trois couches principales :contentReference[oaicite:5]{index=5} :

- **Frontend** : Flask (Python) + HTML / CSS
- **Backend & automatisation** : n8n (workflows automatisés)
- **Stockage des données** : Google Sheets
- **IA** : Google Gemini (LLM) pour l’orientation intelligente


