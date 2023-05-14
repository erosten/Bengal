from .static_pst import SimpleEvaluation
from .dynamic_pst import DynamicPST
from .dynamic_pst_with_tricks import DynamicPSTwithTricks


def get_eval_fn(eval_fn):
    if eval_fn == 'simple_pst':
        return SimpleEvaluation.evaluate
    elif eval_fn == 'dynamic_pst':
        return DynamicPST.evaluate
    elif eval_fn == 'dynamic_tricks':
        return DynamicPSTwithTricks.evaluate
    
def get_eval_expl_fn(eval_fn):
    if eval_fn == 'simple_pst':
        return SimpleEvaluation.evaluate_explained
    elif eval_fn == 'dynamic_pst':
        return DynamicPST.evaluate_explained
    elif eval_fn == 'dynamic_tricks':
        return DynamicPSTwithTricks.evaluate_explained