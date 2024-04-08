# -*- coding: utf-8 -*-
# © 2024 Binovo IT Human Project SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not version:
        return
    partners = env["res.partner"].search([("parent_id", "=", False)])
    for partner in partners:
        partner.write({"valued_picking": partner.valued_picking})
