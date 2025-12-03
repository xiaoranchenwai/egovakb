SELECT
    (SELECT "name" FROM "document" WHERE "id"=document_id) as document_name,
    (SELECT "document_url" FROM "document" WHERE "id"=document_id) as document_url,
	(SELECT "name" FROM "dataset" WHERE "id"=dataset_id) as dataset_name,
	*
FROM
	"paragraph"
