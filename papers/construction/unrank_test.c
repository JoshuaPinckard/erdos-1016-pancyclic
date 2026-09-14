#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
static uint64_t T[1024][5];
static uint64_t C(int n,int r){return (n<1024&&r<5)?T[n][r]:0;}
static void unrank(uint64_t N,int r,int out[]){for(int i=r;i>=1;i--){int lo=i-1,hi=1023;while(lo<hi){int md=(lo+hi+1)/2;if(T[md][i]<=N)lo=md;else hi=md-1;}out[i-1]=lo;N-=T[lo][i];}}
static uint64_t rankc(int r,int *a){uint64_t z=0;for(int i=1;i<=r;i++)z+=T[a[i-1]][i];return z;}
int main(void){for(int i=0;i<1024;i++){T[i][0]=1;for(int j=1;j<5;j++)T[i][j]=(i>=j)?(T[i-1][j-1]+T[i-1][j]):0;} unsigned seed=20260914; srand(seed); int rs[]={2,3,4}, ms[]={10,50,200,779}; unsigned long long fails=0;
 for(int ri=0;ri<3;ri++)for(int mi=0;mi<4;mi++){int r=rs[ri],m=ms[mi];uint64_t total=C(m,r), lim=(m==779?1000000:total); for(uint64_t q=0;q<lim;q++){uint64_t N=(m==779)?(((uint64_t)rand()<<32)^rand())%total:q;int a[4];unrank(N,r,a);for(int i=1;i<r;i++)if(a[i]<=a[i-1]){printf("FAIL increasing r=%d M=%d N=%llu\n",r,m,(unsigned long long)N);fails++;goto next;}if(rankc(r,a)!=N){printf("FAIL rank r=%d M=%d N=%llu got=%llu\n",r,m,(unsigned long long)N,(unsigned long long)rankc(r,a));fails++;goto next;} } printf("PASS r=%d M=%d tested=%llu total=%llu\n",r,m,(unsigned long long)lim,(unsigned long long)total); next:; }
 printf("SUMMARY seed=%u failures=%llu\n",seed,fails);return fails?1:0;}
