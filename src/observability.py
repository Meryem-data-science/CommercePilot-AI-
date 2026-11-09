"""Traces minimales sans contenu utilisateur ; agrégation locale sans service externe."""
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
import json
import math
import os
from pathlib import Path
import threading
import time
import uuid

PATH = Path(__file__).resolve().parents[1] / 'logs' / 'agent_events.jsonl'
TOOLS = {'search_faq', 'get_order_status', 'sales_summary'}
STATUSES = {'ok', 'error', 'refused', 'clarification'}
ERRORS = {'configuration','invalid_context','invalid_input','security_policy','timeout','quota',
          'provider','invalid_response','tool_selection','incomplete_plan','tool_limit','unknown_tool',
          'invalid_arguments','clarification','access_denied','tool_error','iteration_limit','unhandled'}
TECHNICAL = {'configuration','timeout','quota','provider','invalid_response','tool_error','unhandled'}
_sink = ContextVar('commercepilot_trace_sink', default=None)
_lock = threading.Lock()


def write_trace(event):
    """Un append JSONL par interaction ; permissions restrictives à la création."""
    PATH.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(event, ensure_ascii=False, allow_nan=False)+'\n').encode()
    with _lock:
        fd = os.open(PATH, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            os.write(fd, data)
        finally:
            os.close(fd)


@contextmanager
def trace_sink(sink):
    """Injection limitée au contexte courant, pour tests et évaluations locales."""
    token = _sink.set(sink)
    try:
        yield
    finally:
        _sink.reset(token)


def observed(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            started = time.perf_counter()
            timestamp = datetime.now(timezone.utc).isoformat()
            request_id = str(uuid.uuid4())
        except Exception:
            return function(*args, **kwargs)
        result = None
        try:
            result = function(*args, **kwargs)
            return result
        finally:
            # Ne jamais lire les arguments, messages, réponses textuelles ou exceptions.
            # Une panne de télémétrie est silencieuse et ne change pas le résultat métier.
            try:
                status = result.get('status') if isinstance(result, dict) else 'error'
                status = status if status in STATUSES else 'error'
                error = result.get('error_type') if isinstance(result, dict) else 'unhandled'
                error = error if error in ERRORS else ('other' if error else None)
                tools = [t for t in result.get('tools_called', []) if t in TOOLS] if isinstance(result, dict) else []
                event = {'schema_version':1, 'result_available':isinstance(result, dict), 'request_id':request_id, 'timestamp':timestamp,
                         'status':status, 'duration_ms':max(0., (time.perf_counter()-started)*1000),
                         'tools_called':tools, 'tool_count':len(tools), 'refused':status=='refused',
                         'error_type':error, 'final_answer':{'category':status, 'content':'not_retained'}}
                (_sink.get() or write_trace)(event)
            except Exception:
                pass
    return wrapper


def summarize(events):
    """P95 au rang le plus proche supérieur : rang ceil(.95*N), indexé à 1."""
    durations = []
    tools = errors = refusals = clarifications = technical = 0
    for event in events:
        duration = event['duration_ms']
        if event['status'] not in STATUSES or not isinstance(duration, (int,float)) or not math.isfinite(duration) or duration < 0:
            raise ValueError('Trace invalide')
        count = event['tool_count']
        if type(count) is not int or count < 0:
            raise ValueError('Trace invalide')
        durations.append(duration)
        tools += count
        errors += event['status']=='error'
        technical += event['status']=='error' and event['error_type'] in TECHNICAL
        refusals += event['status']=='refused'
        clarifications += event['status']=='clarification'
    n = len(durations)
    return {'request_count':n, 'error_count':errors, 'technical_error_count':technical,
            'refusal_count':refusals, 'clarification_count':clarifications,
            'error_rate':errors/n if n else None, 'refusal_rate':refusals/n if n else None,
            'mean_latency_ms':sum(durations)/n if n else None,
            'p95_latency_ms':sorted(durations)[math.ceil(.95*n)-1] if n else None,
            'mean_tools_per_request':tools/n if n else None}


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Synthèse agrégée des traces, sans afficher les interactions.')
    parser.add_argument('--path', type=Path, default=PATH)
    args = parser.parse_args()
    with args.path.open(encoding='utf-8') as file:
        result = summarize(json.loads(line) for line in file if line.strip())
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
