{
    'name': 'GEMINIIII',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Plan comptable PCGE marocain, écritures comptables, lettrage, contre-passation, écritures récurrentes',
    'description': """
Module de comptabilité pour Odoo 17 Community - Maroc
=====================================================
Fonctionnalités :
- Plan Comptable PCGE marocain par défaut
- Import/Export du plan comptable (CSV, Excel)
- Gestion multi-sociétés
- Comptes analytiques
- Saisie manuelle des écritures comptables
- Écritures automatiques depuis factures clients/fournisseurs
- Lettrage des comptes (réconciliation)
- Contre-passation d'écritures
- Écritures récurrentes (abonnements, loyers)
    """,
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'analytic',     # Module natif Odoo pour les centres de coûts et l'analytique
        'account',      # Moteur comptable de base Odoo Community
        'l10n_ma',      # Plan Comptable Général Marocain officiel Odoo
        'base_setup',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/compta_security.xml',
        #'data/journal_data.xml',
        'wizard/simpl_tva_wizard_views.xml',
        'views/compta_overrides.xml',
        'views/account_tva_declaration_views.xml',
        'views/account_recurring_views.xml',
        # Ajouter ici les futures vues et rapports spécifiques marocains

        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
