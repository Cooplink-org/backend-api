from deep_translator import GoogleTranslator
from django.core.cache import cache
import hashlib
import structlog

logger = structlog.get_logger(__name__)

class TranslationService:
    LANGUAGE_MAP = {
        'uz': 'uzbek',
        'en': 'english', 
        'ru': 'russian'
    }
    
    @classmethod
    def translate_text(cls, text, target_language, source_language='auto'):
        if not text or not text.strip():
            return text
        
        cache_key = cls._get_cache_key(text, target_language, source_language)
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            target_lang = cls.LANGUAGE_MAP.get(target_language, target_language)
            source_lang = cls.LANGUAGE_MAP.get(source_language, source_language)
            
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            translated_text = translator.translate(text)
            
            cache.set(cache_key, translated_text, timeout=86400)  # 24 hours
            
            logger.info("Text translated successfully", 
                       source=source_language, target=target_language, 
                       original_length=len(text), translated_length=len(translated_text))
            
            return translated_text
            
        except Exception as e:
            logger.error("Translation failed", 
                        error=str(e), source=source_language, target=target_language)
            return text
    
    @classmethod
    def translate_to_all_languages(cls, text, source_language='en'):
        translations = {}
        for lang_code in cls.LANGUAGE_MAP.keys():
            if lang_code != source_language:
                translations[lang_code] = cls.translate_text(text, lang_code, source_language)
            else:
                translations[lang_code] = text
        return translations
    
    @classmethod
    def _get_cache_key(cls, text, target_language, source_language):
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"translation:{source_language}:{target_language}:{text_hash}"
