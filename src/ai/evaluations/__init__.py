from .static_pst import SimpleEvaluation
from .dynamic_pst import DynamicPST
from .hueristic import Hueristic


static = Hueristic()
def get_eval_fn(eval_fn):
    if eval_fn == 'simple_pst':
        return SimpleEvaluation.evaluate
    elif eval_fn == 'dynamic_pst':
        return DynamicPST.evaluate
    elif eval_fn == 'dynamic_tricks':
        return static.evaluate
    
def get_eval_expl_fn(eval_fn):
    if eval_fn == 'simple_pst':
        return SimpleEvaluation.evaluate_explained
    elif eval_fn == 'dynamic_pst':
        return DynamicPST.evaluate_explained
    elif eval_fn == 'dynamic_tricks':
        return static.evaluate_explained