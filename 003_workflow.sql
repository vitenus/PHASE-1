-- VITENUS Circular Engine V0.3 — workflow commercial/technical before execution
create table if not exists service_requests (
    id uuid primary key default gen_random_uuid(),
    company_name text not null,
    origin text,
    received_at date,
    status text not null default 'Em espera',
    summary text,
    declared_problem text,
    initial_scope text,
    initial_data text,
    created_at timestamptz not null default now()
);

create table if not exists service_proposals (
    id uuid primary key default gen_random_uuid(),
    service_request_id uuid references service_requests(id) on delete set null,
    company_name text not null,
    fit_conclusion text,
    justification text,
    limitations text,
    scope text,
    created_at timestamptz not null default now()
);

create index if not exists idx_service_requests_status on service_requests(status);
create index if not exists idx_service_proposals_request on service_proposals(service_request_id);
