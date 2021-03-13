import logging
import re

log = logging.getLogger(__name__)


def prepare_title(title: str) -> str:
    """Clean track title for better search results."""
    title = unicode_replace(title)
    # remove anything in brackets
    clean_title = re.sub(r"\([^)]*\)", "", title.lower())
    # remove special characters
    clean_title = re.sub(r"['()!?,.\"]", "", clean_title)
    # remove white spaces and decapitalize
    clean_title = clean_title.lower().strip()
    return clean_title


def prepare_artist(artist: str) -> str:
    """Clean track artist name for better search results."""
    artist = unicode_replace(artist)
    # remove "the", "orchestra"
    clean_artist = re.sub(r"(^the\s|\sorchestra)", "", artist.lower())
    # use only the first artist name
    clean_artist = re.split(r"(,|&|and|with|featuring)\s", clean_artist)[0]
    # remove special characters
    clean_artist = re.sub(r"['-.+]", "", clean_artist)
    # remove white spaces and decapitalize
    clean_artist = clean_artist.lower().strip()
    # fix known exceptions
    substitutions = {
        "pink": "p!nk",
        "asap rocky": "a$ap rocky",
        "asap ferg": "a$ap ferg",
        "cash out": "ca$h out",
        "lady antebellum": "lady a",
        "soulja boy tell 'em": "soulja boy",
        "'n sync": "*nsync",
        "young jeezy": "jeezy",
        "puff daddy": "diddy",
        "p. diddy": "diddy",
        "98 degrees": "98",
        "john cougar mellencamp": "john mellencamp",
        "john cougar": "john mellencamp",
        "the b52s": "the b-52's",
        "los del río": "los del rio",
        "mills brors": "the mills brothers",
        "bobby valentino": "bobby v.",
        "ssgt barry sadler": "sgt barry sadler",
        "matchbox 20": "matchbox twenty",
        "dixie chicks": "chicks",
    }
    if clean_artist in substitutions.keys():
        clean_artist = substitutions[clean_artist]
    return clean_artist


def unicode_replace(s: str) -> str:
    s = re.sub(u"\u00e9", "e", s)
    s = re.sub(u"\u00ed", "i", s)
    s = re.sub(u"\u00e1", "i", s)
    s = re.sub(u"\u2013", "", s)
    s = re.sub(u"\u00fd", "y", s)
    s = re.sub(u"\u00f3", "o", s)
    s = re.sub(u"\u00ff", "y", s)
    return s
