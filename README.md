# Claude Code Interceptor

A wrapper for Claude Code CLI that integrates with Anthropic-compatible endpoints.  Currently, you can use LiteLLM Proxy, Llama.cpp (with or w/o Llama Swap), vLLM.

LiteLLM Proxy allows you to use OpenAI Compatible endpoints, too.

```
Claude Code -> LiteLLM Proxy -> OpenAI Compatible
```

## Overview

Claude Code Interceptor acts as a middleware layer between you and the Claude Code CLI.  It allows you to quickly create configurations with different model providers and models - selecting models to replace Haiku, Sonnet and Opus - and save them for quick reuse later.  

Command line parameters are passed to Claude Code, except for --ccr-xxxx, which go to Claude Code Interceptor.

## Features

- **Multi-Provider Support**: Configure multiple model providers with different base URLs
- **Named Configurations**: Save and load named configurations for different use cases
- **Default Configuration**: Set a default configuration for seamless usage
- **Interactive TUI**: User-friendly terminal interface for configuration management
- **Seamless Integration**: Transparent pass-through to Claude Code CLI with environment variables
- **Model Selection**: Choose specific models for Haiku, Sonnet, and Opus variants
- **Provider Validation**: Automatic validation of providers by fetching available models
- **Configuration Tables**: Visual display of saved configurations with default indicators

## Installation

### Prerequisites

- uv: https://docs.astral.sh/uv/
- Claude Code CLI installed and accessible in your PATH

### Standard Installation

```bash
uv tool install git+https://github.com/eleqtrizit/Claude-Code-Interceptor
```


## Quick Start

1. **Configure providers and models**:
   ```bash
   cci --cci-config
   ```

2. **List available configurations**:
   ```bash
   cci --cci-list-configs
   ```

3. **Run Claude Code CLI with a specific configuration**:
   ```bash
   cci --cci-use-config myconfig
   ```

4. **Run Claude Code CLI with default configuration**:
   ```bash
   cci
   ```

### Development Installation

```bash
uv venv
uv synv
```

## Usage

### Basic Commands

```bash
# Run Claude Code CLI with default settings
cci

# Run Claude Code CLI with specific arguments
cci --help

# Show Claude Code Interceptor version
cci --cci-version

# Show help for Claude Code Interceptor
cci --cci-help
```

### Configuration Management

```bash
# Configure model providers and settings
cci --cci-config

# List saved configurations
cci --cci-list-configs

# Use a specific saved configuration
cci --cci-use-config CONFIG_NAME
```

### Practical Examples

```bash
# Configure a new provider (opens interactive TUI)
cci --cci-config

# List available configurations
cci --cci-list-configs

# Use a specific configuration with Claude CLI help
cci --cci-use-config my-config --help

# Run Claude Code CLI with a specific configuration
cci --cci-use-config my-config

# Set a configuration as default in the TUI
cci --cci-config  # Then select "Set Default Config"
```

## How It Works

Claude Code Interceptor intercepts calls to the Claude Code CLI and injects environment variables based on your selected configuration. This allows you to:

1. Define multiple model providers
2. Associate specific models with Haiku, Sonnet, and Opus variants
3. Save these associations as named configurations
4. Switch between configurations effortlessly

When you run `cci --cci-use-config my-config`, the interceptor:
1. Loads the specified configuration
2. Sets appropriate environment variables (ANTHROPIC_BASE_URL, ANTHROPIC_DEFAULT_HAIKU_MODEL, etc.)
3. Passes all remaining arguments to the Claude Code CLI
4. Displays the environment variables and command for transparency

## Development

### Setup

```bash
# Install dependencies
make install

# Run tests
make test

# Run tests with coverage
make cov

# Run linters
make lint

# Format code
make format
```

## Configuration Details

Configurations are stored in `~/.config/cci/config.json` and include:

- **Providers**: Named model providers with base URLs and available models
- **Models**: Specific model mappings for Haiku, Sonnet, and Opus variants
- **Configs**: Saved named configurations associating providers with model selections
- **Default Config**: The configuration to use when none is explicitly specified

Each configuration can specify:
- A provider to use for the base URL
- Specific models for Haiku, Sonnet, and Opus variants
- These settings are translated to environment variables when running the Claude CLI

## Environment Variables

Claude Code Interceptor sets the following environment variables based on your configuration:

- `ANTHROPIC_BASE_URL`: Base URL for the selected provider
- `ANTHROPIC_DEFAULT_HAIKU_MODEL`: Default model for Haiku variant
- `ANTHROPIC_DEFAULT_SONNET_MODEL`: Default model for Sonnet variant
- `ANTHROPIC_DEFAULT_OPUS_MODEL`: Default model for Opus variant

Note: If an AUTH_TOKEN exists in the environment, it will be unset when using a custom provider.


## License

MIT
