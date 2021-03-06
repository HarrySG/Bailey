select substring(X.complete_name from (length('Physical Locations / ') + strpos(X.complete_name, 'Physical Locations / '))) complete_name, 
	X.product_name, X.product_id, X.co_name, 
	sum(case when X.remain_date <= 30 then X.stock else 0 end) "1-30",
	sum(case when X.remain_date BETWEEN 30 and 60 then X.stock else 0 end) "31-60",
	sum(case when X.remain_date BETWEEN 61 and 90 then X.stock else 0 end) "61-90",
	sum(case when X.remain_date > 90 then X.stock else 0 end) ">90",
	sum(X.stock) total
from
((select sq.location_id,sl.complete_name, pp.name_template product_name, sq.product_id, sp.date_done::DATE, sum(sq.qty) stock, now()::DATE - sp.date_done::DATE as remain_date,
	(select sw.name
	from stock_picking_type spt
	inner join stock_warehouse sw on spt.warehouse_id = sw.id
	where spt.default_location_dest_id = sq.location_id
	and spt.code = 'incoming') co_name
from stock_quant sq
inner join product_product pp on sq.product_id = pp.id
inner join stock_location sl on sq.location_id = sl.id
inner join stock_pack_operation spo on sq.lot_id = spo.lot_id and sq.location_id = spo.location_dest_id
inner join stock_picking sp on spo.picking_id = sp.id
where sl.usage in ('internal')
and (sl.complete_name like '%Physical%Stock%'
or sl.complete_name like '%Partner%')
group by 1,2,3,4,5
order by 1,3)
union
(select sq.location_id,sl.complete_name, pp.name_template product_name, sq.product_id, '2015-01-01'::DATE date_done, sum(sq.qty) stock, 99 as remain_date,
	(select sw.name
	from stock_picking_type spt
	inner join stock_warehouse sw on spt.warehouse_id = sw.id
	where spt.default_location_dest_id = sq.location_id
	and spt.code = 'incoming') co_name
from stock_quant sq
inner join product_product pp on sq.product_id = pp.id
inner join stock_location sl on sq.location_id = sl.id
where sl.usage in ('internal')
and (sl.complete_name like '%Physical%Stock%'
or sl.complete_name like '%Partner%')
and sq.lot_id is null
group by 1,2,3,4,5
order by 1,3)
)X
group by 1,2,3,4
order by 1,3