insert into methodology_versions(version_code,release_date,status,description,assumptions)
values ('VITENUS-METHODOLOGY-0.1',current_date,'experimental','Prototype de diagnostic, valorisation circulaire, priorisation, Payback, ROI et mesure de performance.',jsonb_build_object('ipc_weights',jsonb_build_object('IE',.30,'FT',.20,'IA',.20,'CI',.10,'TN',.10,'GR',.10),'roi_bands_are_pilot_governance',true,'not_iso_certification',true))
on conflict (version_code) do nothing;
