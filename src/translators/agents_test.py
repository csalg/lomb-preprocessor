import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from translators.agents import GoogleTranslateAgent

buffer = """
Sejrssikker Biden talte til amerikanerne: Tallene viser, at vi vinder
Af Kevin AhrensI dag kl. 06:03 | opdateret 6 min. sidenForklar ordStørre TekstLæs op
3-4 minutes

- Vi vinder valget.

Sådan lød det fra demokraternes præsidentkandidat, Joe Biden, da han klokken 04.50 dansk tid gik på talerstolen i hjemstaten Delaware.

- Vi vinder valget med et klart mandat og med nationen bag os. Vi har fået flere end 74 millioner stemmer. Det er mere end nogen anden præsidentkandidat nogensinde har fået i USA’s historie. Og det tal vokser stadig, siger Joe Biden.

Joe Biden skulle egentlig have holdt sin tale omkring klokken 2 dansk tid, hvilket svarer til klokken 20 på den amerikanske østkyst, men den blev - ligesom meget andet ved det her valg - forsinket.

Han havde nok håbet på, at han kunne erklære sig som vinder af valget, inden amerikanerne gik i seng, men sådan gik det ikke, siger DR's USA-korrespondent Steffen Kretz.

- Det lykkedes ikke, og så valgte man at gå ud og holde en tale, hvor man igen siger, "vi er på vej til at sejre, og det her er, hvad vi er i gang med, og hvordan vores kommende regering skal se ud."

Ifølge Joe Biden tyder det dog på, at han får flere end 300 valgmænd, når alle stemmerne er talt op.

I skrivende stund fører han både i Georgia, Nevada, Pennsylvania og Arizona.

Du kan se hele Joe Bidens tale nederst i artiklen.

Skal være tålmodige

Joe Biden lagde da heller ikke skjul på, at ventetiden efterhånden har været lang.

Men i sidste ende handler det om at lade tingene gå sin gang og bevare både tålmodigheden og roen, siger han.

- Jeres stemmer vil tælle med, og jeg er ligeglad med, hvor meget nogle folk forsøger at standse det. Jeg vil ikke lade det ske.

Inden da havde præsident Donald Trump advaret sin modstander mod at erklære sejr ved talen.

- Joe Biden bør ikke uretmæssigt gøre krav på præsidentembedet. Jeg kunne stille samme krav. Retlige procedurer er kun lige ved at begynde, tweetede præsidenten.

Ligesom ved Joe Bidens tale i går, understregede han, at det nu handler om at forene USA, så man kan komme i gang med at løse landets udfordringer, fortæller Steffen Kretz.

- Hans vigtigste budskab var, at tidspunktet nu med coronavirus, økonomisk krise og så videre, er så vigtigt, at han vil kæmpe for at overvinde fjendskabet, der har været mellem partierne. Han sagde, at amerikanerne nu har brug for, at alle arbejder sammen på tværs af partiskel.

Joe Biden fortalte i bund og grund, at han er ved at overtage ansvaret og ledelsen af USA, siger Steffen Kretz.

- Biden lod forstå, at han og vicepræsidentkandidat Kamala Harris er i fuld gang med transitionen - altså fordelingen af poster i deres kommende regering og Det Hvide Hus, og at de holder møder med sundhedseksperter for at lægge en plan for håndteringen af Corona pandemien

Se hele talen i videoen her:
"""

def __test_google_translate():
    agent = GoogleTranslateAgent("dk", "en")
    agent.start()
    translated_buffer = agent.translate_buffer(buffer)
    agent.close()
    assert translated_buffer