import functools
from typing import List

from refact_data_pipeline import DatasetOpts


class HumanEvalContinuation:
    def __init__(
            self,
            inner_filter,
            dataopts: DatasetOpts
    ):
        self.inner_filter = inner_filter
        self.dataopts = dataopts
        self.enc = dataopts.encoding

    def decode_result(self, prompt, tokens_with_completion: List[int]):
        txt = self.enc.decode(tokens_with_completion, cut_at_eot=True)
        assert txt.startswith(prompt)
        completion = txt[len(prompt):]
        for stop in ["\nclass", "\ndef", "\n#", "\nif", "\nprint"]:
            if stop in completion:
                i = completion.find(stop)
                assert i != -1
                completion = completion[:i]
        return {
            "completion": completion,
            "tokens_with_completion": [int(t) for t in tokens_with_completion],
        }

    def __iter__(self):
        for ex in self.inner_filter:
            ex["prompt"] = ex["prompt"].strip()
            ex["completion"] = ex["canonical_solution"]
            ex["decode_result_fn"] = functools.partial(self.decode_result, ex["prompt"])
            yield ex
