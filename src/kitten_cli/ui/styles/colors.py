from textual.theme import Theme

# Based on gemini-cli's semantic-colors and darkTheme
gemini_dark_theme = Theme(
    name="gemini-dark",
    primary="#87AFFF",       # AccentBlue (Active state, links)
    secondary="#D7AFFF",     # AccentPurple
    accent="#87D7D7",        # AccentCyan
    foreground="#FFFFFF",    # Foreground (Primary text)
    background="#000000",    # Background
    surface="#5F5F5F",       # InputBackground / MessageBackground
    panel="#5F5F5F",         # Panel backgrounds
    dark=True,
    variables={
        "gray": "#AFAFAF",
        "dark-gray": "#878787",
        "accent-green": "#D7FFD7",
        "accent-yellow": "#FFFFAF",
        "accent-red": "#FF87AF",
        "success": "#D7FFD7",
        "warning": "#FFFFAF",
        "error": "#FF87AF",
        "diff-added": "#005F00",
        "diff-removed": "#5F0000",
        "focus-background": "#005F00"
    }
)
