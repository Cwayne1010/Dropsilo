-- Override dbt's default schema naming behavior.
-- By default dbt concatenates target.schema + custom_schema (e.g. DBT_DEV_LOGIC_VIEWS).
-- This macro uses the custom_schema name directly, enabling clean Snowflake schema names
-- (STAGING, INTERMEDIATE, DBT_LOGIC_VIEWS) regardless of the target environment.
--
-- In prod: models land in the exact schema configured in dbt_project.yml
-- In dev:  use `dbt run --vars '{"dev_suffix": "_dev"}'` to isolate if needed

{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema | upper }}
    {%- else -%}
        {{ custom_schema_name | upper }}
    {%- endif -%}
{%- endmacro %}
