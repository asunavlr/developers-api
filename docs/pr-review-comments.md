# Roteiro de Code Review (PT/EN)

Objetivo: comentários prontos para usar em um Pull Request, cobrindo arquitetura, segurança, validação, testes e deploy.

## Visão Geral
- PT: Stack `FastAPI + Supabase + Pydantic v2 + Docker + Render`. Objetivo: API de usuários com registro, login, perfil e rota admin para status. Documentação via OpenAPI.
- EN: Stack `FastAPI + Supabase + Pydantic v2 + Docker + Render`. Goal: user API with register, login, profile, and admin status route. OpenAPI docs.

## python/app/main.py
- PT: Restringir `CORS` por domínio quando o frontend estiver definido; hoje está amplo para facilitar testes. Considerar `GET /health` e logs JSON com `correlation_id`.
- EN: Restrict `CORS` to known client origins once defined; currently permissive for testing. Consider `GET /health` and JSON logs with `correlation_id`.

## python/app/routers/auth.py
- PT: `POST /auth/register` e `POST /auth/login` delegam validação ao Supabase. Revisar mensagens de erro para não vazar detalhes internos. Planejar `POST /auth/refresh` e rate limit no login.
- EN: `POST /auth/register` and `POST /auth/login` rely on Supabase validation. Review error messages to avoid leaking internals. Plan `POST /auth/refresh` and rate limit login.
- PT: Pergunta: se `sign_up` funcionar e o insert em `users` falhar, há compensação/rollback?
- EN: Question: if `sign_up` succeeds but `users` insert fails, do we have compensation/rollback?

## python/app/routers/users.py
- PT: `PUT /users/{id}` corretamente impede atualizar outro usuário (403). Validar campos permitidos e normalizar telefone/email.
- EN: `PUT /users/{id}` correctly forbids cross-user updates (403). Validate allowed fields and normalize phone/email.
- PT: `GET /users/me` retorna `role`; considerar auditoria de acessos e cache leve de claims.
- EN: `GET /users/me` returns `role`; consider access audit logging and lightweight claims cache.
- PT: `PATCH /users/{id}/status` exige `role=admin`. Garantir que `role` não é editável pelo usuário e que RLS impede elevação indevida.
- EN: `PATCH /users/{id}/status` requires `role=admin`. Ensure `role` is immutable by users and RLS prevents privilege escalation.

## python/app/schemas.py
- PT: Bom uso de Pydantic v2. Aplicar `EmailStr`, `StrictStr`, tamanhos mínimos/máximos e enums para `status`. Adicionar exemplos via `json_schema_extra`.
- EN: Good use of Pydantic v2. Apply `EmailStr`, `StrictStr`, min/max lengths, and enums for `status`. Add examples via `json_schema_extra`.

## python/app/utils/auth.py
- PT: Tratar `Authorization: Bearer` ausente/malformado com 401 consistente. Validar expiração e assinatura via JWKS do Supabase.
- EN: Handle missing/malformed `Authorization: Bearer` with consistent 401. Validate token expiry and signature via Supabase JWKS.

## python/app/deps/supabase_client.py
- PT: Fail-fast se faltarem `SUPABASE_URL`/`SUPABASE_ANON_KEY`. Minimizar uso do `service_role` apenas onde necessário.
- EN: Fail-fast if `SUPABASE_URL`/`SUPABASE_ANON_KEY` are missing. Minimize `service_role` usage to where strictly needed.

## python/tests/
- PT: Expandir cobertura para cenários negativos: 401 sem token, 403 cross-user, 422 inválido, admin-only negado. Adicionar e2e `register → login → me` e admin `status`.
- EN: Expand coverage for negative scenarios: 401 no token, 403 cross-user, 422 invalid, admin-only denied. Add e2e `register → login → me` and admin `status`.

## Dockerfile
- PT: `EXPOSE 3000` e `--port ${PORT:-3000}` compatíveis com Render. Tornar número de workers configurável via env.
- EN: `EXPOSE 3000` and `--port ${PORT:-3000}` compatible with Render. Make worker count configurable via env.

## docker-compose.yml
- PT: `3000:3000` ok. Adicionar `healthcheck` e volume (opcional) para hot-reload. Logs mais verbosos em dev.
- EN: `3000:3000` OK. Add `healthcheck` and optional volume for hot-reload. More verbose logs in dev.

## render.yaml
- PT: Confirmar env vars (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, opcional `SUPABASE_SERVICE_ROLE_KEY`). Configurar domínio customizado, SSL, política de auto-deploy.
- EN: Confirm env vars (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, optional `SUPABASE_SERVICE_ROLE_KEY`). Configure custom domain, SSL, auto-deploy policy.

## README.md
- PT: Documentação atualizada para porta 3000. Adicionar seção de erros comuns e exemplos curl/Postman.
- EN: Docs updated to port 3000. Add common errors section and curl/Postman examples.

## Segurança e Observabilidade
- PT: Restringir CORS, adicionar rate limit no login, LGPD para dados pessoais. Logs JSON por request e `GET /health`.
- EN: Restrict CORS, add rate limiting on login, privacy compliance for PII. JSON logs per request and `GET /health`.