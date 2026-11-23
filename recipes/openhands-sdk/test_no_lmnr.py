"""Offline regression tests for the downstream optional-Laminar patch."""
import asyncio
import importlib.util
import importlib.metadata
import subprocess
import types
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

for key in list(os.environ):
    if key.startswith(('LMNR_', 'OTEL_', 'OPENHANDS_OBSERVABILITY_')):
        del os.environ[key]
os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'

assert importlib.util.find_spec('lmnr') is None
assert importlib.util.find_spec('lmnr_claude_code_proxy') is None

from openhands.sdk import Agent, LocalConversation, LLM
from openhands.sdk.agent.acp_agent import ACPAgent
from openhands.sdk.observability import laminar
from litellm import ModelResponse

assert not laminar.should_enable_observability()
laminar.maybe_init_laminar()

@laminar.observe(name='sync-test')
def sync_call():
    return 42

@laminar.observe(name='async-test')
async def async_call():
    return 43

assert sync_call() == 42
assert asyncio.run(async_call()) == 43
with laminar.llm_call_span('test') as span:
    assert span is None
assert laminar.start_root_span('test') is None
print('PASS: SDK/ACP imports and tracing-disabled sync/async helpers')

response = ModelResponse(
    model='gpt-4o-mini',
    choices=[{'index': 0, 'finish_reason': 'tool_calls', 'message': {
        'role': 'assistant', 'content': None,
        'tool_calls': [{'id': 'call_finish', 'type': 'function', 'function': {
            'name': 'finish', 'arguments': '{"message":"offline test complete"}'}}],
    }}],
    usage={'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15},
)
with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
    with patch('openhands.sdk.llm.llm.litellm_completion', return_value=response) as call:
        agent = Agent(llm=LLM(model='openai/gpt-4o-mini', api_key='test-key'), tools=[])
        conversation = LocalConversation(agent=agent, workspace=tmp, persistence_dir=tmp,
                                    profile_store_dir=str(Path(tmp) / 'profiles'))
        try:
            conversation.send_message('Finish this offline test.')
            conversation.run()
            assert call.call_count == 1, call.call_count
            assert conversation.state.execution_status.value == 'finished'
        finally:
            conversation.close()
print('PASS: local conversation with mocked model and real finish-tool execution')
assert 'lmnr' not in sys.modules
print('PASS: lmnr was never imported')

# Every supported endpoint/key must fail clearly, without caching an enabled state.
for key in laminar._OBSERVABILITY_ENV_KEYS:
    with patch.dict(os.environ, {key: 'test-endpoint'}):
        for operation in (laminar.maybe_init_laminar, sync_call,
                          lambda: asyncio.run(async_call())):
            try:
                operation()
            except RuntimeError as exc:
                assert "optional 'lmnr'" in str(exc)
                assert 'openhands-sdk[observability]' in str(exc)
                assert key in str(exc)
            else:
                raise AssertionError(f'{key}: expected actionable missing-dependency error')
        assert not laminar._observability_enabled
    assert not laminar.should_enable_observability()
    assert sync_call() == 42
print('PASS: all tracing variables fail clearly; clearing them restores normal calls')

# The wheel metadata must agree with the conda dependency list.
from packaging.requirements import Requirement
requirements = [Requirement(r) for r in importlib.metadata.requires('openhands-sdk')]
optional = [r for r in requirements if r.name == 'lmnr']
assert len(optional) == 1
assert optional[0].marker is not None
assert not optional[0].marker.evaluate({'extra': ''})
assert optional[0].marker.evaluate({'extra': 'observability'})
print('PASS: installed metadata declares lmnr only as an extra')

# Simulate an installed optional integration; preserve the existing initialize path.
fake_lmnr = types.ModuleType('lmnr')
fake_lmnr.__spec__ = importlib.util.spec_from_loader('lmnr', loader=None)
from unittest.mock import Mock
fake_lmnr.Laminar = Mock()
fake_lmnr.Laminar.is_initialized.return_value = False
fake_lmnr.Instruments = Mock()
with patch.dict(sys.modules, {'lmnr': fake_lmnr}):
    with patch.dict(os.environ, {'LMNR_PROJECT_API_KEY': 'test-key'}):
        laminar.maybe_init_laminar()
        fake_lmnr.Laminar.initialize.assert_called_once()
laminar._observability_enabled = False
print('PASS: installed optional integration retains the initialization path (mocked)')

# Also cover endpoint configuration already present before the first SDK import.
result = subprocess.run(
    [sys.executable, '-c', 'import openhands.sdk'],
    env={**os.environ, 'OTEL_EXPORTER_OTLP_ENDPOINT': 'http://127.0.0.1:1'},
    text=True, capture_output=True,
)
assert result.returncode != 0
assert "optional 'lmnr'" in result.stderr
assert 'ModuleNotFoundError' not in result.stderr
print('PASS: first import with tracing configured reports an actionable error')

