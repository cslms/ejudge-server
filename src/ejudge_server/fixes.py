# Mokey patch ejudge.execution_manager to use billiard.Process instead of
# multiprocessing.Process
import billiard
from ejudge import execution_manager as _ex
_ex.multiprocessing = billiard
