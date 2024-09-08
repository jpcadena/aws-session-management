"""
A module for security headers in the app.middlewares package.
"""

import logging
from secrets import token_urlsafe
from typing import Any

from fastapi import FastAPI, Request, Response
from pydantic import PositiveInt
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

logger: logging.Logger = logging.getLogger(__name__)


def generate_nonce(entropy: PositiveInt = 90) -> str:
    """
    Generates a secure nonce (number used once) for use in security contexts
    such as Content Security Policy (CSP) headers

    :param entropy: The amount of entropy (randomness) to use when generating
     the nonce.
    :type entropy: PositiveInt
    :return: A securely generated nonce string
    :rtype: str
    """
    return token_urlsafe(entropy)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to the response."""

    def __init__(
        self,
        app: FastAPI,
        csp_options: dict[str, Any] | None = None,
        script_nonce: bool = False,
        style_nonce: bool = False,
        report_only: bool = False,
    ) -> None:
        super().__init__(app)
        self.default_csp_options: dict[str, Any] = csp_options or {
            "default-src": ["'self'"],
            "base-uri": ["'self'"],
            "block-all-mixed-content": [],
            "font-src": ["'self'", "https:", "data:"],
            "frame-ancestors": ["'self'"],
            "img-src": ["'self'", "data:"],
            "object-src": ["'none'"],
            "script-src": ["'self'"],
            "script-src-attr": ["'none'"],
            "style-src": ["'self'", "https:", "'unsafe-inline'"],
            "upgrade-insecure-requests": [],
            "require-trusted-types-for": ["'script'"],
        }
        self.script_nonce: bool = script_nonce
        self.style_nonce: bool = style_nonce
        self.report_only: bool = report_only
        self.nonce: str | None = (
            generate_nonce() if (script_nonce or style_nonce) else None
        )
        self.swagger_csp_options: dict[str, list[str]] = {
            "default-src": ["'self'"],
            "script-src": [
                "'self'",
                "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui"
                "-bundle.js",
                "'sha256-swagger_sha_key'",
            ],
            "style-src": [
                "'self'",
                "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
            ],
            "img-src": ["'self'", "data:", "https:"],
            "font-src": ["'self'", "https:", "data:"],
            "connect-src": ["'self'", "https:"],
            "frame-ancestors": ["'none'"],
        }

    def _construct_csp_header(
        self, csp_options: dict[str, Any]
    ) -> tuple[str, str]:
        """
        Constructs the Content Security Policy header.

        :param csp_options: The CSP options to construct the header
        :type csp_options: dict[str, Any]
        :return: A tuple containing the header name and the constructed CSP
         string
        :rtype: tuple[str, str]
        """
        header_name: str = (
            "Content-Security-Policy"
            if not self.report_only
            else "Content-Security-Policy-Report-Only"
        )
        csp_directives: list[str] = []
        for directive, sources in csp_options.items():
            if directive in ["script-src", "style-src"]:
                sources = sources.copy()
                if directive == "script-src" and self.script_nonce:
                    sources.append(f"'nonce-{self.nonce}'")
                if directive == "style-src" and self.style_nonce:
                    sources.append(f"'nonce-{self.nonce}'")
            csp_directives.append(f"{directive} {' '.join(sources)}")
        return header_name, "; ".join(csp_directives)

    def _add_security_headers(
        self,
        response: Response,
        max_age: PositiveInt,
        csp_options: dict[str, Any],
        ct_max_age: PositiveInt,
    ) -> None:
        """
        Adds security headers to the response.

        :param max_age: The maximum age for the strict transport security
        :type max_age: PositiveInt
        :param response: The FastAPI response instance
        :type response: Response
        :param csp_options: The content security policy options to apply
        :type csp_options: dict[str, Any]
        :param ct_max_age: The max age for the certificate transparency
        :type ct_max_age: PositiveInt
        :return: None
        :rtype: NoneType
        """
        if "Access-Control-Allow-Origin" not in response.headers:
            response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Strict-Transport-Security"] = (
            f"max-age={max_age}; includeSubDomains; preload"
        )
        response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(self), "
            "microphone=(), "
            "camera=(), "
            "fullscreen=(self), "
            "accelerometer=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "payment=(), "
            "usb=()"
        )
        response.headers["Cache-Control"] = "no-cache"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-DNS-Prefetch-Control"] = "off"
        response.headers["X-Download-Options"] = "noopen"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Expect-CT"] = f"max-age={ct_max_age}, enforce"
        csp_header_name, csp_header_value = self._construct_csp_header(
            csp_options
        )
        response.headers[csp_header_name] = csp_header_value

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Dispatch the request with the security headers added to the response.

        :param request: The HTTP request to be dispatched.
        :type request: Request
        :param call_next: The call_next middleware function.
        :type call_next: RequestResponseEndpoint
        :return: The response with the security headers added.
        :rtype: Response
        """
        response: Response = await call_next(request)
        max_age: PositiveInt = (
            request.app.state.settings.STRICT_TRANSPORT_SECURITY_MAX_AGE
        )
        ct_max_age: PositiveInt = (
            request.app.state.settings.CERTIFICATE_TRANSPARENCY_MAX_AGE
        )
        if request.url.path.startswith("/docs") or request.url.path.startswith(
            "/redoc"
        ):
            csp_options = self.swagger_csp_options.copy()
            swagger_sha_key: str = request.app.state.settings.SWAGGER_SHA_KEY
            csp_options["script-src"] = [
                "'self'",
                "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui"
                "-bundle.js",
                f"'sha256-{swagger_sha_key}'",
            ]
            logger.info("Applying Swagger UI specific CSP with dynamic SHA key")
        else:
            csp_options = self.default_csp_options
            logger.info("Applying default CSP")
        self._add_security_headers(response, max_age, csp_options, ct_max_age)
        return response
