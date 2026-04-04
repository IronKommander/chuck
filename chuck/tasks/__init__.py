from .compute_core import TASK_SPEC as COMPUTE_CORE_TASK
from .data_encoding import TASK_SPEC as DATA_ENCODING_TASK
from .graph_analytics import TASK_SPEC as GRAPH_ANALYTICS_TASK
from .io_pipeline import TASK_SPEC as IO_PIPELINE_TASK
from .memory_index import TASK_SPEC as MEMORY_INDEX_TASK
from .memory_tier import TASK_SPEC as MEMORY_TIER_TASK
from .ordering_core import TASK_SPEC as ORDERING_CORE_TASK
from .prime_analytics import TASK_SPEC as PRIME_ANALYTICS_TASK
from .relational_fusion import TASK_SPEC as RELATIONAL_FUSION_TASK
from .retrieval_core import TASK_SPEC as RETRIEVAL_CORE_TASK

TASKS = [
    IO_PIPELINE_TASK,
    ORDERING_CORE_TASK,
    RETRIEVAL_CORE_TASK,
    DATA_ENCODING_TASK,
    GRAPH_ANALYTICS_TASK,
    PRIME_ANALYTICS_TASK,
    MEMORY_TIER_TASK,
    MEMORY_INDEX_TASK,
    COMPUTE_CORE_TASK,
    RELATIONAL_FUSION_TASK,
]
