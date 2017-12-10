'''
(1) Read excel am4ir spreadsheet from elsevier
(2) and modify local mysql table article_item
by  selecting row based on pii value and based on existence either insert or
update a row, with the column values:
 (a) embargo_end_date,
 (b) set flag is_am4ir to true,
 (c) update_dt value (this column update should be automatic in the db, though)

(3) and also use elevier entitlement for each row (depending on a runtime flag)
     and from that, update values of: api based on the article_item.publisher_item_id (pii) value to:
  (a) doi,  eid, scopus_id, is_publisher_open_access

NOTE: make separate program later to get oaidoi open access info
(4) use the doi value to use the oaidoi API update the
oaidoi.org open access value.. oai_doi_open_access
'''
#
