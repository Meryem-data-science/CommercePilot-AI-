"""Contrôle local reproductible : motifs de secrets, exclusions et traces synthétiques."""
import json
import os
from pathlib import Path
import re
import subprocess
from quality.check import secret_issues

ROOT=Path(__file__).resolve().parents[1]
PATTERN=re.compile(rb'(?:gsk_|ghp_|github_pat_)[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')


def main():
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).split(b'\0')
    paths+=[p for p in subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).split(b'\0') if p not in paths]
    issues=secret_issues([ROOT/os.fsdecode(p) for p in paths if p])
    objects=subprocess.check_output(['git','rev-list','--objects','--all'],cwd=ROOT).splitlines()
    ids=list(dict.fromkeys(line.split(b' ',1)[0] for line in objects))
    values=[v.encode() for k,v in os.environ.items() if len(v)>12 and any(x in k.upper() for x in ('API_KEY','TOKEN','PASSWORD','SECRET'))]
    hits=[];blobs=0
    # Batch Git en mémoire ; aucun contenu correspondant imprimé ou enregistré.
    proc=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    try:
        for oid in ids:
            proc.stdin.write(oid+b'\n');proc.stdin.flush()
            header=proc.stdout.readline().split()
            size=int(header[2]);data=proc.stdout.read(size);proc.stdout.read(1)
            if header[1]!=b'blob':continue
            blobs+=1
            if PATTERN.search(data) or any(v in data for v in values):hits.append(oid.decode())
    finally:
        proc.stdin.close();proc.stdout.close();proc.wait()
    ignored={}
    for name in ['.env','.env.local','.streamlit/secrets.toml','logs/runtime.jsonl','private.key','work/private.txt']:
        ignored[name]=subprocess.run(['git','check-ignore','-q','--no-index',name],cwd=ROOT).returncode==0
    events=[json.loads(line) for line in (ROOT/'evaluation/anonymized_traces.jsonl').read_text().splitlines()]
    keys={'schema_version','result_available','request_id','timestamp','status','duration_ms','tools_called','tool_count','refused','error_type','final_answer'}
    traces_safe=all(set(e)==keys and e['final_answer']=={'category':e['status'],'content':'not_retained'} for e in events)
    assert not re.search(r'CLI-\d{3}|CMD-DEMO-\d{3}',json.dumps(events))
    report={'scope':'Local source audit and reachable Git history; pattern-based, not a security guarantee',
            'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'files_scanned':len([p for p in paths if p]),'file_findings':issues,
            'reachable_blobs_scanned':blobs,'history_pattern_findings_count':len(hits),
            'history_finding_object_ids':hits,'ignored_sensitive_paths':ignored,
            'example_trace_count':len(events),'example_traces_minimized':traces_safe,
            'public_verification':{'five_mock_paths':'reported verified by owner','runtime_sha':'pending','runtime_python':'pending','remote_secret_inventory':'not inspected'},
            'ci_artifact_review':{'run_id':42714484210,'artifact_id':13718015315,'retention_days':3,'metadata_verified':True,'archive_contents_inspected':False}}
    dest=ROOT/'security/audit_results.json';dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    ok=not issues and not hits and all(ignored.values()) and traces_safe
    print('Audit local : '+('PASS' if ok else 'FAIL')+f' ; {blobs} blobs historiques contrôlés ; aucune valeur sensible imprimée.')
    return 0 if ok else 1


if __name__=='__main__':
    raise SystemExit(main())
