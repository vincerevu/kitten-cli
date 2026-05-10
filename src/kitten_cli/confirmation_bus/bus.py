
import asyncio
import uuid
from typing import Any, Callable, Dict, List, Optional
from kitten_cli.confirmation_bus.types import (
    MessageBusType,
    ToolConfirmationRequest,
    ToolConfirmationResponse,
    ToolPolicyRejection,
)
from kitten_cli.agents.confirmation import PolicyDecision, check_policy
from kitten_cli.config.settings import AppConfig


class MessageBus:
    """
    Async pub/sub message bus for tool confirmation flow.
    
    Flow:
    1. Executor publishes TOOL_CONFIRMATION_REQUEST
    2. Bus checks policy → ALLOW/DENY/ASK_USER
    3. If ALLOW → auto-emit TOOL_CONFIRMATION_RESPONSE(confirmed=True)
    4. If DENY → emit TOOL_POLICY_REJECTION + TOOL_CONFIRMATION_RESPONSE(confirmed=False)
    5. If ASK_USER → forward request to UI listeners → UI sends response back
    """

    def __init__(self, config: AppConfig, debug: bool = False):
        self._config = config
        self._debug = debug
        self._listeners: Dict[str, List[Callable]] = {}
        self._pending: Dict[str, asyncio.Future] = {}

    def subscribe(self, event_type: str, listener: Callable) -> None:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: str, listener: Callable) -> None:
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(listener)
            except ValueError:
                pass

    def _emit(self, event_type: str, message: Any) -> None:
        for listener in self._listeners.get(event_type, []):
            listener(message)

    async def publish(self, message: Any) -> None:
        msg_type = getattr(message, "type", None)
        if not msg_type:
            return

        if msg_type == MessageBusType.TOOL_CONFIRMATION_REQUEST:
            decision = check_policy(
                message.tool_name, message.tool_args, self._config
            )

            # Honor forced_decision from trusted callers
            forced = getattr(message, "forced_decision", None)
            if forced:
                decision = PolicyDecision(forced)

            if decision == PolicyDecision.ALLOW:
                self._emit(
                    MessageBusType.TOOL_CONFIRMATION_RESPONSE,
                    ToolConfirmationResponse(
                        correlation_id=message.correlation_id,
                        confirmed=True,
                    ),
                )
            elif decision == PolicyDecision.DENY:
                self._emit(
                    MessageBusType.TOOL_POLICY_REJECTION,
                    ToolPolicyRejection(
                        tool_name=message.tool_name,
                        tool_args=message.tool_args,
                    ),
                )
                self._emit(
                    MessageBusType.TOOL_CONFIRMATION_RESPONSE,
                    ToolConfirmationResponse(
                        correlation_id=message.correlation_id,
                        confirmed=False,
                    ),
                )
            elif decision == PolicyDecision.ASK_USER:
                has_listeners = len(
                    self._listeners.get(
                        MessageBusType.TOOL_CONFIRMATION_REQUEST, []
                    )
                ) > 0
                if has_listeners:
                    self._emit(MessageBusType.TOOL_CONFIRMATION_REQUEST, message)
                else:
                    # No UI listener → deny with requires_user_confirmation flag
                    self._emit(
                        MessageBusType.TOOL_CONFIRMATION_RESPONSE,
                        ToolConfirmationResponse(
                            correlation_id=message.correlation_id,
                            confirmed=False,
                            requires_user_confirmation=True,
                        ),
                    )
        else:
            self._emit(msg_type, message)

    async def request(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        timeout_seconds: float = 60.0,
    ) -> ToolConfirmationResponse:
        """
        Request-response pattern: publish a confirmation request and wait
        for the correlated response.
        """
        correlation_id = str(uuid.uuid4())
        self._pending_correlation_id = correlation_id
        future: asyncio.Future[ToolConfirmationResponse] = asyncio.get_running_loop().create_future()

        def on_response(response: ToolConfirmationResponse):
            # Match exact correlation_id OR empty (broadcast respond)
            if not future.done() and (
                response.correlation_id == correlation_id
                or response.correlation_id == ""
            ):
                future.set_result(response)

        self.subscribe(MessageBusType.TOOL_CONFIRMATION_RESPONSE, on_response)

        try:
            await self.publish(
                ToolConfirmationRequest(
                    tool_name=tool_name,
                    tool_args=tool_args,
                    correlation_id=correlation_id,
                )
            )
            return await asyncio.wait_for(future, timeout=timeout_seconds)
        finally:
            self._pending_correlation_id = None
            self.unsubscribe(MessageBusType.TOOL_CONFIRMATION_RESPONSE, on_response)

    async def respond(self, confirmed: bool, correlation_id: Optional[str] = None) -> None:
        """
        UI side: respond to the current pending confirmation request.
        If correlation_id is None, uses the tracked pending ID (or broadcasts).
        """
        cid = correlation_id or getattr(self, "_pending_correlation_id", None) or ""
        response = ToolConfirmationResponse(
            correlation_id=cid,
            confirmed=confirmed,
        )
        self._emit(MessageBusType.TOOL_CONFIRMATION_RESPONSE, response)

