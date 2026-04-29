# M0.X Phase A Post-Migration Schema Audit

Captured: 2026-04-29T00:23:03Z
Git commit: 40d51cc8389d545e7e9306121026bbf623412423

## \d+ tasks

```
                                                             Table "public.tasks"
      Column       |           Type           | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
-------------------+--------------------------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id                | uuid                     |           | not null | gen_random_uuid() | plain    |             |              | 
 title             | text                     |           | not null |                   | extended |             |              | 
 description       | text                     |           |          |                   | extended |             |              | 
 bucket            | text                     |           | not null |                   | extended |             |              | 
 project           | text                     |           |          |                   | extended |             |              | 
 module            | text                     |           |          |                   | extended |             |              | 
 status            | text                     |           | not null | 'open'::text      | extended |             |              | 
 priority          | text                     |           |          | 'normal'::text    | extended |             |              | 
 blocked_by        | uuid                     |           |          |                   | plain    |             |              | 
 trigger_phase     | text                     |           |          |                   | extended |             |              | 
 source            | text                     |           | not null |                   | extended |             |              | 
 estimated_minutes | integer                  |           |          |                   | plain    |             |              | 
 github_issue_url  | text                     |           |          |                   | extended |             |              | 
 created_at        | timestamp with time zone |           | not null | now()             | plain    |             |              | 
 updated_at        | timestamp with time zone |           | not null | now()             | plain    |             |              | 
 done_at           | timestamp with time zone |           |          |                   | plain    |             |              | 
 metadata          | jsonb                    |           |          | '{}'::jsonb       | extended |             |              | 
Indexes:
    "tasks_pkey" PRIMARY KEY, btree (id)
    "idx_tasks_bucket_status" btree (bucket, status)
    "idx_tasks_module" btree (module) WHERE module IS NOT NULL
    "idx_tasks_open_by_phase" btree (trigger_phase) WHERE status = ANY (ARRAY['open'::text, 'blocked'::text])
Check constraints:
    "tasks_priority_check" CHECK (priority = ANY (ARRAY['urgent'::text, 'high'::text, 'normal'::text, 'low'::text]))
    "tasks_source_check" CHECK (source = ANY (ARRAY['operator'::text, 'claude'::text, 'reflection_worker'::text, 'migration'::text]))
    "tasks_status_check" CHECK (status = ANY (ARRAY['open'::text, 'in_progress'::text, 'blocked'::text, 'done'::text, 'cancelled'::text]))
Foreign-key constraints:
    "tasks_blocked_by_fkey" FOREIGN KEY (blocked_by) REFERENCES tasks(id) ON DELETE SET NULL
Referenced by:
    TABLE "tasks" CONSTRAINT "tasks_blocked_by_fkey" FOREIGN KEY (blocked_by) REFERENCES tasks(id) ON DELETE SET NULL
Triggers:
    trg_set_updated_at_tasks BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap

```

## \d+ operator_preferences

```
                                                  Table "public.operator_preferences"
   Column   |           Type           | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
------------+--------------------------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id         | uuid                     |           | not null | gen_random_uuid() | plain    |             |              | 
 category   | text                     |           | not null |                   | extended |             |              | 
 key        | text                     |           | not null |                   | extended |             |              | 
 value      | text                     |           | not null |                   | extended |             |              | 
 scope      | text                     |           | not null | 'global'::text    | extended |             |              | 
 active     | boolean                  |           | not null | true              | plain    |             |              | 
 source     | text                     |           | not null |                   | extended |             |              | 
 created_at | timestamp with time zone |           | not null | now()             | plain    |             |              | 
 updated_at | timestamp with time zone |           | not null | now()             | plain    |             |              | 
 metadata   | jsonb                    |           |          | '{}'::jsonb       | extended |             |              | 
Indexes:
    "operator_preferences_pkey" PRIMARY KEY, btree (id)
    "idx_preferences_category_active" btree (category) WHERE active
    "idx_preferences_scope_active" btree (scope) WHERE active
    "operator_preferences_category_key_scope_key" UNIQUE CONSTRAINT, btree (category, key, scope)
Check constraints:
    "operator_preferences_category_check" CHECK (category = ANY (ARRAY['communication'::text, 'tooling'::text, 'workflow'::text, 'identity'::text, 'language'::text, 'schedule'::text]))
    "operator_preferences_source_check" CHECK (source = ANY (ARRAY['operator_explicit'::text, 'inferred'::text, 'migration'::text]))
Triggers:
    trg_set_updated_at_operator_preferences BEFORE UPDATE ON operator_preferences FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap

```

## \d+ router_feedback

```
                                                         Table "public.router_feedback"
       Column        |           Type           | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
---------------------+--------------------------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id                  | uuid                     |           | not null | gen_random_uuid() | plain    |             |              | 
 request_id          | text                     |           |          |                   | extended |             |              | 
 feedback_type       | text                     |           | not null |                   | extended |             |              | 
 operator_note       | text                     |           |          |                   | extended |             |              | 
 proposed_correction | jsonb                    |           |          |                   | extended |             |              | 
 status              | text                     |           | not null | 'pending'::text   | extended |             |              | 
 reviewed_by         | text                     |           |          |                   | extended |             |              | 
 applied_at          | timestamp with time zone |           |          |                   | plain    |             |              | 
 created_at          | timestamp with time zone |           | not null | now()             | plain    |             |              | 
Indexes:
    "router_feedback_pkey" PRIMARY KEY, btree (id)
    "idx_router_feedback_request" btree (request_id) WHERE request_id IS NOT NULL
    "idx_router_feedback_status" btree (status)
    "idx_router_feedback_type" btree (feedback_type) WHERE status = 'pending'::text
Check constraints:
    "router_feedback_feedback_type_check" CHECK (feedback_type = ANY (ARRAY['missing_context'::text, 'wrong_bucket'::text, 'wrong_complexity'::text, 'irrelevant_lessons'::text, 'too_much_context'::text, 'low_quality_response'::text]))
    "router_feedback_status_check" CHECK (status = ANY (ARRAY['pending'::text, 'reviewed'::text, 'applied'::text, 'dismissed'::text]))
Access method: heap

```

## \d+ best_practices

```
                                                          Table "public.best_practices"
        Column        |           Type           | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description 
----------------------+--------------------------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 id                   | uuid                     |           | not null | gen_random_uuid() | plain    |             |              | 
 title                | text                     |           | not null |                   | extended |             |              | 
 guidance             | text                     |           | not null |                   | extended |             |              | 
 rationale            | text                     |           |          |                   | extended |             |              | 
 domain               | text                     |           | not null |                   | extended |             |              | 
 scope                | text                     |           | not null | 'global'::text    | extended |             |              | 
 applicable_buckets   | text[]                   |           | not null | '{}'::text[]      | extended |             |              | 
 tags                 | text[]                   |           | not null | '{}'::text[]      | extended |             |              | 
 active               | boolean                  |           | not null | true              | plain    |             |              | 
 source               | text                     |           | not null |                   | extended |             |              | 
 derived_from_lessons | uuid[]                   |           |          | '{}'::uuid[]      | extended |             |              | 
 previous_guidance    | text                     |           |          |                   | extended |             |              | 
 previous_rationale   | text                     |           |          |                   | extended |             |              | 
 superseded_by        | uuid                     |           |          |                   | plain    |             |              | 
 embedding            | vector(3072)             |           |          |                   | external |             |              | 
 created_at           | timestamp with time zone |           | not null | now()             | plain    |             |              | 
 updated_at           | timestamp with time zone |           | not null | now()             | plain    |             |              | 
Indexes:
    "best_practices_pkey" PRIMARY KEY, btree (id)
    "idx_best_practices_applicable_buckets" gin (applicable_buckets)
    "idx_best_practices_domain" btree (domain) WHERE active
    "idx_best_practices_scope" btree (scope) WHERE active
    "idx_best_practices_superseded" btree (superseded_by) WHERE superseded_by IS NOT NULL
    "idx_best_practices_tags" gin (tags)
Check constraints:
    "best_practices_domain_check" CHECK (domain = ANY (ARRAY['process'::text, 'convention'::text, 'workflow'::text, 'communication'::text]))
    "best_practices_source_check" CHECK (source = ANY (ARRAY['operator'::text, 'derived_from_lessons'::text, 'migration'::text]))
Foreign-key constraints:
    "best_practices_superseded_by_fkey" FOREIGN KEY (superseded_by) REFERENCES best_practices(id)
Referenced by:
    TABLE "best_practices" CONSTRAINT "best_practices_superseded_by_fkey" FOREIGN KEY (superseded_by) REFERENCES best_practices(id)
Triggers:
    trg_set_updated_at_best_practices BEFORE UPDATE ON best_practices FOR EACH ROW EXECUTE FUNCTION set_updated_at()
Access method: heap

```

## \d+ decisions

```
                                                              Table "public.decisions"
        Column        |           Type           | Collation | Nullable |       Default       | Storage  | Compression | Stats target | Description 
----------------------+--------------------------+-----------+----------+---------------------+----------+-------------+--------------+-------------
 id                   | uuid                     |           | not null | gen_random_uuid()   | plain    |             |              | 
 bucket               | text                     |           | not null |                     | extended |             |              | 
 project              | text                     |           | not null |                     | extended |             |              | 
 projects_indexed_id  | uuid                     |           |          |                     | plain    |             |              | 
 client_id            | uuid                     |           |          |                     | plain    |             |              | 
 title                | text                     |           | not null |                     | extended |             |              | 
 context              | text                     |           | not null |                     | extended |             |              | 
 decision             | text                     |           | not null |                     | extended |             |              | 
 consequences         | text                     |           | not null |                     | extended |             |              | 
 alternatives         | text                     |           |          |                     | extended |             |              | 
 status               | text                     |           | not null | 'active'::text      | extended |             |              | 
 superseded_by_id     | uuid                     |           |          |                     | plain    |             |              | 
 embedding            | vector(3072)             |           |          |                     | external |             |              | 
 created_at           | timestamp with time zone |           | not null | now()               | plain    |             |              | 
 scope                | text                     |           | not null | 'operational'::text | extended |             |              | 
 applicable_buckets   | text[]                   |           | not null | '{}'::text[]        | extended |             |              | 
 decided_by           | text                     |           | not null | 'operator'::text    | extended |             |              | 
 tags                 | text[]                   |           | not null | '{}'::text[]        | extended |             |              | 
 severity             | text                     |           |          | 'normal'::text      | extended |             |              | 
 adr_number           | integer                  |           |          |                     | plain    |             |              | 
 derived_from_lessons | uuid[]                   |           |          | '{}'::uuid[]        | extended |             |              | 
Indexes:
    "decisions_pkey" PRIMARY KEY, btree (id)
    "decisions_adr_number_key" UNIQUE CONSTRAINT, btree (adr_number)
    "idx_decisions_applicable_buckets" gin (applicable_buckets)
    "idx_decisions_client" btree (client_id) WHERE client_id IS NOT NULL
    "idx_decisions_indexed_project" btree (projects_indexed_id) WHERE projects_indexed_id IS NOT NULL
    "idx_decisions_project" btree (bucket, project)
    "idx_decisions_scope_status" btree (scope, status)
    "idx_decisions_tags" gin (tags)
Check constraints:
    "decisions_scope_check" CHECK (scope = ANY (ARRAY['architectural'::text, 'process'::text, 'product'::text, 'operational'::text]))
Foreign-key constraints:
    "decisions_projects_indexed_id_fkey" FOREIGN KEY (projects_indexed_id) REFERENCES projects_indexed(id)
    "decisions_superseded_by_id_fkey" FOREIGN KEY (superseded_by_id) REFERENCES decisions(id)
Referenced by:
    TABLE "decisions" CONSTRAINT "decisions_superseded_by_id_fkey" FOREIGN KEY (superseded_by_id) REFERENCES decisions(id)
Triggers:
    trg_decisions_emb AFTER INSERT ON decisions FOR EACH ROW EXECUTE FUNCTION notify_missing_embedding()
Access method: heap

```

