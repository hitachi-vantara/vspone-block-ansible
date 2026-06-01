import threading
import os

# Create a thread-local storage engine
_thread_local_context = threading.local()


def set_option_a1(is_forced: bool):
    """Called by the frontend Ansible module."""
    # 1. Fallback for single-threaded legacy processes
    os.environ['_OPTION_A1'] = str(is_forced)
    # 2. Secure isolation for concurrent thread contexts
    _thread_local_context.option_a1 = is_forced


def get_option_a1() -> bool:
    """Called by the backend helper files."""
    # Check the thread-isolated context first; fall back to os.getenv if empty
    return getattr(_thread_local_context, 'option_a1', os.getenv('_OPTION_A1', 'False').strip().lower() == 'true')
