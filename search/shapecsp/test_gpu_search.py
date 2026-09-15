"""Behavior tests, including every colex rank of a small composition space.

--mutate removes high-word coverage in memory; the n=67 control must turn RED.
"""
import math
import sys
import unittest
import gpu_search as G


class GpuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine=G.Engine(12,70,127)

    def test_all_small_compositions(self):
        lows=[1,2,1,2]; n=12
        total=math.comb(n-sum(lows)+len(lows)-1,len(lows)-1)
        seen=set()
        for r in range(total):
            a=G.unrank(r,n,lows)
            self.assertEqual(sum(a),n)
            self.assertTrue(all(x>=y for x,y in zip(a,lows)))
            self.assertEqual(G.rank_arcs(a,lows),r)
            seen.add(tuple(a))
        self.assertEqual(len(seen),total)

    def test_gpu_exhaustive_small_and_batched(self):
        d=G.record(4,[(0,2),(1,3)])
        n=10; total=math.comb(n-1,3)
        hits,_,(arcs,flags)=self.engine.run(n,[d],[0],[1],total,True)
        for r in range(total):
            a=G.unrank(r,n,d['lows'])
            self.assertEqual(list(arcs[r,:4]),a)
            self.assertEqual(bool(flags[r]),G.V.pancyclic(n,G.materialise(d['chords'],a)))
        batch,_,_=self.engine.run(n,[d,d],[0,0],[1,1],total)
        self.assertEqual(len(batch),2*len(hits))

    def test_largest_branch_count_and_word_boundaries(self):
        d=G.record(12,[(i,i+6) for i in range(6)])
        for n in (63,64,65,68,69,70):
            total=math.comb(n-1,11)
            for r in (0,total//2,total-1):
                _,_,(arcs,flags)=self.engine.run(n,[d],[r],[1],1,True)
                a=G.unrank(r,n,d['lows'])
                self.assertEqual(list(arcs[0,:12]),a)
                self.assertEqual(bool(flags[0]),G.V.pancyclic(n,G.materialise(d['chords'],a)))

    def test_known_controls(self):
        evidence=G.controls(self.engine)
        self.assertEqual(evidence['mismatches'],0)
        self.assertEqual([x['n'] for x in evidence['witnesses']],[67,56])

    def test_entire_known_family(self):
        for n in range(41,68):
            ch=[(0,2),(0,n-7),(1,13),(3,n-6),(4,31),(n-8,n-5)]
            d,a=G.canonical_witness(n,ch)
            hits,_,(arcs,flags)=self.engine.run(n,[d],[G.rank_arcs(a,d['lows'])],[1],1,True)
            self.assertTrue(G.V.pancyclic(n,ch))
            self.assertEqual(len(hits),1)
            self.assertEqual(list(arcs[0,:d['b']]),a)
            self.assertEqual(int(flags[0]),1)

    def test_rejects_false_gpu_sat(self):
        original=G.CUDA
        try:
            G.CUDA=G.CUDA.replace('int sat=((cov0&need0)==need0 && (cov1&need1)==need1);','int sat=1;')
            broken=G.Engine(12,70,127)
        finally:
            G.CUDA=original
        d=G.record(12,[(i,i+6) for i in range(6)])
        with self.assertRaisesRegex(RuntimeError,'independent verifier rejected GPU SAT'):
            broken.run(70,[d],[0],[1],1)


if __name__=='__main__':
    if '--mutate' in sys.argv:
        sys.argv.remove('--mutate')
        G.CUDA=G.CUDA.replace('cov1|=1ULL<<(len-64)','cov1|=0ULL')
    if '--mutate-verifier' in sys.argv:
        sys.argv.remove('--mutate-verifier')
        G.V.pancyclic=lambda n,ch: True
    unittest.main()
