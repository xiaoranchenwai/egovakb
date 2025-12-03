SELECT
	app_or_dataset.*
FROM
	(
	SELECT
		"id",
		"name",
		'DATASET' AS "type",
		user_id
	FROM
		dataset
	UNION
	SELECT
		"id",
		"name",
		'APPLICATION' AS "type",
		user_id
	FROM
		application
	) app_or_dataset