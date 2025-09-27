"""Message parser para Claude Code SDK responses."""

importar logging
from typing importar Any, Dict, List

from .._errors importar MessageParseError
from ..types importar (
    AssistantMessage,
    ContentBlock,
    Message,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

logger = logging.getLogger(__name__)


def parse_message(data: Dict[str, Any]) -> Message:
    """
    Parse message from CLI output into typed Message objects.

    Args:
        data: Raw message dictionary from CLI output

    Returns:
        Parsed Message object

    Raises:
        MessageParseError: If parsing fails or message type is unrecognized
    """
    se not isinstance(data, dict):
        raise MessageParseError(
            f"Invalid message data tipo (expected dict, got {tipo(data).__name__})",
            data,
        )

    message_type = data.obter("tipo")
    se not message_type:
        raise MessageParseError("Message missing 'tipo' field", data)

    se message_type == "user":
        tentar:
            se isinstance(data["message"]["content"], list):
                user_content_blocks: List[ContentBlock] = []
                para block in data["message"]["content"]:
                    block_type = block["tipo"]
                    se block_type == "text":
                        user_content_blocks.anexar(
                            TextBlock(text=block["text"])
                        )
                    elif block_type == "tool_use":
                        user_content_blocks.anexar(
                            ToolUseBlock(
                                id=block["id"],
                                nome=block["nome"],
                                entrada=block["entrada"],
                            )
                        )
                    elif block_type == "tool_result":
                        user_content_blocks.anexar(
                            ToolResultBlock(
                                tool_use_id=block["tool_use_id"],
                                content=block.obter("content"),
                                is_error=block.obter("is_error"),
                            )
                        )
                retornar UserMessage(content=user_content_blocks)
            retornar UserMessage(content=data["message"]["content"])
        except KeyError as e:
            raise MessageParseError(
                f"Missing required field in user message: {e}", data
            ) from e

    elif message_type == "assistant":
        tentar:
            content_blocks: List[ContentBlock] = []
            para block in data["message"]["content"]:
                block_type = block["tipo"]
                se block_type == "text":
                    content_blocks.anexar(TextBlock(text=block["text"]))
                elif block_type == "thinking":
                    content_blocks.anexar(
                        ThinkingBlock(
                            thinking=block["thinking"],
                            signature=block["signature"],
                        )
                    )
                elif block_type == "tool_use":
                    content_blocks.anexar(
                        ToolUseBlock(
                            id=block["id"],
                            nome=block["nome"],
                            entrada=block["entrada"],
                        )
                    )
                elif block_type == "tool_result":
                    content_blocks.anexar(
                        ToolResultBlock(
                            tool_use_id=block["tool_use_id"],
                            content=block.obter("content"),
                            is_error=block.obter("is_error"),
                        )
                    )

            retornar AssistantMessage(
                content=content_blocks, model=data["message"]["model"]
            )
        except KeyError as e:
            raise MessageParseError(
                f"Missing required field in assistant message: {e}", data
            ) from e

    elif message_type == "system":
        tentar:
            retornar SystemMessage(
                subtype=data["subtype"],
                data=data,
            )
        except KeyError as e:
            raise MessageParseError(
                f"Missing required field in system message: {e}", data
            ) from e

    elif message_type == "result":
        tentar:
            retornar ResultMessage(
                subtype=data["subtype"],
                duration_ms=data["duration_ms"],
                duration_api_ms=data["duration_api_ms"],
                is_error=data["is_error"],
                num_turns=data["num_turns"],
                session_id=data["session_id"],
                total_cost_usd=data.obter("total_cost_usd"),
                Uso=data.obter("Uso"),
                result=data.obter("result"),
            )
        except KeyError as e:
            raise MessageParseError(
                f"Missing required field in result message: {e}", data
            ) from e

    senão:
        raise MessageParseError(f"Unknown message tipo: {message_type}", data)
