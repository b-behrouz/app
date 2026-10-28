#!/usr/bin/env python3
"""Fail-closed manual gate. A typed field records an approval; it never grants chat consent."""
import os,re,subprocess

def authorize(event,ref,operation,revision,approved_revision,confirmation,enabled,current,is_ancestor):
    if event!='workflow_dispatch' or ref!='refs/heads/main':raise ValueError('Only manual runs on main are allowed')
    if operation=='check':return current
    if operation not in {'deploy','rollback'}:raise ValueError('Unknown operation')
    if enabled!='true':raise ValueError('HOSTING_ENABLED must be true; it is not an approval')
    if not re.fullmatch(r'[0-9a-f]{40}',revision) or revision!=approved_revision:raise ValueError('Exact separately approved full SHA required')
    expected=operation.upper()+' hamghadamcare.ir '+revision
    if confirmation!=expected:raise ValueError('Explicit domain, operation and SHA confirmation required')
    if not is_ancestor(revision):raise ValueError('Revision must exist in main history')
    return revision

def main():
    current=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    def ancestor(sha):return subprocess.run(['git','merge-base','--is-ancestor',sha,current],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
    op=os.environ.get('OPERATION','')
    sha=authorize(os.environ.get('GITHUB_EVENT_NAME',''),os.environ.get('GITHUB_REF',''),op,
        os.environ.get('REVISION',''),os.environ.get('APPROVED_REVISION',''),os.environ.get('CONFIRMATION',''),
        os.environ.get('ENABLED',''),current,ancestor)
    with open(os.environ['GITHUB_OUTPUT'],'a') as out:out.write(f'operation={op}\nrevision={sha}\nready=true\n')
if __name__=='__main__':main()
