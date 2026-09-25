import os
from supabase import create_client, Client


def get_client() -> Client:
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    if not url or not key:
        raise RuntimeError('SUPABASE_URL and SUPABASE_KEY are required.')
    return create_client(url, key)


def save_assessment(client: Client, company_name: str, project_name: str, opportunity_name: str, indices: dict, roi: float, payback: float, data_confidence: float, methodology_version='VITENUS-METHODOLOGY-0.1'):
    company = client.table('companies').insert({'name': company_name}).execute().data[0]
    project = client.table('projects').insert({'company_id': company['id'], 'name': project_name, 'methodology_version': methodology_version}).execute().data[0]
    opportunity = client.table('opportunities').insert({'project_id': project['id'], 'name': opportunity_name}).execute().data[0]
    score = client.table('scores').insert({
        'opportunity_id': opportunity['id'], 'methodology_version': methodology_version,
        'ie': indices['IE'], 'ft': indices['FT'], 'ia': indices['IA'], 'ci': indices['CI'],
        'tn': indices['TN'], 'gr': indices['GR'], 'ipc': indices['IPC'],
        'data_confidence': data_confidence, 'roi_projected': roi,
        'payback_months': None if payback == float('inf') else payback,
        'recommendation': indices.get('recommendation'),
        'calculation_trace': indices.get('trace', {}),
    }).execute().data[0]
    return company, project, opportunity, score
