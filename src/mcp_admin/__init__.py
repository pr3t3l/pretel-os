"""mcp_admin — admin console for pretel-os (Module 10 fase 1).

FastAPI + Jinja2 + HTMX server-rendered. Listens on 127.0.0.1; exposed
to the operator via Cloudflare Tunnel + Cloudflare Access at
`mcp-admin.alfredopretelvargas.com`. The FastAPI process never sees
unauthenticated traffic — Cloudflare Access enforces auth at the edge.

Per CONSTITUTION §2.1: every mutation routes through an existing MCP
tool (preference_set, save_lesson, archive_project, decision_record,
etc.). The admin is a peer consumer of the MCP gateway, not a parallel
write path.

See specs/mcp_admin/{spec,plan,tasks,phase_a_close}.md.
"""
