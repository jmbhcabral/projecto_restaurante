from django.db import migrations

SEQ = "perfil_numero_cliente_seq"
TABLE = "perfil_perfil"
PREFIX = "CEW-"
START_AT = 1050  # business decision


class Migration(migrations.Migration):

    dependencies = [
        ("perfil", "0033_remove_morada_finalidade_morada_morada_created_at_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql=f"""
            DO $$
            BEGIN
                -- 1) Create sequence if missing
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relkind = 'S'
                      AND c.relname = '{SEQ}'
                      AND n.nspname = 'public'
                ) THEN
                    CREATE SEQUENCE public.{SEQ};
                END IF;

                -- 2) Align sequence with existing data
                --    If no data exists, start at {START_AT}
                PERFORM setval(
                    '{SEQ}',
                    COALESCE(
                        (
                            SELECT MAX(
                                NULLIF(
                                    regexp_replace(numero_cliente, '^' || '{PREFIX}', ''),
                                    ''
                                )::int
                            )
                            FROM {TABLE}
                            WHERE numero_cliente LIKE '{PREFIX}%'
                        ),
                        {START_AT - 1}
                    ),
                    true
                );
            END$$;
            """,
            reverse_sql=f"DROP SEQUENCE IF EXISTS public.{SEQ};",
        ),
    ]