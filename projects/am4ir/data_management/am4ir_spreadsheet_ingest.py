'''
(1) Read excel am4ir spreadsheet from elsevier
(2) and modify local mysql table article_item
by inserting embargo_end_date, set flag is_am4ir to true, and update the update_dt value
or maybe have a separate update_am4ir_dt value (and add one for update_els_oa_dt,
and add column update_oadoi_open_access_dt value)
(3) and optionally (or make another program later to..) also use elevier entitlement
api based on the article_item.publisher_item_id (pii) value to:
  (a) update open_acccess info from elsevier, (b) the doi,
  (c) scopus id, (d) eid
(4) use the doi value to use the oaidoi API update the
oaidoi.org open access value.. oai_doi_open_access
'''
