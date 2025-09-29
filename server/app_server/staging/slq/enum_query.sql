SELECT n.nspname AS schema_name,
       t.typname AS enum_type
FROM pg_type t
JOIN pg_namespace n ON n.oid = t.typnamespace
WHERE t.typtype = 'e'
ORDER BY schema_name, enum_type;


SELECT n.nspname AS schema_name,
       t.typname AS enum_type,
       e.enumlabel AS enum_value,
       e.enumsortorder
FROM pg_type t
JOIN pg_namespace n ON n.oid = t.typnamespace
JOIN pg_enum e ON t.oid = e.enumtypid
WHERE t.typtype = 'e'
ORDER BY schema_name, enum_type, e.enumsortorder;
