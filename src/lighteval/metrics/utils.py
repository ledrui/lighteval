from dataclasses import dataclass
from enum import Enum, auto


class MetricCategory(Enum):
    TARGET_PERPLEXITY = auto()
    PERPLEXITY = auto()
    GENERATIVE = auto()
    GENERATIVE_LOGPROB = auto()
    MULTICHOICE = auto()
    MULTICHOICE_ONE_TOKEN = auto()
    IGNORED = auto()


class MetricUseCase(Enum):
    # General
    ACCURACY = auto()
    PERPLEXITY = auto()
    # Task specific
    CODE = auto()
    COPYRIGHT = auto()
    MATH = auto()
    REASONING = auto()
    SOCIAL_IMPACTS = auto()
    SUMMARIZATION = auto()
    TRANSLATION = auto()
    NONE = auto()


@dataclass
class Metric:
    metric: str
    higher_is_better: bool
    category: MetricCategory
    use_case: MetricUseCase
    sample_level_fn: callable
    corpus_level_fn: callable

    def get_doc(self):
        return self.sample_level_fn.__doc__

    def compute(self, **kwargs) -> dict:  # result: Union[list[ModelReturn], ModelReturn], formatted_doc: Doc) -> dict:
        if self.category == MetricCategory.IGNORED:
            return {}
        if isinstance(self, MetricGrouping):
            return self.sample_level_fn(**kwargs)  # result, formatted_doc,
        return {self.metric: self.sample_level_fn(**kwargs)}  # result, formatted_doc,


@dataclass
class MetricGrouping(Metric):
    """Some metrics are more advantageous to compute together at once.
    For example, if a costly preprocessing is the same for all metrics, it makes more sense to compute it once.
    """

    metric: list[str]
    corpus_level_fn: dict[str:callable]
    higher_is_better: dict[str:callable]


@dataclass
class CorpusLevelMetric(Metric):
    """Metric computed over the whole corpora, with computations happening at the aggregation phase"""

    pass


@dataclass
class SampleLevelMetric(Metric):
    """Metric computed per sample, then aggregated over the corpus"""

    pass


@dataclass
class CorpusLevelMetricGrouping(MetricGrouping):
    """MetricGrouping computed over the whole corpora, with computations happening at the aggregation phase"""

    pass


@dataclass
class SampleLevelMetricGrouping(MetricGrouping):
    """MetricGrouping are computed per sample, then aggregated over the corpus"""

    pass
