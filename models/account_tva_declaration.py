from odoo import models, fields, api
import calendar
from datetime import date

class AccountTvaDeclaration(models.Model):
    """
    Modèle représentant une déclaration de TVA historique (Tableau de Bord).
    Gère le calcul de la TVA due (Collectée - Déductible) pour les régimes
    d'encaissement et des débits, pour un mois ou trimestre donné.
    """
    _name = 'account.tva.declaration'
    _description = 'Déclaration de TVA (Tableau de Bord et Historique)'
    _order = 'periode_annee desc, date_start desc'

    name = fields.Char(string='Titre de la déclaration', compute='_compute_name', store=True)
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    
    tva_regime = fields.Selection(related='company_id.tva_regime', string="Régime")
    
    periode_annee = fields.Selection(
        [(str(y), str(y)) for y in range(2020, 2035)], 
        string='Année', required=True, 
        default=lambda self: str(fields.Date.context_today(self).year)
    )
    
    periode_mois = fields.Selection([
        ('01', 'Janvier'), ('02', 'Février'), ('03', 'Mars'), ('04', 'Avril'),
        ('05', 'Mai'), ('06', 'Juin'), ('07', 'Juillet'), ('08', 'Août'),
        ('09', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')
    ], string='Mois', default=lambda self: str(fields.Date.context_today(self).month).zfill(2))
    
    periode_trimestre = fields.Selection([
        ('1', '1er Trimestre (Jan-Fév-Mars)'),
        ('2', '2ème Trimestre (Avr-Mai-Juin)'),
        ('3', '3ème Trimestre (Juil-Août-Sept)'),
        ('4', '4ème Trimestre (Oct-Nov-Déc)'),
    ], string='Trimestre', default='1')
    
    date_start = fields.Date(string='Date de début', compute='_compute_dates', store=True)
    date_end = fields.Date(string='Date de fin', compute='_compute_dates', store=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('done', 'Validée')
    ], string='Statut', default='draft')

    # Synthèse financière
    tva_collectee = fields.Monetary(string='TVA Collectée (Ventes)', readonly=True)
    tva_deductible = fields.Monetary(string='TVA Déductible (Achats)', readonly=True)
    tva_a_payer = fields.Monetary(string='TVA à Payer', readonly=True)

    # Lignes de ventilation par taux
    line_ids = fields.One2many('account.tva.declaration.line', 'declaration_id', string='Ventilation des Montants')

    @api.depends('periode_annee', 'periode_mois', 'periode_trimestre', 'tva_regime')
    def _compute_dates(self):
        """
        Calcule les dates de début et de fin de la période de déclaration
        en fonction de l'année, du mois/trimestre sélectionnés, et du régime TVA.
        """
        for rec in self:
            if not rec.periode_annee:
                rec.date_start = False
                rec.date_end = False
                continue
                
            year = int(rec.periode_annee)
            
            if rec.tva_regime == 'mensuel' and rec.periode_mois:
                month = int(rec.periode_mois)
                rec.date_start = date(year, month, 1)
                last_day = calendar.monthrange(year, month)[1]
                rec.date_end = date(year, month, last_day)
                
            elif rec.tva_regime == 'trimestriel' and rec.periode_trimestre:
                trimestre = int(rec.periode_trimestre)
                start_month = (trimestre - 1) * 3 + 1
                end_month = start_month + 2
                rec.date_start = date(year, start_month, 1)
                last_day = calendar.monthrange(year, end_month)[1]
                rec.date_end = date(year, end_month, last_day)

    @api.depends('date_start', 'tva_regime', 'periode_annee', 'periode_mois', 'periode_trimestre')
    def _compute_name(self):
        """Génère le titre d'affichage automatique de la déclaration."""
        for rec in self:
            if rec.tva_regime == 'trimestriel' and rec.periode_trimestre and rec.periode_annee:
                rec.name = f"TVA T{rec.periode_trimestre} - {rec.periode_annee}"
            elif rec.tva_regime == 'mensuel' and rec.periode_mois and rec.periode_annee:
                rec.name = f"TVA {dict(self._fields['periode_mois'].selection).get(rec.periode_mois)} {rec.periode_annee}"
            else:
                rec.name = "Nouvelle Déclaration"

    def action_validate(self):
        """Valide la déclaration et la verrouille."""
        self.state = 'done'

    def action_draft(self):
        """Remet la déclaration à l'état brouillon pour modification."""
        self.state = 'draft'

    def action_compute_tva(self):
        """
        Algorithme de calcul basé STRICTEMENT sur l'encaissement (Cash Basis).
        On cherche les paiements effectués dans la période (partiels ou totaux) 
        et on déduit la part proportionnelle de TVA de la facture d'origine.
        """
        for rec in self:
            rec.line_ids.unlink()  # Nettoyer les anciens calculs
            
            total_collectee = 0.0
            total_deductible = 0.0
            ventilation = {} # { ('collectee'/'deductible', taux): montant_tva }

            # 1. Chercher tous les lettrages (paiements de factures) sur la période choisie
            domain = [
                ('max_date', '>=', rec.date_start),
                ('max_date', '<=', rec.date_end),
                ('company_id', '=', rec.company_id.id)
            ]
            partials = self.env['account.partial.reconcile'].search(domain)

            for partial in partials:
                # Retrouver la ligne de facture concernée par ce paiement
                move_lines = partial.debit_move_id | partial.credit_move_id
                invoice_line = move_lines.filtered(lambda l: l.move_id.is_invoice(include_receipts=True))
                
                if not invoice_line:
                    continue
                    
                invoice = invoice_line.move_id[0]
                
                # S'assurer que le montant total n'est pas zéro
                if invoice.amount_total == 0:
                    continue
                    
                # Calcul de la "proportion" payée (Ex: Paiement de 500 sur facture de 1000 = 50%)
                proportion = partial.amount / invoice.amount_total
                
                # 2. Appliquer la proportion aux lignes de taxes de cette facture
                tax_lines = invoice.line_ids.filtered(lambda l: l.tax_line_id)
                for t_line in tax_lines:
                    # Montant de la TVA proportionnel au paiement
                    tva_calculee = abs(t_line.balance) * proportion
                    taux = abs(t_line.tax_line_id.amount)
                    
                    if invoice.move_type in ['out_invoice', 'out_receipt', 'out_refund']:
                        type_tva = 'collectee'
                        total_collectee += tva_calculee
                    else:
                        type_tva = 'deductible'
                        total_deductible += tva_calculee
                        
                    key = (type_tva, taux)
                    ventilation[key] = ventilation.get(key, 0.0) + tva_calculee
                    
            # 3. Mettre à jour l'en-tête (Synthèse)
            rec.tva_collectee = total_collectee
            rec.tva_deductible = total_deductible
            rec.tva_a_payer = total_collectee - total_deductible

            # 4. Générer les lignes de ventilation (Tableau de bord détaillé)
            lines_to_create = []
            for (type_tva, taux), montant in ventilation.items():
                lines_to_create.append((0, 0, {
                    'type_tva': type_tva,
                    'taux': taux,
                    'montant_tva': montant
                }))
            rec.line_ids = lines_to_create


class AccountTvaDeclarationLine(models.Model):
    _name = 'account.tva.declaration.line'
    _description = 'Ligne de ventilation TVA'

    declaration_id = fields.Many2one('account.tva.declaration', ondelete='cascade')
    company_id = fields.Many2one(related='declaration_id.company_id')
    currency_id = fields.Many2one(related='declaration_id.currency_id')
    
    type_tva = fields.Selection([
        ('collectee', 'TVA Collectée (Ventes)'),
        ('deductible', 'TVA Déductible (Achats)')
    ], string='Type')
    
    taux = fields.Float(string='Taux appliqué (%)')
    montant_tva = fields.Monetary(string='Montant TVA')
