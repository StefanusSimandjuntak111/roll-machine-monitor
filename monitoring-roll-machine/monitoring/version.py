"""
Version configuration for Roll Machine Monitor application.
"""

# Application version
VERSION = "1.3.2"
VERSION_STRING = f"v{VERSION}"

# Build information
BUILD_DATE = "2024-01-XX"
BUILD_TYPE = "Release"

# Application information
APP_NAME = "Roll Machine Monitor"
APP_DESCRIPTION = "Enhanced Monitor untuk mesin roll kain dengan auto-send dan real-time display"
APP_AUTHOR = "Textilindo Team"
APP_WEBSITE = "https://github.com/StefanusSimandjuntak111/roll-machine-monitor"

def get_version_info():
    """Get complete version information."""
    return {
        'version': VERSION,
        'version_string': VERSION_STRING,
        'build_date': BUILD_DATE,
        'build_type': BUILD_TYPE,
        'app_name': APP_NAME,
        'app_description': APP_DESCRIPTION,
        'app_author': APP_AUTHOR,
        'app_website': APP_WEBSITE
    }

def get_version_string():
    """Get version string."""
    return VERSION_STRING

def get_full_version_info():
    """Get full version information as string."""
    info = get_version_info()
    return f"{info['app_name']} {info['version_string']} ({info['build_type']}) - {info['build_date']}" 