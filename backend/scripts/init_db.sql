-- Script de inicialización PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
SELECT 'PostgreSQL listo para SEIRA 2.0!' as status;
