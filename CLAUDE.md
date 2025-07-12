# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Whisper Input is a Python-based voice transcription tool that enables real-time speech-to-text conversion using keyboard shortcuts. The application supports two transcription services:

- **Groq Whisper Large V3 Turbo** - Fast transcription via Groq API
- **SiliconFlow SenseVoiceSmall** - Even faster transcription with automatic punctuation via SiliconFlow API

### Core Functionality

- **Option/Alt key**: Multi-language voice transcription
- **Shift + Option/Alt**: Chinese to English translation
- Real-time audio recording and processing
- Automatic clipboard insertion with original content restoration
- Cross-platform support (macOS/Windows)

## Architecture

### Main Components

```
main.py                    # Entry point and VoiceAssistant orchestration
control_ui.py             # GUI control interface (not currently used in main flow)
src/
├── audio/
│   └── recorder.py       # AudioRecorder class for microphone input
├── keyboard/
│   ├── listener.py       # KeyboardManager for hotkey detection and text input
│   └── inputState.py     # UI state management for recording/processing status
├── transcription/
│   ├── whisper.py        # WhisperProcessor for Groq API integration
│   └── senseVoiceSmall.py # SenseVoiceSmallProcessor for SiliconFlow API
├── llm/
│   ├── symbol.py         # SymbolProcessor for punctuation enhancement
│   └── translate.py      # TranslateProcessor for translation services
└── utils/
    ├── logger.py         # Centralized logging configuration
    ├── clipboard.py      # Cross-platform clipboard management
    └── notifications.py  # macOS native notification system
```

### Key Classes

- **VoiceAssistant** (main.py:28): Main orchestrator that coordinates audio recording, transcription, and text input
- **AudioRecorder** (src/audio/recorder.py): Handles microphone recording using sounddevice
- **KeyboardManager** (src/keyboard/listener.py): Manages hotkey detection and native notification display
- **ClipboardManager** (src/utils/clipboard.py): Cross-platform clipboard operations with osascript/pyperclip
- **NotificationManager** (src/utils/notifications.py): macOS native notifications and system sounds
- **WhisperProcessor** (src/transcription/whisper.py): Groq API client for Whisper transcription
- **SenseVoiceSmallProcessor** (src/transcription/senseVoiceSmall.py): SiliconFlow API client for SenseVoice transcription

## Development Commands

### Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt
```

### Running the Application

```bash
# Run the main application
python main.py
```

### Configuration

Copy `.env.example` to `.env` and configure:

- Set `SERVICE_PLATFORM=siliconflow` or `SERVICE_PLATFORM=groq`
- Add appropriate API keys (`SILICONFLOW_API_KEY` or `GROQ_API_KEY`)
- Configure platform-specific settings (`SYSTEM_PLATFORM=mac` or `SYSTEM_PLATFORM=win`)

## Important Environment Variables

### Required Configuration

- `SERVICE_PLATFORM`: Choose transcription service (`siliconflow`/`groq`)
- `SYSTEM_PLATFORM`: Target platform (`mac`/`win`)
- `TRANSCRIPTIONS_BUTTON`: Recording hotkey (default: `alt`)
- `TRANSLATIONS_BUTTON`: Translation modifier (default: `shift`)

### API Keys

- `SILICONFLOW_API_KEY`: For SiliconFlow SenseVoice service
- `GROQ_API_KEY`: For Groq Whisper service

### Feature Toggles

- `CONVERT_TO_SIMPLIFIED`: Convert traditional to simplified Chinese (`true`/`false`)
- `ADD_SYMBOL`: Add punctuation to transcribed text (`true`/`false`)
- `OPTIMIZE_RESULT`: Experimental result optimization (`true`/`false`)
- `KEEP_ORIGINAL_CLIPBOARD`: Restore original clipboard after text insertion (`true`/`false`)

## Permission Requirements

### macOS

- **Microphone Access**: Required for audio recording
- **Accessibility Access**: Required for keyboard monitoring and text input
- **Input Monitoring**: Required for global hotkey detection

The application provides detailed permission setup instructions on first run if permissions are missing.

## Code Patterns

### Native macOS Integration

- macOS notification center for non-intrusive status updates
- System sound feedback for different events (Pop/Glass/Basso/Funk)
- osascript integration for clipboard and notifications
- Automatic platform detection (macOS vs Windows/Linux)

### Error Handling

- Service-specific error handling in transcription processors
- Timeout decorators for API calls (20-second default)
- Permission checking with user-friendly error messages
- Audio length validation (minimum 1 second recording)

### State Management

- Centralized state management in KeyboardManager
- Native macOS notifications for recording/processing status
- Automatic state reset on errors or short recordings

### Audio Processing

- In-memory audio buffering (no temporary files)
- 16kHz sampling rate for optimal transcription quality
- Real-time recording start/stop via hotkey detection

### Clipboard Protection

- ClipboardContext manager prevents pollution of user's clipboard
- Automatic backup and restore of original clipboard content
- Cross-platform clipboard operations (osascript for macOS, pyperclip for others)

## Dependencies

Key dependencies managed in `requirements.in`:

- `pynput`: Cross-platform keyboard/mouse input control
- `sounddevice`/`soundfile`: Audio recording and processing
- `openai`: Groq API client
- `httpx`: SiliconFlow API requests
- `python-dotenv`: Environment variable management
- `pyqt5`: GUI framework (for future UI components)
- `pyperclip`: Clipboard manipulation
- `opencc-python-reimplemented`: Traditional/Simplified Chinese conversion

## Testing

No test framework is currently configured. The application is tested manually through:

1. Hotkey activation testing
2. Audio recording verification
3. API transcription validation
4. Text input functionality testing
