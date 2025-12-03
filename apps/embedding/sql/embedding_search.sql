SELECT
    DISTINCT_TEMP.paragraph_id,
    DISTINCT_TEMP.chunk_id,
    DISTINCT_TEMP.comprehensive_score,
    DISTINCT_TEMP.comprehensive_score as similarity,
    c.content as chunk_data,
    c.chunk_index,
    c.char_length
FROM
    (
    SELECT DISTINCT ON
        ("paragraph_id") ( similarity ),* ,similarity AS comprehensive_score
    FROM
        ( SELECT *, ( 1 - ( embedding.embedding <=>  %s ) ) AS similarity FROM embedding ${embedding_query}) TEMP
    ORDER BY
        paragraph_id,
        similarity DESC
    ) DISTINCT_TEMP
LEFT JOIN chunk c ON c.id = DISTINCT_TEMP.chunk_id
WHERE DISTINCT_TEMP.comprehensive_score>%s
ORDER BY DISTINCT_TEMP.comprehensive_score DESC
LIMIT %s