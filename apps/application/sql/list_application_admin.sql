SELECT *,to_json(dataset_setting) as dataset_setting,to_json(model_setting) as model_setting,to_json(work_flow) as work_flow FROM ( SELECT * FROM application  ${application_custom_sql} UNION
	SELECT
		*
	FROM
		application
	) temp_application ${default_sql}