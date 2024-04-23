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
        child_ids = env["res.partner"].search([('parent_id', 'child_of', partner.id)]).ids
        if len(child_ids) > 1:
            openupgrade.logged_query(
                env.cr,
                """
                UPDATE res_partner SET valued_picking = %s WHERE id in %s
                """,
                (partner.valued_picking, tuple(child_ids)),
            )
