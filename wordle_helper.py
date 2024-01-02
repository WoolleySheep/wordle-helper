import enum
import string


class Letter:
    def __init__(self, text: str) -> None:
        if len(text) != 1 or not text.isalpha():
            raise ValueError("Invalid text")

        self._text = text.lower()

    def __str__(self) -> str:
        return self._text

    def __repr__(self) -> str:
        return f"letter({self._text})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Letter):
            raise NotImplementedError

        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(self._text)


ALL_LETTERS = {Letter(char) for char in string.ascii_lowercase}


class Word:
    @classmethod
    def from_string(cls, text: str, /) -> "Word":
        if len(text) != 5:
            raise ValueError("Invalid text")

        return cls(
            first=Letter(text[0]),
            second=Letter(text[1]),
            third=Letter(text[2]),
            fourth=Letter(text[3]),
            fifth=Letter(text[4]),
        )

    def __init__(
        self,
        first: Letter,
        second: Letter,
        third: Letter,
        fourth: Letter,
        fifth: Letter,
    ) -> None:
        self.first = first
        self.second = second
        self.third = third
        self.fourth = fourth
        self.fifth = fifth

    def __str__(self) -> str:
        return f"{self.first}{self.second}{self.third}{self.fourth}{self.fifth}"

    def __hash__(self) -> int:
        return hash((self.first, self.second, self.third, self.fourth, self.fifth))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Word):
            raise NotImplementedError

        return (
            self.first == other.first
            and self.second == other.second
            and self.third == other.third
            and self.fourth == other.fourth
            and self.fifth == other.fifth
        )

    def __repr__(self) -> str:
        return f"word({self})"


class Outcome(enum.Enum):
    CORRECT_SPOT = enum.auto()
    WRONG_SPOT = enum.auto()
    NOT_IN_WORD = enum.auto()


class LetterOutcome:
    def __init__(self, letter: Letter, outcome: Outcome) -> None:
        self.letter = letter
        self.outcome = outcome


class GuessOutcome:
    def __init__(
        self,
        first: LetterOutcome,
        second: LetterOutcome,
        third: LetterOutcome,
        fourth: LetterOutcome,
        fifth: LetterOutcome,
    ) -> None:
        self.first = first
        self.second = second
        self.third = third
        self.fourth = fourth
        self.fifth = fifth

    def __str__(self) -> str:
        return f"{self.first or '?'}{self.second or '?'}{self.third or '?'}{self.fourth or '?'}{self.fifth or '?'}"

class LetterOptions:

    def __init__(self) -> None:
        self.possible_options = ALL_LETTERS.copy()
        self.wrong_spot_options = set[Letter]()

    def discard_possible_option(self, letter: Letter, /) -> None:
        self.possible_options.remove(letter)

    def discard_wrong_spot_option(self, letter: Letter, /) -> None:
        self.wrong_spot_options.remove(letter)

class WordProgress:
    def __init__(self) -> None:
        self.first: Letter | LetterOptions = LetterOptions()
        self.second: Letter | LetterOptions = LetterOptions()
        self.third: Letter | LetterOptions = LetterOptions()
        self.fourth: Letter | LetterOptions = LetterOptions()
        self.fifth: Letter | LetterOptions = LetterOptions()

    def nunknown_letters(self) -> int:
        count = 0
        if isinstance(self.first, Letter):
            count += 1
        if isinstance(self.second, Letter):
            count += 1
        if isinstance(self.third, Letter):
            count += 1
        if isinstance(self.fourth, Letter):
            count += 1
        if isinstance(self.fifth, Letter):
            count += 1
        return count

    def update(self, outcome: GuessOutcome) -> None:
        raise NotImplementedError
    
    def _found_letter_not_in_word(self, letter: Letter) -> None:
        if isinstance(self.first, LetterOptions):
            self.first.discard_possible_option(letter)
        if isinstance(self.second, LetterOptions):
            self.second.discard_possible_option(letter)
        if isinstance(self.third, LetterOptions):
            self.third.discard_possible_option(letter)
        if isinstance(self.fourth, LetterOptions):
            self.fourth.discard_possible_option(letter)
        if isinstance(self.fifth, LetterOptions):
            self.fifth.discard_possible_option(letter)

    def _found_letter_wrong_spot(self, letter: Letter) -> None:


    def is_possible_match(self, word: Word) -> bool:
        if isinstance(self.first, Letter):
            if word.first != self.first:
                return False
        elif word.first not in self.first:
            return False

        if isinstance(self.second, Letter):
            if word.second != self.second:
                return False
        elif word.second not in self.second:
            return False

        if isinstance(self.third, Letter):
            if word.third != self.third:
                return False
        elif word.third not in self.third:
            return False

        if isinstance(self.fourth, Letter):
            if word.fourth != self.fourth:
                return False
        elif word.fourth not in self.fourth:
            return False

        if isinstance(self.fifth, Letter):
            if word.fifth != self.fifth:
                return False
        elif word.fifth not in self.fifth:
            return False

        return True
