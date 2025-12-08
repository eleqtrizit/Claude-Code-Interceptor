# Changes Made to Remove "None" as Model Option

## Summary
Modified the configuration TUI to force users to select a valid model instead of allowing them to choose "None". This ensures that all configurations have valid model selections.

## Changes Made

### 1. Modified `cci/tui.py`

#### InquirerPromptHandler.select_model()
- Removed the "None" option from model selection
- Added a check for empty model lists, returning None with a warning message
- Forced users to select a valid model from the available options

#### TestPromptHandler.select_model()
- Removed the "None" option from model selection (numbered option 0)
- Changed numbering to start from 1 for actual models
- Added a check for empty model lists, returning None with a warning message
- Updated the selection logic to account for 1-based indexing

### 2. Updated `tests/test_tui.py`

#### TestInquirerPromptHandler
- Renamed `test_select_model_with_none` to `test_select_model_no_models_available`
- Updated the test to verify the new behavior when no models are available
- Added verification that a warning message is printed when no models are available

#### TestTestPromptHandler
- Renamed `test_select_model_with_none` to `test_select_model_no_models_available`
- Updated the test to verify the new behavior when no models are available
- Updated `test_select_model_with_selection` to account for 1-based indexing
- Added verification that a warning message is printed when no models are available

## Behavior Changes

### Before
- Users could select "None" for any model type (haiku, sonnet, opus)
- This allowed configurations with missing model specifications

### After
- Users must select a valid model from the available options
- If no models are available for a provider, the system shows a warning and returns None
- All configurations must have valid model selections

## Testing
- All 104 tests pass
- Updated tests verify the new behavior
- No regressions introduced