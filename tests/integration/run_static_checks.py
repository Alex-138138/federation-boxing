import runpy
checks=['api_contract_check.py','frontend_contract_check.py','security_check.py','cms_contract_check.py','model_contract_check.py','deploy_contract_check.py']
for name in checks:
    print('==',name,'==')
    runpy.run_path('tests/integration/'+name,run_name='__main__')
print('All static integration checks: OK')
