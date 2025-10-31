# Propostas de Issues

Lista de melhorias com títulos, descrições, critérios de aceitação, prioridade e rótulos sugeridos.

## 1) Restringir CORS por domínio
- Descrição: Limitar `allow_origins` a domínios conhecidos do frontend.
- Critérios de aceitação:
  - Configuração de CORS só permite origens definidas em env (`ALLOWED_ORIGINS`).
  - Documentar como setar origens em produção.
- Prioridade: Alta
- Labels: security, config, backend

## 2) Adicionar endpoint de saúde `GET /health`
- Descrição: Endpoint simples que retorna 200 OK com status.
- Critérios de aceitação:
  - Rota `/health` respondendo com JSON `{status:"ok"}`.
  - Incluir verificação leve (ex.: tempo de resposta do app, opcional DB ping).
- Prioridade: Média
- Labels: ops, observability

## 3) Padronizar tratamento de erros (400/401/403/422)
- Descrição: Middleware/handlers para respostas de erro consistentes.
- Critérios de aceitação:
  - Mensagens com código, tipo e detalhe sem expor internals do Supabase.
  - Testes cobrindo cenários comuns.
- Prioridade: Alta
- Labels: DX, error-handling

## 4) Rate limiting no login
- Descrição: Mitigar brute force com limite por IP/usuário.
- Critérios de aceitação:
  - Limite configurável via env (ex.: `LOGIN_RATE_LIMIT`).
  - Resposta 429 quando excedido.
- Prioridade: Alta
- Labels: security, auth

## 5) Token validation via JWKS do Supabase
- Descrição: Validar assinatura e expiração dos JWTs contra JWKS.
- Critérios de aceitação:
  - Biblioteca/implementação confiável para JWKS fetch/cache.
  - 401 para tokens inválidos/expirados.
- Prioridade: Alta
- Labels: security, auth

## 6) Testes de cenários negativos e e2e
- Descrição: Expandir cobertura para falhas e fluxo completo.
- Critérios de aceitação:
  - 401 sem token, 403 cross-user, 422 payload inválido, admin-only negado.
  - e2e `register → login → me` e admin `status`.
- Prioridade: Média
- Labels: testing

## 7) Políticas e constraints no banco
- Descrição: Garantir índices e restrições (email único, enum status).
- Critérios de aceitação:
  - Índice único em `users.email`.
  - Enum/constraint para `users.status` com valores válidos.
- Prioridade: Média
- Labels: database

## 8) Minimizar uso de `service_role`
- Descrição: Revisar rotas que usam `service_role` e reduzir escopo.
- Critérios de aceitação:
  - Documentar quais rotas precisam `service_role`.
  - Garantir que demais rotas usam `anon_client` com RLS.
- Prioridade: Alta
- Labels: security, auth

## 9) Logs JSON e `correlation_id`
- Descrição: Padronizar logs estruturados por request com id de correlação.
- Critérios de aceitação:
  - Logger configurado com JSON, incluindo método, rota, latência, status.
  - Incluir `correlation_id` via header ou gerado.
- Prioridade: Média
- Labels: observability, ops

## 10) Documentação: erros comuns e exemplos curl/Postman
- Descrição: Ampliar README com troubleshooting e exemplos.
- Critérios de aceitação:
  - Seção com erros típicos (cold start, 401/403/422) e soluções.
  - Exemplos de requests curl e Postman atualizados.
- Prioridade: Baixa
- Labels: docs, DX