import copy
import json
import unittest
from pathlib import Path

import numpy as np
import analyze as a


def row(arm, y, admitted=True, family='one', instance='one-L1-1'):
    return dict(kind='primary',family=family,level='L1',instance_id=instance,arm=arm,seed=1,
                terminal='SUCCESS' if y else 'EXECUTION',terminal_success=y,
                qualification_legacy={'qualified':admitted})


class PairingEstimandTests(unittest.TestCase):
    def test_reject_duplicate_before_silent_overwrite(self):
        rows=[row(x,1) for x in a.ARMS]
        with self.assertRaisesRegex(ValueError,'duplicate'):
            a.index_rows(rows+[copy.deepcopy(rows[0])])

    def test_missing_arm_is_error(self):
        with self.assertRaisesRegex(ValueError,'missing arm'):
            a.index_rows([row('R0',1),row('R1',1)])

    def test_pair_by_family_instance_not_input_order_or_seed_alone(self):
        rows=[row(x,1,family=f,instance=f+'-L1-1') for f in ('a','b') for x in a.ARMS]
        self.assertEqual(len(a.index_rows(rows)),2)
        self.assertEqual(a.index_rows(rows),a.index_rows(rows[::-1]))

    def test_excluded_terminal_requires_explicit_denominator_handling(self):
        rows=[row(x,1) for x in a.ARMS]
        rows[1]['terminal']='PROVIDER_FAILURE'
        with self.assertRaisesRegex(ValueError,'excluded terminal'):
            a.index_rows(rows)

    def test_counterfactual_and_interaction_sign(self):
        arms={'R0':row('R0',1,True),'R1':row('R1',1,False),'R2':row('R2',0,True)}
        self.assertEqual(a.vector(arms,'R1'),(0,-1,-1))
        self.assertEqual(a.vector(arms,'R2'),(-1,-1,0))
        arms['R0']['qualification_legacy']['qualified']=False
        self.assertEqual(a.vector(arms,'R2'),(-1,0,1))

    def test_joint_resampling_preserves_within_pair_estimand_identity(self):
        x=np.array([[0,-1,-1],[1,0,-1],[-1,0,1],[0,0,0]])
        draws=a.bootstrap(x,['a','a','b','b'],1000,42)
        np.testing.assert_allclose(draws[:,2],draws[:,1]-draws[:,0])
        np.testing.assert_array_equal(draws,a.bootstrap(x,['a','a','b','b'],1000,42))

    def test_stratification_keeps_family_weights_fixed(self):
        values=np.array([[1,1,0],[1,1,0],[-1,-1,0],[-1,-1,0]])
        draw=a.bootstrap(values,['a','a','b','b'],1000,42)
        np.testing.assert_array_equal(draw,np.zeros((1000,3)))
        self.assertGreater(float(np.var(a.bootstrap(values,['a','a','b','b'],1000,42,'unstratified_instance'))),0)

    def test_zero_discordance_keeps_nonzero_uncertainty_bound(self):
        result=a.describe(np.zeros(64),np.zeros(100))
        self.assertEqual(result['ci95_percentile'],[0,0])
        self.assertGreater(result['zero_nonzero_event_upper95'],0.045)
        self.assertLess(result['zero_nonzero_event_upper95'],0.046)

    def test_frozen_data_exact_denominators_and_l3_claim(self):
        rows=[json.loads(s) for s in (a.SOURCE/'runs/confirmatory/results.jsonl').read_text().splitlines()]
        index=a.index_rows(rows)
        self.assertEqual(len(index),256)
        for lv,n in [('L1',64),('L2',64),('L3',128)]:
            self.assertEqual(sum(k[1]==lv for k in index),n)
        l3=[v for k,v in index.items() if k[1]=='L3']
        for arm,current,legacy in [('R0',125,100),('R1',126,111),('R2',124,58)]:
            self.assertEqual(sum(v[arm]['terminal_success'] for v in l3),current)
            self.assertEqual(sum(v[arm]['terminal_success']*v[arm]['qualification_legacy']['qualified'] for v in l3),legacy)
        self.assertEqual(sum(a.vector(v,'R2')[2] for v in l3),-41)


if __name__=='__main__':
    unittest.main(verbosity=2)
