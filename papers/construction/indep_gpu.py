"""CUDA direct-DFS replication; deliberately does not use cycle-space XOR."""
import argparse, json, math, os, time
import numpy as np
import cupy as cp
try: cp.cuda.runtime.setDeviceFlags(4)
except Exception: pass

KERNEL=r'''
extern "C" __global__ void go(int n,int k,int fixedb,int r,const int* ca,const int* cb,int M,const unsigned long long* Ctab,unsigned long long start,unsigned long long count,unsigned long long* hits,int* out){
 unsigned long long tid=(unsigned long long)blockIdx.x*blockDim.x+threadIdx.x;if(tid>=count)return;unsigned long long N=start+tid;int A[8],B[8];A[0]=0;B[0]=fixedb;
 int idx[4];for(int i=r;i>=1;i--){int lo=i-1,hi=M-1;while(lo<hi){int md=(lo+hi+1)>>1;if(Ctab[md*5+i]<=N)lo=md;else hi=md-1;}idx[i-1]=lo;N-=Ctab[lo*5+i];}
 for(int i=0;i<r;i++){A[i+1]=ca[idx[i]];B[i+1]=cb[idx[i]];}
 unsigned long long adj[64];for(int i=0;i<n;i++)adj[i]=(1ULL<<((i+n-1)%n))|(1ULL<<((i+1)%n));
 for(int j=0;j<k;j++){adj[A[j]]|=1ULL<<B[j];adj[B[j]]|=1ULL<<A[j];}
 unsigned long long lens=0;int sv[64],sn[64],sd[64];
 for(int s=0;s<n;s++){int top=0;sv[0]=s;sn[0]=0;sd[0]=0;unsigned long long used=1ULL<<s;
  while(top>=0){int v=sv[top],d=sd[top];unsigned long long rem=adj[v];while(sn[top]<n && !(rem&(1ULL<<sn[top])))sn[top]++;if(sn[top]>=n){top--;if(top>=0)used&=~(1ULL<<v);continue;}int w=sn[top]++;if(w==s&&d+1>=3){lens|=1ULL<<(d+1);continue;}if(w<=s||(used&(1ULL<<w)))continue;if(d+1>=n)continue;top++;sv[top]=w;sn[top]=0;sd[top]=d+1;used|=1ULL<<w;}
 }
 unsigned long long need=((1ULL<<(n+1))-1)&~7ULL;if((lens&need)==need){unsigned long long q=atomicAdd(hits,1ULL);if(q<8){for(int j=0;j<k;j++){out[q*16+2*j]=A[j];out[q*16+2*j+1]=B[j];}}}
}
'''
def table():
 t=np.zeros((1024,5),dtype=np.uint64)
 for n in range(1024):
  t[n,0]=1
  for r in range(1,5): t[n,r]=math.comb(n,r) if n>=r else 0
 return t.reshape(-1)
def chords(n): return [(a,b) for a in range(n) for b in range(a+2,n) if not(a==0 and b==n-1)]
def main():
 p=argparse.ArgumentParser();p.add_argument('n',type=int);p.add_argument('k',type=int);p.add_argument('b',type=int);p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=1<<24);p.add_argument('--state',default='indep-gpu-state.json');a=p.parse_args();n,k,b=a.n,a.k,a.b
 allc=chords(n); cand=[e for e in allc if e!=(0,b)];r=k-1;total=math.comb(len(cand),r);start=min(a.start,total);count=min(a.count,total-start)
 ca=cp.asarray([x[0] for x in cand],dtype=cp.int32);cb=cp.asarray([x[1] for x in cand],dtype=cp.int32);ct=cp.asarray(table());hits=cp.zeros(1,dtype=cp.uint64);out=cp.zeros(8*16,dtype=cp.int32);ker=cp.RawKernel(KERNEL,'go');t=time.perf_counter();threads=128;blocks=(count+threads-1)//threads;ker((blocks,),(threads,),(n,k,b,r,ca,cb,len(cand),ct,np.uint64(start),np.uint64(count),hits,out));cp.cuda.Device().synchronize();dt=time.perf_counter()-t;nh=int(hits.get()[0]);arr=out.get();ws=[]
 for q in range(min(nh,8)):ws.append([(int(arr[q*16+2*j]),int(arr[q*16+2*j+1])) for j in range(k)])
 print(json.dumps({'n':n,'k':k,'b':b,'start':start,'count':count,'total':total,'hits':nh,'witnesses':ws,'seconds':dt},separators=(',',':')))
 if a.state:
  d=json.load(open(a.state)) if os.path.exists(a.state) else {};d[f'{n}-{k}-{b}-{start}']={'count':count,'hits':nh,'seconds':dt};json.dump(d,open(a.state,'w'))
if __name__=='__main__':main()
