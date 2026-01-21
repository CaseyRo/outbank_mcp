#!/usr/bin/env python3
"""Generate a secure authentication token and copy it to clipboard.

This script generates a token that meets security requirements:
- Minimum 16 characters (enforced)
- Recommended 32+ characters (default: 32 bytes = ~43 URL-safe base64 chars)
- 128+ bits of entropy (meets OWASP, OAuth/RFC 6750, NIST guidelines)
"""

import re
import secrets
import subprocess
import sys
from pathlib import Path


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard. Supports macOS, Linux, and Windows."""
    try:
        # macOS
        if sys.platform == "darwin":
            process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, close_fds=True)
            process.communicate(input=text.encode("utf-8"))
            return process.returncode == 0

        # Linux (requires xclip or xsel)
        elif sys.platform.startswith("linux"):
            try:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text.encode("utf-8"),
                    check=True,
                )
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    subprocess.run(
                        ["xsel", "--clipboard", "--input"],
                        input=text.encode("utf-8"),
                        check=True,
                    )
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return False

        # Windows
        elif sys.platform == "win32":
            subprocess.run(
                ["clip"],
                input=text.encode("utf-8"),
                check=True,
            )
            return True

        return False
    except Exception:
        return False


def update_env_file(token: str, env_path: Path) -> bool:
    """Update or add MCP_HTTP_AUTH_TOKEN in .env file."""
    try:
        if not env_path.exists():
            return False

        # Read current content
        content = env_path.read_text(encoding="utf-8")

        # Pattern to match MCP_HTTP_AUTH_TOKEN line (with or without value)
        pattern = r"^MCP_HTTP_AUTH_TOKEN=.*$"

        # Check if token line exists
        if re.search(pattern, content, re.MULTILINE):
            # Replace existing line
            new_content = re.sub(
                pattern,
                f"MCP_HTTP_AUTH_TOKEN={token}",
                content,
                flags=re.MULTILINE,
            )
        else:
            # Add new line (find HTTP transport settings section or append at end)
            http_section_pattern = r"(# HTTP transport settings.*?\nMCP_HOST=.*?\n)"
            if re.search(http_section_pattern, content, re.MULTILINE | re.DOTALL):
                # Insert after MCP_HOST line
                new_content = re.sub(
                    r"(MCP_HOST=.*?\n)",
                    rf"\1MCP_HTTP_AUTH_TOKEN={token}\n",
                    content,
                    flags=re.MULTILINE,
                )
            else:
                # Append at end
                new_content = content.rstrip() + f"\nMCP_HTTP_AUTH_TOKEN={token}\n"

        # Write back
        env_path.write_text(new_content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Error updating .env file: {e}", file=sys.stderr)
        return False


def main():
    """Generate secure token and copy to clipboard."""
    # Find project root (where .env.example should be)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    env_path = project_root / ".env"

    # Generate token with 32 bytes (256 bits) of entropy
    # token_urlsafe encodes to URL-safe base64, resulting in ~43 characters
    token = secrets.token_urlsafe(32)

    print("Generated secure authentication token:")
    print(f"  Length: {len(token)} characters")
    print("  Entropy: ~256 bits (exceeds OWASP/NIST recommendations)")
    print("\nToken:")
    print(f"  {token}")

    # Copy to clipboard
    clipboard_success = copy_to_clipboard(token)
    if clipboard_success:
        print("\n✅ Token copied to clipboard!")
    else:
        print("\n⚠️  Could not copy to clipboard automatically.")
        print("   Please copy the token above manually.")

    # Ask if user wants to add to .env
    print("\n📝 Add token to .env file?")
    if env_path.exists():
        print(f"   Found: {env_path}")
        response = input("   (y/n, default: n): ").strip().lower()
        if response in ("y", "yes"):
            if update_env_file(token, env_path):
                print(f"   ✅ Token added to {env_path}")
            else:
                print(f"   ❌ Failed to update {env_path}")
                print("   Please add manually:")
                print(f"     MCP_HTTP_AUTH_TOKEN={token}")
    else:
        print(f"   .env file not found at {env_path}")
        print("   Copy .env.example to .env first, then run this script again.")
        print("\n   Or add manually to your .env file:")
        print(f"     MCP_HTTP_AUTH_TOKEN={token}")


if __name__ == "__main__":
    main()
