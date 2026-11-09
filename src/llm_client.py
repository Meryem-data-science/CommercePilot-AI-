"""Adaptateurs de planification ; pas d'appel réseau à l'import ou en mode mock."""
import os


class ProviderError(Exception):
    pass


class ProviderTimeout(ProviderError):
    pass


class ProviderQuota(ProviderError):
    pass


class GroqClient:
    def __init__(self):
        # N'effectue aucune requête : construction paresseuse à la première sélection.
        self.model = os.environ.get('GROQ_MODEL')
        self.key_present = bool(os.environ.get('GROQ_API_KEY'))

    def complete(self, messages, tools, config):
        if not self.model or not self.key_present:
            raise ProviderError('configuration_absente')
        try:
            from groq import Groq, APITimeoutError, RateLimitError, APIError
        except ImportError:
            raise ProviderError() from None
        try:
            with Groq(api_key=os.environ['GROQ_API_KEY'], timeout=config['api_timeout_seconds'], max_retries=0) as client:
                response = client.chat.completions.create(model=self.model, messages=messages, tools=tools,
                            tool_choice='auto', max_completion_tokens=config['max_output_tokens'], temperature=0)
            message = response.choices[0].message
            return {'calls':[{'id':c.id,'name':c.function.name,'arguments':c.function.arguments}
                             for c in (message.tool_calls or [])]}
        except APITimeoutError:
            raise ProviderTimeout() from None
        except RateLimitError:
            raise ProviderQuota() from None
        except (APIError,KeyError,IndexError,AttributeError,ValueError):
            raise ProviderError() from None


class MockClient:
    """Réponses scriptées ; ne prétend pas comprendre le langage naturel."""
    def __init__(self, steps=None):
        self.steps = list(steps if steps is not None else [{'calls':[]}])
        self.index = 0

    def complete(self, messages, tools, config):
        if self.index >= len(self.steps):
            return {'calls':[]}
        step = self.steps[self.index]
        self.index += 1
        if isinstance(step,Exception):
            raise step
        return step
