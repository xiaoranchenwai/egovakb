# coding=utf-8
"""
    @project: maxkb
    @file： statistics_serializers.py
    @date：2024/10/30
    @desc: 用户统计序列化器
"""
from django.db import connection
from rest_framework import serializers

from common.util.field_message import ErrMessage
from django.utils.translation import gettext_lazy as _


class StatisticsSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        start_time = serializers.DateTimeField(
            format='%Y-%m-%d %H:%M:%S', 
            error_messages=ErrMessage.date(_("Start time"))
        )
        end_time = serializers.DateTimeField(
            format='%Y-%m-%d %H:%M:%S', 
            error_messages=ErrMessage.date(_("End time"))
        )
        username = serializers.CharField(
            required=False, 
            error_messages=ErrMessage.char(_('用户名'))
        )
        dimension = serializers.CharField(
            required=False, 
            default='user',
            error_messages=ErrMessage.char(_('统计维度'))
        )
        current_page = serializers.IntegerField(
            required=False, 
            default=1,
            error_messages=ErrMessage.integer(_('当前页'))
        )
        page_size = serializers.IntegerField(
            required=False, 
            default=10,
            error_messages=ErrMessage.integer(_('每页大小'))
        )

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            
            start_time = self.data.get('start_time')
            end_time = self.data.get('end_time')
            username = self.data.get('username')
            dimension = self.data.get('dimension', 'user')
            current_page = self.data.get('current_page', 1)
            page_size = self.data.get('page_size', 10)
            
            if dimension == 'user':
                return self._get_user_statistics(start_time, end_time, username, current_page, page_size)
            else:
                return self._get_group_statistics(start_time, end_time, username, current_page, page_size)

        def _get_user_statistics(self, start_time, end_time, username, current_page, page_size):
            """获取用户维度统计"""
            # 构建SQL查询
            sql = """
            WITH user_stats AS (
              SELECT 
                u.id,
                u.username,
                u.nick_name,
                COUNT(DISTINCT CASE WHEN a.create_time < COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') 
                                    AND a.create_time > COALESCE(%s, '1970-01-01'::timestamp) THEN a.id END) as app_created_count,
                COUNT(DISTINCT CASE WHEN a.update_time < COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') 
                                    AND a.update_time > COALESCE(%s, '1970-01-01'::timestamp) 
                                    AND date_trunc('second', a.update_time) != date_trunc('second', a.create_time) 
                                    THEN a.id END) as app_updated_count,
                COUNT(DISTINCT CASE WHEN d.create_time < COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') 
                                    AND d.create_time > COALESCE(%s, '1970-01-01'::timestamp) THEN d.id END) as dataset_created_count,
                COUNT(DISTINCT CASE WHEN d.update_time < COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') 
                                    AND d.update_time > COALESCE(%s, '1970-01-01'::timestamp)
                                    AND date_trunc('second', d.update_time) != date_trunc('second', d.create_time)
                                    THEN d.id END) as dataset_updated_count,
                COUNT(DISTINCT CASE WHEN doc.create_time < COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') 
                                    AND doc.create_time > COALESCE(%s, '1970-01-01'::timestamp) THEN doc.id END) as document_created_count,
                COUNT(DISTINCT CASE WHEN doc.update_time < COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') 
                                    AND doc.update_time > COALESCE(%s, '1970-01-01'::timestamp)
                                    AND date_trunc('second', doc.update_time) != date_trunc('second', doc.create_time)
                                    THEN doc.id END) as document_updated_count
              FROM "public"."user" u
              LEFT JOIN "public"."application" a ON u.id = a.user_id
              LEFT JOIN "public"."dataset" d ON u.id = d.user_id
              LEFT JOIN "public"."document" doc ON d.id = doc.dataset_id
              WHERE (%s IS NULL OR u.username ILIKE %s)
              GROUP BY u.id, u.username, u.nick_name
            )
            SELECT 
              id,
              username,
              nick_name,
              app_created_count,
              app_updated_count,
              dataset_created_count,
              dataset_updated_count,
              document_created_count,
              document_updated_count
            FROM user_stats
            ORDER BY username
            LIMIT %s OFFSET %s;
            """
            
            # 准备参数
            params = [
                end_time, start_time,  # app create
                end_time, start_time,  # app update
                end_time, start_time,  # dataset create
                end_time, start_time,  # dataset update 
                end_time, start_time,  # doc create
                end_time, start_time,  # doc update
                username, f'%{username}%' if username else '%',
                page_size, (current_page - 1) * page_size
            ]
            
            # 执行查询
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # 获取总数
            count_sql = """
            WITH user_stats AS (
              SELECT 
                u.id
              FROM "public"."user" u
              LEFT JOIN "public"."application" a ON u.id = a.user_id
              LEFT JOIN "public"."dataset" d ON u.id = d.user_id
              LEFT JOIN "public"."document" doc ON d.id = doc.dataset_id
              WHERE (%s IS NULL OR u.username ILIKE %s)
              GROUP BY u.id, u.username, u.nick_name
            )
            SELECT COUNT(*) as total FROM user_stats;
            """
            
            with connection.cursor() as cursor:
                cursor.execute(count_sql, [username, f'%{username}%' if username else '%'])
                total = cursor.fetchone()[0]
            
            return {
                'total': total,
                'records': results,
                'current': current_page,
                'size': page_size
            }

        def _get_group_statistics(self, start_time, end_time, username, current_page, page_size):
            """获取分组维度统计"""
            # 构建SQL查询
            sql = """
            WITH group_stats AS (
              SELECT 
                g.id,
                g.name as group_name,
                COUNT(DISTINCT gm.user_id) as member_count,
                COUNT(DISTINCT CASE WHEN a.create_time < COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') 
                                    AND a.create_time > COALESCE(%s, '1970-01-01'::timestamp) 
                                    AND gm.user_id = a.user_id THEN a.id END) as app_created_count,
                COUNT(DISTINCT CASE WHEN a.update_time < COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') 
                                    AND a.update_time > COALESCE(%s, '1970-01-01'::timestamp) 
                                    AND date_trunc('second', a.update_time) != date_trunc('second', a.create_time) 
                                    AND gm.user_id = a.user_id THEN a.id END) as app_updated_count,
                COUNT(DISTINCT CASE WHEN d.create_time < COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') 
                                    AND d.create_time > COALESCE(%s, '1970-01-01'::timestamp) 
                                    AND gm.user_id = d.user_id THEN d.id END) as dataset_created_count,
                COUNT(DISTINCT CASE WHEN d.update_time < COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') 
                                    AND d.update_time > COALESCE(%s, '1970-01-01'::timestamp)
                                    AND date_trunc('second', d.update_time) != date_trunc('second', d.create_time)
                                    AND gm.user_id = d.user_id THEN d.id END) as dataset_updated_count,
                COUNT(DISTINCT CASE WHEN doc.create_time < COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') 
                                    AND doc.create_time > COALESCE(%s, '1970-01-01'::timestamp) 
                                    AND gm.user_id = d.user_id THEN doc.id END) as document_created_count,
                COUNT(DISTINCT CASE WHEN doc.update_time < COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') 
                                    AND doc.update_time > COALESCE(%s, '1970-01-01'::timestamp)
                                    AND date_trunc('second', doc.update_time) != date_trunc('second', doc.create_time)
                                    AND gm.user_id = d.user_id THEN doc.id END) as document_updated_count
              FROM "public"."group" g
              LEFT JOIN "public"."group_member" gm ON g.id = gm.group_id
              LEFT JOIN "public"."application" a ON gm.user_id = a.user_id
              LEFT JOIN "public"."dataset" d ON gm.user_id = d.user_id
              LEFT JOIN "public"."document" doc ON d.id = doc.dataset_id
              WHERE (%s IS NULL OR g.name ILIKE %s)
              GROUP BY g.id, g.name
            )
            SELECT 
              id,
              group_name,
              member_count,
              app_created_count,
              app_updated_count,
              dataset_created_count,
              dataset_updated_count,
              document_created_count,
              document_updated_count
            FROM group_stats
            ORDER BY group_name
            LIMIT %s OFFSET %s;
            """
            
            # 准备参数
            params = [
                end_time, start_time,  # app create
                end_time, start_time,  # app update
                end_time, start_time,  # dataset create
                end_time, start_time,  # dataset update 
                end_time, start_time,  # doc create
                end_time, start_time,  # doc update
                username, f'%{username}%' if username else '%',
                page_size, (current_page - 1) * page_size
            ]
            
            # 执行查询
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # 获取总数
            count_sql = """
            WITH group_stats AS (
              SELECT 
                g.id
              FROM "public"."group" g
              LEFT JOIN "public"."group_member" gm ON g.id = gm.group_id
              LEFT JOIN "public"."application" a ON gm.user_id = a.user_id
              LEFT JOIN "public"."dataset" d ON gm.user_id = d.user_id
              LEFT JOIN "public"."document" doc ON d.id = doc.dataset_id
              WHERE (%s IS NULL OR g.name ILIKE %s)
              GROUP BY g.id, g.name
            )
            SELECT COUNT(*) as total FROM group_stats;
            """
            
            with connection.cursor() as cursor:
                cursor.execute(count_sql, [username, f'%{username}%' if username else '%'])
                total = cursor.fetchone()[0]
            
            return {
                'total': total,
                'records': results,
                'current': current_page,
                'size': page_size
            }

    class Detail(serializers.Serializer):
        def get_detail(self, username, start_time=None, end_time=None):
            sql = """
            SELECT 
                u.username,
                u.nick_name,
                (
                    SELECT json_agg(app_stats)
                    FROM (
                        SELECT 
                            a.name,
                            a.create_time,
                            a.update_time,
                            CASE WHEN a.create_time BETWEEN COALESCE(%s, '1970-01-01'::timestamp) 
                                AND COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') THEN true ELSE false END as is_created,
                            CASE WHEN a.update_time BETWEEN COALESCE(%s, '1970-01-01'::timestamp) 
                                AND COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') 
                                AND date_trunc('second', a.update_time) != date_trunc('second', a.create_time) 
                                THEN true ELSE false END as is_updated
                        FROM application a
                        WHERE a.user_id = u.id
                        AND (
                            a.create_time BETWEEN COALESCE(%s, '1970-01-01'::timestamp) 
                                AND COALESCE(%s, CURRENT_DATE + INTERVAL '1 day')
                            OR 
                            a.update_time BETWEEN COALESCE(%s, '1970-01-01'::timestamp) 
                                AND COALESCE(%s, CURRENT_DATE + INTERVAL '1 day')
                        )
                    ) app_stats
                ) as apps,
                (
                    SELECT json_agg(dataset_stats)
                    FROM (
                        SELECT 
                            d.name,
                            d.create_time,
                            d.update_time,
                            CASE WHEN d.create_time BETWEEN COALESCE(%s, '1970-01-01'::timestamp) 
                                AND COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') THEN true ELSE false END as is_created,
                            CASE WHEN d.update_time BETWEEN COALESCE(%s, '1970-01-01'::timestamp) 
                                AND COALESCE(%s, CURRENT_DATE + INTERVAL '1 day')
                                AND date_trunc('second', d.update_time) != date_trunc('second', d.create_time)
                                THEN true ELSE false END as is_updated
                        FROM dataset d
                        WHERE d.user_id = u.id
                        AND (
                            d.create_time BETWEEN COALESCE(%s, '1970-01-01'::timestamp) 
                                AND COALESCE(%s, CURRENT_DATE + INTERVAL '1 day')
                            OR 
                            d.update_time BETWEEN COALESCE(%s, '1970-01-01'::timestamp) 
                                AND COALESCE(%s, CURRENT_DATE + INTERVAL '1 day')
                        )
                    ) dataset_stats
                ) as datasets,
                (
                    SELECT json_agg(doc_stats)
                    FROM (
                        SELECT 
                            doc.name,
                            doc.create_time,
                            doc.update_time,
                            CASE WHEN doc.create_time BETWEEN COALESCE(%s, '1970-01-01'::timestamp) 
                                AND COALESCE(%s, CURRENT_DATE + INTERVAL '1 day') THEN true ELSE false END as is_created,
                            CASE WHEN doc.update_time BETWEEN COALESCE(%s, '1970-01-01'::timestamp) 
                                AND COALESCE(%s, CURRENT_DATE + INTERVAL '1 day')
                                AND date_trunc('second', doc.update_time) != date_trunc('second', doc.create_time)
                                THEN true ELSE false END as is_updated
                        FROM document doc
                        JOIN dataset d ON doc.dataset_id = d.id
                        WHERE d.user_id = u.id
                        AND (
                            doc.create_time BETWEEN COALESCE(%s, '1970-01-01'::timestamp) 
                                AND COALESCE(%s, CURRENT_DATE + INTERVAL '1 day')
                            OR 
                            doc.update_time BETWEEN COALESCE(%s, '1970-01-01'::timestamp) 
                                AND COALESCE(%s, CURRENT_DATE + INTERVAL '1 day')
                        )
                    ) doc_stats
                ) as documents
            FROM "public"."user" u
            WHERE u.username = %s
            GROUP BY u.id, u.username, u.nick_name;
            """
            
            params = [
                start_time, end_time, start_time, end_time,  # apps is_created/is_updated check
                start_time, end_time, start_time, end_time,  # apps time filter
                start_time, end_time, start_time, end_time,  # datasets is_created/is_updated check
                start_time, end_time, start_time, end_time,  # datasets time filter
                start_time, end_time, start_time, end_time,  # documents is_created/is_updated check
                start_time, end_time, start_time, end_time,  # documents time filter
                username
            ]
            
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
            return results[0] if results else None 