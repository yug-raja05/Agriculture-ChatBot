import logging
from app.ai.registry import ai_tool_registry

logger = logging.getLogger(__name__)

# Explicitly import all 13 tool modules to trigger decorators on startup
try:
    import app.ai.tools.weather
    import app.ai.tools.disease
    import app.ai.tools.crop
    import app.ai.tools.market
    import app.ai.tools.government
    import app.ai.tools.pdf
    import app.ai.tools.ocr
    import app.ai.tools.voice
    import app.ai.tools.yield_tool
    import app.ai.tools.fertilizer
    import app.ai.tools.notification
    import app.ai.tools.memory
    import app.ai.tools.image
    import app.ai.tools.translation
    import app.ai.tools.reminder
    import app.ai.tools.knowledge_base
    logger.info("Successfully loaded and registered all 15 modular AI tools.")
except Exception as e:
    logger.error(f"Error registering tool modules: {str(e)}")
