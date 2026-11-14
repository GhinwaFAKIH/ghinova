#!/usr/bin/env python3
"""Export a local tutorial JSON to Markdown and an unexecuted notebook. Stdlib only."""
import argparse, ast, json, re
from pathlib import Path

def export(path, overwrite=False):
    path=Path(path).resolve()
    data=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data,dict): raise ValueError('Lesson must be an object')
    for key in ('title','level','language','validation'):
        if not isinstance(data.get(key),str) or not data[key].strip(): raise ValueError('Missing text: '+key)
    for key in ('objectives','sources'):
        if not isinstance(data.get(key),list) or not all(isinstance(x,str) and x.strip() for x in data[key]): raise ValueError('Invalid list: '+key)
    if not data['objectives']: raise ValueError('Add at least one learning objective')
    cells=data.get('cells')
    if not isinstance(cells,list) or not cells: raise ValueError('Add lesson cells')
    nb=[]; markdown=['# '+data['title'],f"Level: {data['level']} · Language: {data['language']}",'## Learning objectives','\n'.join('- '+o for o in data['objectives'])]
    nb.append({'cell_type':'markdown','metadata':{},'source':'\n\n'.join(markdown)})
    kinds=set()
    for i,cell in enumerate(cells,1):
        if not isinstance(cell,dict) or cell.get('type') not in ('markdown','code') or not isinstance(cell.get('source'),str): raise ValueError('Invalid cell '+str(i))
        kind=cell['type'];source=cell['source'];kinds.add(kind)
        item={'cell_type':kind,'metadata':{},'source':source}
        if kind=='code':
            ast.parse(source,filename=f'cell-{i}')
            item.update(execution_count=None,outputs=[])
            runs=[len(x) for x in re.findall(r'`+',source)]
            fence='`'*max(3,max(runs,default=0)+1)
            markdown.append(f'{fence}python\n{source}\n{fence}')
        else: markdown.append(source)
        nb.append(item)
    if kinds!={'code','markdown'}: raise ValueError('Include explanations and Python code')
    footer='## Sources\n'+ ('\n'.join('- '+s for s in data['sources']) or 'No external sources supplied.')+'\n\n## Validation\n'+data['validation']+'\n\nExport check: Python syntax passed. This exporter did not execute the code.'
    nb.append({'cell_type':'markdown','metadata':{},'source':footer});markdown.append(footer)
    notebook={'nbformat':4,'nbformat_minor':4,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'cells':nb}
    targets=[path.with_name('tutorial.md'),path.with_name('tutorial.ipynb')]
    if not overwrite and any(t.exists() for t in targets): raise FileExistsError('Output exists; use a new revision folder or --overwrite')
    targets[0].write_text('\n\n'.join(markdown)+'\n',encoding='utf-8');targets[1].write_text(json.dumps(notebook,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return targets

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('lesson');parser.add_argument('--overwrite',action='store_true');args=parser.parse_args()
    try:
        for path in export(args.lesson,args.overwrite): print(path)
    except (ValueError,SyntaxError,OSError) as exc: parser.exit(1,str(exc)+'\n')
