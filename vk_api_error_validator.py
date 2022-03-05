from typing import TYPE_CHECKING, Any, NoReturn, Union, Dict, Type
import asyncio

from vkbottle import ABCResponseValidator
from vkbottle.modules import logger

if TYPE_CHECKING:
    from vkbottle.api import ABCAPI, API


class VKAPIErrorResponseValidator(ABCResponseValidator):
    """Default vk api error response validator
    Documentation: https://github.com/vkbottle/vkbottle/blob/master/docs/low-level/api/response-validator.md
    """

    async def validate(
            self,
            method: str,
            data: dict,
            response: Any,
            ctx_api: Union["ABCAPI", "API"],
    ) -> Union[Any, NoReturn]:
        if "error" not in response:
            if "response" not in response:
                # invalid response, just igrnore it
                return response
            elif isinstance(response["response"], list):
                errors = [item["error"] for item in response["response"] if "error" in item]
                if errors:
                    logger.debug(
                        f"{len(errors)} API error(s) in response wasn't handled: {errors}"
                    )
            return response

        if ctx_api.ignore_errors:
            return None

        error = response["error"]
        if 'error_code' not in error:
            return response
        code = error["error_code"]

        if code == 6:
            error.pop("error_code")
            await asyncio.sleep(5)
            return await ctx_api.request(
                method, {**data}
            )

        return response
