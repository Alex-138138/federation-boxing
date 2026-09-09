import runpy
checks=['api_contract_check.py','frontend_contract_check.py','security_check.py','cms_contract_check.py','model_contract_check.py','deploy_contract_check.py','python_syntax_check.py','js_contract_check.py','router_registration_check.py','db_safety_check.py','auth_flow_check.py','role_access_check.py','cms_publish_flow_check.py','data_relation_check.py']
for name in checks:
    print('==',name,'==')
    runpy.run_path('tests/integration/'+name,run_name='__main__')
print('All static integration checks: OK')
