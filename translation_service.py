from deep_translator import GoogleTranslator


class TranslationService:
    def __init__(self, default_lang="en"):
        self.default_lang = default_lang

    def translate_text(self, text, target_lang):
        if not text or target_lang == self.default_lang:
            return text

        try:
            return GoogleTranslator(
                source="auto",
                target=target_lang
            ).translate(text)
        except Exception as e:
            print("Translation error:", e)
            return text

    def translate_list(self, texts, target_lang):
        return [
            self.translate_text(t, target_lang)
            for t in texts
        ]
