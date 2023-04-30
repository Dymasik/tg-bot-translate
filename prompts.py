from langchain.prompts import PromptTemplate

word = PromptTemplate(
    input_variables=["word"],
    template="""You are professional translator. Translate a word from Ukrainian to English.

    Word: Привіт
    Translation: Hello

    Word: {word}
    Translation:
    """,
)

word_transcription = PromptTemplate(
    input_variables=["word"],
    template="""You are professional translator. Translate a word from Ukrainian to English and provide transcription.

    Word: Привіт
    Translation: Hello [hə'ləʊ]

    Word: {word}
    Translation:
    """,
)

word_synonym = PromptTemplate(
    input_variables=["word"],
    template="""You are professional translator. Translate a word from Ukrainian to English, provide several possible translations.

    Word: Привіт
    Translation: Hello, Hi, Hey

    Word: {word}
    Translation:
    """,
)

word_synonym_explenation = PromptTemplate(
    input_variables=["word"],
    template="""You are professional translator. Translate a word from Ukrainian to English, provide several possible translations and explain when is better to use each.

    Word: Привіт
    Translation: Hi - better to use in friendly, informal situation
    Good Afternoon - better to use in formal situation

    Word: {word}
    Translation:
    """,
)

text = PromptTemplate(
    input_variables=["text"],
    template="""You are professional translator. Translate a text from Ukrainian to English.

    Text: Привіт, як в тебе справи? Чи добре ти доїхав вчора?
    Translation: Hi, how are you? Was the trip good yesterday? 

    Text: {text}
    Translation:
    """,
)

text_style = PromptTemplate(
    input_variables=["text", "style"],
    template="""You are professional translator. Translate a text from Ukrainian to English taking into account text style.

    Text: Привіт, як в тебе справи? Чи добре ти доїхав вчора?
    Style: Friendly
    Translation: Hi, how are you? Was the trip good yesterday? 

    Text: {text}
    Style: {style}
    Translation:
    """,
)