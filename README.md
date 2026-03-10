# Odoo 17 Community - Comptabilité Marocaine

Ce module étend les fonctionnalités natives d'Odoo 17 Community pour répondre aux exigences de la comptabilité générale marocaine (PCGE), en facilitant la saisie des écritures, la gestion de la TVA et les déclarations fiscales.

##  Fonctionnalités Principales

### 1. Plan Comptable et Configuration
* Configuration et personnalisation du plan comptable (PCGE marocain par défaut).
* Import/export du plan comptable.
* Gestion multi-sociétés et comptabilité analytique.

### 2. Écritures Comptables
* Saisie manuelle facilitée des écritures (Opérations Diverses, À-Nouveaux).
* Écritures automatiques depuis les factures.
* Lettrage des comptes et réconciliation.
* **Écritures récurrentes (Abonnements, Loyers)** : Module de gestion des écritures périodiques, comblant le manque de cette fonctionnalité dans la version Community.

### 3. Journaux Comptables
* Structuration par défaut selon les normes marocaines (Ventes, Achats, Banques, OD...).

### 4. Déclarations Fiscales & TVA
* Gestion automatique des taux de TVA marocains (20%, 14%, 10%, 7%).
* Assistant complet d'analyse historique et de calcul de la TVA (Encaissements).
* **Export pour télédéclaration SIMPL-TVA (DGI)** : Génération automatique du fichier XML prêt à être téléversé sur le portail de la Direction Générale des Impôts (DGI).

##  Installation

1. Clonez ce dépôt ou décompressez l'archive dans le répertoire des addons de votre instance Odoo 17.
2. Assurez-vous d'avoir installé les dépendances natives suivantes (gérées automatiquement lors de l'installation de ce module) :
   * `l10n_ma` (Localisation Maroc - Vient avec le Plan Comptable)
   Si votre plan comptable n'est pas marocain, vous pouvez le modifier dans le fichier `__manifest__.py`.  
   Par exemple, vous pouvez utiliser un plan comptable français (`l10n_fr`).
3. Redémarrez le service Odoo.
4. Connectez-vous en tant qu'administrateur, activez le **Mode Développeur**.
5. Allez dans *Applications* > *Mise à jour de la liste des applications*.
6. Recherchez "Comptabilité OMEGASOFT" et cliquez sur **Activer**.

##  Utilisation

* **Menu Comptabilité** : Un menu principal "Comptabilité" est ajouté au menu racine d'Odoo. Ce menu centralise l'accès aux écritures manuelles, récurrentes, et lettrage.
* **Écritures Récurrentes** : Accessibles via `Comptabilité > Écritures Récurrentes`. Permet de générer des écritures de loyers ou d'abonnements à des intervalles réguliers.
* **TVA & SIMPL-TVA** : Accessibles via `Comptabilité > Déclarations Fiscales`. Un tableau de bord permet d'analyser les montants collectés/déductibles et un assistant `"Export XML"` permet de générer le fichier de télédéclaration.

##  Licence

Ce module est distribué sous la licence [LGPL-3](https://www.gnu.org/licenses/lgpl-3.0.html).