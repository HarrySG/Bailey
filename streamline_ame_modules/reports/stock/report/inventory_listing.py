# -*- coding: utf-8 -*-

import time
from openerp.osv import osv
from openerp.report import report_sxw

class wrapped_streamline_ame_report_inventory_listing(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(wrapped_streamline_ame_report_inventory_listing, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_data_report':self._get_data_report,
        })

    def _get_data_report(self):
        self.cr.execute('''
        select pp.default_code, pt.description, pu.name uom, rp.name vendor, 
            case when sq.lot_id is NULL then NULL
            else (
                select DISTINCT to_char(tpo.date_order, 'dd/MM/yyyy')
                from stock_pack_operation tspo
                inner join stock_move tsm on tsm.picking_id = tspo.picking_id
                inner join purchase_order_line tpol on tsm.purchase_line_id = tpol.id
                inner join purchase_order tpo on tpol.order_id = tpo.id
                where tspo.lot_id is not null
                and tspo.lot_id = sq.lot_id
                and tsm.product_id = pp.id
            ) end date_order
        from stock_quant sq
        inner join product_product pp on sq.product_id = pp.id
        inner join product_template pt on pp.product_tmpl_id = pt.id
        inner join product_uom pu on pt.uom_id = pu.id
        inner join product_supplierinfo ps on ps.product_tmpl_id = pt.id
        inner join res_partner rp on ps.name = rp.id and rp.supplier = 't'
        inner join stock_picking_type spt on sq.location_id = spt.default_location_dest_id and spt.code = 'incoming'
        inner join stock_warehouse sw on spt.warehouse_id = sw.id
        where sw.company_id = 1
        and sw.partner_id = 1
        group by 1,2,3,4,5
        order by pp.default_code
        ''')
        res = self.cr.dictfetchall()
        return res

class report_streamline_ame_inventory_listing(osv.AbstractModel):
    _name = 'report.streamline_ame_modules.report_streamline_ame_inventory_listing'
    _inherit = 'report.abstract_report'
    _template = 'streamline_ame_modules.report_streamline_ame_inventory_listing'
    _wrapped_report_class = wrapped_streamline_ame_report_inventory_listing

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
