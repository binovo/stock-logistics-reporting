# Copyright 2014-2018 Tecnativa - Pedro M. Baeza
# Copyright 2015 Antonio Espinosa - Tecnativa <antonio.espinosa@tecnativa.com>
# Copyright 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# Copyright 2016 Luis M. Ontalba - Tecnativa <luis.martinez@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    valued = fields.Boolean(
        related='partner_id.valued_picking', readonly=True,
    )
    currency_id = fields.Many2one(
        related='sale_id.currency_id', readonly=True,
        string='Currency',
        related_sudo=True,  # See explanation for sudo in compute method
    )
    amount_untaxed = fields.Monetary(
        compute='_compute_amount_all',
        string='Untaxed Amount',
        compute_sudo=True,  # See explanation for sudo in compute method
    )
    amount_tax = fields.Monetary(
        compute='_compute_amount_all',
        string='Taxes',
        compute_sudo=True,
    )
    amount_total = fields.Monetary(
        compute='_compute_amount_all',
        string='Total',
        compute_sudo=True,
    )

    @api.multi
    def _compute_amount_all(self):
        """This is computed with sudo for avoiding problems if you don't have
        access to sales orders (stricter warehouse users, inter-company
        records...).
        """
        for pick in self:
            round_curr = pick.sale_id.currency_id.round
            amount_tax = 0.0
            # In v12 the support for compute_sudo on non stored fields is
            # limited (officially unsupported) so we have to mainaint some
            # some sudo() calls. This is not necessary from v13
            # https://github.com/odoo/odoo/blob/12.0/odoo/fields.py#L179
            for tax_id, tax_group in pick.sudo().get_taxes_values().items():
                amount_tax += round_curr(tax_group['amount'])
            amount_untaxed = sum(
                l.sale_price_subtotal for l in pick.move_line_ids)
            pick.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    def get_taxes_values(self):
        self.ensure_one()
        tax_grouped = {}
        for line in self.move_line_ids:
            tax_key = '-'.join(sorted(map(str, line.sale_line.tax_id.ids)))
            tax_amount = 0
            tax_list = line.sale_line.tax_id.mapped('amount')
            for tax in tax_list:
                tax_amount += line.sale_price_subtotal * (tax / 100)
            if tax_key not in tax_grouped:
                tax_grouped[tax_key] = {
                    "base": line.sale_price_total,
                    "tax": line.sale_line.tax_id.mapped('amount'),
                    "tax_name": ', '.join(line.sale_line.tax_id.mapped('name')),
                    "amount": tax_amount,
                }
            else:
                tax_grouped[tax_key]["base"] += line.sale_price_total
                tax_grouped[tax_key]["amount"] += tax_amount

        return tax_grouped
