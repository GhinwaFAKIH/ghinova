#!/usr/bin/env python3
"""Install a separate workspace; never edit an existing workspace or provider config."""
import argparse,json,shutil,subprocess,sys,urllib.request
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--model',required=True,help='Exact installed local Ollama model name, without ollama/');a=p.parse_args()
    if not shutil.which('openclaw'): sys.exit('OpenClaw was not found. Run this on the Mac where OpenClaw is installed.')
    if 'cloud' in a.model.lower() or '/' in a.model or not a.model.strip(): sys.exit('Choose an installed local model name, not a cloud/provider reference.')
    try:
        def api(route,data=None):
            req=urllib.request.Request('http://127.0.0.1:11434/api/'+route,data=json.dumps(data).encode() if data else None,headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
        models=api('tags').get('models',[])
        if a.model not in [m.get('name') for m in models]: sys.exit('Model not installed. Run ollama list and use an exact local model name.')
        info=api('show',{'model':a.model})
        if info.get('remote_host') or info.get('remote_model'): sys.exit('Remote model detected. Choose a local model.')
        if 'tools' not in info.get('capabilities',[]): sys.exit('This model does not report tool support. Choose a local tool-capable model.')
    except Exception: sys.exit('Cannot inspect local Ollama. Open Ollama on your Mac and try again.')
    workspace=Path.home()/'.openclaw'/'workspace-ghinova-tutorial'
    if workspace.exists(): sys.exit('Workspace already exists; nothing overwritten. Inspect openclaw agents list before retrying.')
    print('Creating GHINOVA tutorial workspace at',workspace)
    shutil.copytree(Path(__file__).parent/'workspace',workspace)
    (workspace/'outputs').mkdir(exist_ok=True)
    result=subprocess.run(['openclaw','agents','add','ghinova-tutorial','--workspace',str(workspace),'--model','ollama/'+a.model,'--non-interactive'])
    if result.returncode: sys.exit('Registration did not complete. Workspace retained. Check openclaw agents list; do not repeat blindly.')
    print('Workspace registered. Verify the agent model/provider and tool permissions in OpenClaw before your first lesson. No paid provider was configured.')
    print('Next: openclaw dashboard — select ghinova-tutorial and use FIRST-PROMPT.txt.')
if __name__=='__main__':main()
