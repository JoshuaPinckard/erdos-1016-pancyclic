"""Windows job CPU hard cap and measured resource log for a child command.

Usage: python gpu_supervise.py --log resources.jsonl -- python script.py ...
The child and descendants together are capped at 7% of system CPU capacity.
"""
import argparse
import ctypes as C
from ctypes import wintypes as W
import json
import subprocess
import time
import psutil


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--log',required=True)
    p.add_argument('--cpu-percent',type=int,default=7)
    p.add_argument('--child-output')
    p.add_argument('command',nargs=argparse.REMAINDER)
    args=p.parse_args(); command=args.command
    if not 1<=args.cpu_percent<=7: p.error('CPU cap must be 1..7 percent')
    if command[0]=='--': command=command[1:]
    kernel=C.WinDLL('kernel32',use_last_error=True)
    kernel.CreateJobObjectW.restype=W.HANDLE
    kernel.SetInformationJobObject.argtypes=[W.HANDLE,C.c_int,C.c_void_p,W.DWORD]
    kernel.AssignProcessToJobObject.argtypes=[W.HANDLE,W.HANDLE]
    kernel.CloseHandle.argtypes=[W.HANDLE]
    class Rate(C.Structure):
        _fields_=[('flags',W.DWORD),('rate',W.DWORD)]
    job=kernel.CreateJobObjectW(None,None)
    if not job: raise C.WinError(C.get_last_error())
    rate=Rate(1|4,args.cpu_percent*100) # ENABLE | HARD_CAP, hundredths of one percent
    if not kernel.SetInformationJobObject(job,15,C.byref(rate),C.sizeof(rate)):
        raise C.WinError(C.get_last_error())
    output=open(args.child_output,'x',encoding='utf-8',newline='\n') if args.child_output else None
    child=subprocess.Popen(command,creationflags=4,stdout=output,stderr=subprocess.STDOUT if output else None) # CREATE_SUSPENDED
    try:
        if not kernel.AssignProcessToJobObject(job,W.HANDLE(child._handle)):
            raise C.WinError(C.get_last_error())
        nt=C.WinDLL('ntdll'); nt.NtResumeProcess.argtypes=[W.HANDLE]
        if nt.NtResumeProcess(W.HANDLE(child._handle))!=0: raise RuntimeError('resume failed')
        proc=psutil.Process(child.pid); proc.cpu_percent(); psutil.cpu_percent()
        with open(args.log,'x',encoding='utf-8',newline='\n') as f:
            while child.poll() is None:
                time.sleep(1)
                try: cpu=proc.cpu_percent()/psutil.cpu_count()
                except psutil.NoSuchProcess: break
                gpu=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,power.draw,memory.used','--format=csv,noheader,nounits'],capture_output=True,text=True)
                row=dict(time=time.time(),child_cpu_percent=cpu,host_cpu_percent=psutil.cpu_percent(),gpu=gpu.stdout.strip(),gpu_exit=gpu.returncode,job_cpu_cap_percent=args.cpu_percent)
                f.write(json.dumps(row)+'\n'); f.flush()
        raise SystemExit(child.wait())
    finally:
        if child.poll() is None: child.kill(); child.wait()
        kernel.CloseHandle(job)
        if output: output.close()


if __name__=='__main__': main()
