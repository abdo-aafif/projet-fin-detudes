from odoo import models, fields

class ResCompany(models.Model):
    """
    Surcharge de la société pour y rajouter les paramètres comptables et fiscaux marocains.
    Ex: Le régime de la périodicité de déclaration de la TVA.
    """
    _inherit = 'res.company'
    
    tva_regime = fields.Selection([
        ('mensuel', 'Mensuel'),
        ('trimestriel', 'Trimestriel')
    ], string="Périodicité de TVA", default='mensuel')

class ResConfigSettings(models.TransientModel):
    """
    Surcharge des paramètres de configurations (Settings) pour exposer
    la configuration de la périodicité de déclaration TVA aux administrateurs.
    """
    _inherit = 'res.config.settings'
    
    tva_regime = fields.Selection(related='company_id.tva_regime', readonly=False, string="Périodicité de déclaration TVA")