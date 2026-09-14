/* Independent verifier: direct DFS over graph cycles, deliberately no cycle-space XOR. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int n, k, adj[64][64], chords[8][2];
static int ea[2000], eb[2000], em;
static uint64_t seenmask, tested, pancyclic, hits;
static unsigned long long lens;
static int target;
static int found[64];
static uint64_t rngstate=1;
static uint64_t rng64(void){rngstate^=rngstate<<7;rngstate^=rngstate>>9;return rngstate;}

static void dfs(int s, int v, int depth, uint64_t used) {
    for (int w=0; w<n; ++w) if (adj[v][w]) {
        if (w==s && depth+1>=3) { lens |= 1ULL<<(depth+1); continue; }
        if (w<=s || (used&(1ULL<<w))) continue;
        dfs(s,w,depth+1,used|(1ULL<<w));
    }
}
static unsigned long long spectrum(void) {
    lens=0;
    for(int s=0;s<n;s++) dfs(s,s,0,1ULL<<s);
    return lens;
}
static int ispan(int a,int b) { int d=b-a; if(d<0)d=-d; if(n-d<d)d=n-d; return d; }
static int has_triangle(void){ for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)if(adj[a][b])for(int c=b+1;c<n;c++)if(adj[a][c]&&adj[b][c])return 1; return 0; }
static int pan(void) { if(!has_triangle()) return 0; unsigned long long need=0; for(int i=3;i<=n;i++)need|=1ULL<<i; return (spectrum()&need)==need; }
static void setgraph(void) {
    memset(adj,0,sizeof(adj)); for(int i=0;i<n;i++){adj[i][(i+1)%n]=adj[(i+1)%n][i]=1;}
    for(int i=0;i<k;i++){int a=chords[i][0],b=chords[i][1];adj[a][b]=adj[b][a]=1;}
}
static void printw(void){printf("WITNESS n=%d k=%d :",n,k);for(int i=0;i<k;i++)printf(" (%d,%d)",chords[i][0],chords[i][1]);printf("\n");}
static void comb(int slot,int start,int fixedb) {
    if(slot==k){ tested++; setgraph(); if(pan()){hits++; printw();} return; }
    for(int q=start;q<em;q++) { int a=ea[q],b=eb[q];
        if(slot==0 && (a!=0 || b!=fixedb)) continue;
        chords[slot][0]=a;chords[slot][1]=b; comb(slot+1,q+1,fixedb);
    }
}
static void chunkfixed(int fixedb){
    em=0; for(int a=0;a<n;a++) for(int b=a+2;b<n;b++) if(!(a==0&&b==n-1)){ea[em]=a;eb[em]=b;em++;}
    comb(0,0,fixedb);
}
static void allfixed(void){
    for(int b=2;b<=n-2;b++) chunkfixed(b);
}
static void one(int nn,int kk,int *a,int *b){n=nn;k=kk;for(int i=0;i<k;i++){chords[i][0]=a[i];chords[i][1]=b[i];}setgraph();unsigned long long s=spectrum();printf("CHECK n=%d k=%d lengths=%d pancyclic=%s\n",n,k,__builtin_popcountll(s),pan()?"yes":"no");}
static void randomrun(int nn,int kk,unsigned long long count,uint64_t seed){n=nn;k=kk;rngstate=seed;unsigned long long ph=0;clock_t t=clock();em=0;for(int a=0;a<n;a++)for(int b=a+2;b<n;b++)if(!(a==0&&b==n-1)){ea[em]=a;eb[em]=b;em++;}for(unsigned long long q=0;q<count;q++){int used[2000]={0};for(int j=0;j<k;j++){int z;do{z=(int)(rng64()%em);}while(used[z]);used[z]=1;chords[j][0]=ea[z];chords[j][1]=eb[z];}setgraph();if(pan())ph++;}printf("RANDOM n=%d k=%d count=%llu seed=%llu pancyclic=%llu cpu_seconds=%.3f\n",n,k,count,(unsigned long long)seed,ph,(double)(clock()-t)/CLOCKS_PER_SEC);}
int main(int ac,char**av){
    if(ac<2){fprintf(stderr,"usage: indep 24|25|witnesses\n");return 2;}
    clock_t t=clock();
    if(!strcmp(av[1],"witnesses")){int a38[]={0,0,1,3,17},b38[]={2,18,12,19,20};one(38,5,a38,b38);int a40[]={0,1,2,3,4},b40[]={5,5,30,10,11};one(40,5,a40,b40);int a41[]={4,28,12,17,12,24},b41[]={13,30,26,31,29,27};one(41,6,a41,b41);}
    else if(!strcmp(av[1],"random")){if(ac<5)return 2;randomrun(atoi(av[2]),atoi(av[3]),strtoull(av[4],0,10),ac>=6?strtoull(av[5],0,10):1);}
    else {n=atoi(av[1]); k=4; if(ac>=3){ int b=atoi(av[2]); chunkfixed(b); printf("CHUNK n=%d b=%d tested=%llu pancyclic=%llu cpu_seconds=%.3f\n",n,b,tested,hits,(double)(clock()-t)/CLOCKS_PER_SEC); } else { allfixed(); printf("SUMMARY n=%d k=4 tested=%llu pancyclic=%llu cpu_seconds=%.3f\n",n,tested,hits,(double)(clock()-t)/CLOCKS_PER_SEC); }}
    return 0;
}
