import enum
import itertools
import string
from collections.abc import Generator, Sequence
from typing import Self

from allowed_guesses import ALLOWED_GUESSES


class Position(enum.Enum):
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"
    FOURTH = "fourth"
    FIFTH = "fifth"


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

    def __lt__(self, other: Self) -> bool:
        if not isinstance(other, Letter):
            raise NotImplementedError

        return str(self) < str(other)

    def __hash__(self) -> int:
        return hash(self._text)


ALL_LETTERS = {Letter(char) for char in string.ascii_lowercase}


class Word:
    @staticmethod
    def is_valid_text(text: str) -> bool:
        return len(text) == 5 and all(char.isalpha() for char in text)

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

    def __iter__(self) -> Generator[Letter, None, None]:
        yield self.first
        yield self.second
        yield self.third
        yield self.fourth
        yield self.fifth

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Word):
            raise NotImplementedError

        return all(l1 == l2 for l1, l2 in zip(self, other))

    def __lt__(self, other: Self) -> bool:
        if not isinstance(other, Word):
            raise NotImplementedError

        return str(self) < str(other)

    def __str__(self) -> str:
        return "".join(str(letter) for letter in self)

    def __hash__(self) -> int:
        return hash((self.first, self.second, self.third, self.fourth, self.fifth))

    def __repr__(self) -> str:
        return f"word({self})"


class Result(enum.Enum):
    CORRECT_SPOT = enum.auto()
    WRONG_SPOT = enum.auto()
    NOT_IN_WORD = enum.auto()


def map_text_to_result(text: str) -> Result:
    match text:
        case "C":
            return Result.CORRECT_SPOT
        case "B":
            return Result.WRONG_SPOT
        case "A":
            return Result.NOT_IN_WORD

    raise ValueError("Invalid text")


class LetterGuess:
    def __init__(self, letter: Letter, result: Result) -> None:
        self.letter = letter
        self.result = result


class WordGuess:
    @classmethod
    def from_word_and_guesses(
        cls, word: Word, results: Sequence[Result]
    ) -> "WordGuess":
        if len(results) != 5:
            raise ValueError("Invalid guesses length")

        return cls(
            first=LetterGuess(word.first, results[0]),
            second=LetterGuess(word.second, results[1]),
            third=LetterGuess(word.third, results[2]),
            fourth=LetterGuess(word.fourth, results[3]),
            fifth=LetterGuess(word.fifth, results[4]),
        )

    def __init__(
        self,
        first: LetterGuess,
        second: LetterGuess,
        third: LetterGuess,
        fourth: LetterGuess,
        fifth: LetterGuess,
    ) -> None:
        self.first = first
        self.second = second
        self.third = third
        self.fourth = fourth
        self.fifth = fifth

    def __iter__(self) -> Generator[LetterGuess, None, None]:
        yield self.first
        yield self.second
        yield self.third
        yield self.fourth
        yield self.fifth


class GameProgress:
    def __init__(self) -> None:
        self.first: Letter | set[Letter] = ALL_LETTERS.copy()
        self.second: Letter | set[Letter] = ALL_LETTERS.copy()
        self.third: Letter | set[Letter] = ALL_LETTERS.copy()
        self.fourth: Letter | set[Letter] = ALL_LETTERS.copy()
        self.fifth: Letter | set[Letter] = ALL_LETTERS.copy()

        self.must_include: set[Letter] = set()

    def __iter__(self) -> Generator[Letter | set[Letter], None, None]:
        yield self.first
        yield self.second
        yield self.third
        yield self.fourth
        yield self.fifth

    def update(self, guess: WordGuess) -> None:
        def update_correct_letter(
            self: Self, position: Position, letter: Letter
        ) -> None:
            match position:
                case Position.FIRST:
                    self.first = letter
                case Position.SECOND:
                    self.second = letter
                case Position.THIRD:
                    self.third = letter
                case Position.FOURTH:
                    self.fourth = letter
                case Position.FIFTH:
                    self.fifth = letter

            if letter in self.must_include:
                self.must_include.remove(letter)

        def update_letter_in_wrong_spot(
            self: Self, position: Position, letter: Letter
        ) -> None:
            match position:
                case Position.FIRST:
                    if isinstance(self.first, set):
                        self.first.remove(letter)
                case Position.SECOND:
                    if isinstance(self.second, set):
                        self.second.remove(letter)
                case Position.THIRD:
                    if isinstance(self.third, set):
                        self.third.remove(letter)
                case Position.FOURTH:
                    if isinstance(self.fourth, set):
                        self.fourth.remove(letter)
                case Position.FIFTH:
                    if isinstance(self.fifth, set):
                        self.fifth.remove(letter)

            for options in self:
                if isinstance(options, set):
                    continue

                if letter == options:
                    return

            self.must_include.add(letter)

        def update_letter_is_not_in_word(self: Self, letter: Letter) -> None:
            for letter_options in self:
                if isinstance(letter_options, Letter):
                    continue

                if letter in letter_options:
                    letter_options.remove(letter)

        def collapse_must_include(self: Self) -> None:
            def collapse_letter(self: Self, letter: Letter) -> None:
                """If a must-include letter can fit only one place, set it."""
                valid_position: Position | None = None
                for position, options in zip(Position, self):
                    if isinstance(options, Letter):
                        continue

                    if letter in options:
                        if valid_position:
                            return
                        valid_position = position

                if valid_position:
                    update_correct_letter(self, valid_position, letter)

            while True:
                initial_must_include = self.must_include.copy()
                for letter in initial_must_include:
                    collapse_letter(self, letter)
                if initial_must_include == self.must_include:
                    break

        for position, letter_guess in zip(Position, guess):
            match letter_guess.result:
                case Result.CORRECT_SPOT:
                    update_correct_letter(self, position, letter_guess.letter)
                case Result.WRONG_SPOT:
                    update_letter_in_wrong_spot(self, position, letter_guess.letter)
                case Result.NOT_IN_WORD:
                    update_letter_is_not_in_word(self, letter_guess.letter)

        collapse_must_include(self)

    def is_possible_match(self, word: Word) -> bool:
        for letter, options in zip(word, self):
            if isinstance(options, Letter):
                if letter != options:
                    return False
            elif letter not in options:
                return False

        return all(letter in word for letter in self.must_include)


def get_matching_words(
    progress: GameProgress, words: list[Word]
) -> Generator[Word, None, None]:
    for word in words:
        if not progress.is_possible_match(word):
            continue

        yield word


def print_info(progress: GameProgress, remaining: Sequence[Word]) -> None:
    print("Known letters")
    chars = (str(letter) if isinstance(letter, Letter) else " " for letter in progress)
    print(f"  |{"|".join(chars)}|")
    print("-----------")
    print("Required letters")
    for letter in sorted(progress.must_include):
        chars = (
            "X" if isinstance(options, set) and letter in options else " "
            for options in progress
        )
        print(f"{letter} |{"|".join(chars)}|")
    print("-----------")
    print("Available letters")
    for letter in sorted(ALL_LETTERS):
        chars = (
            "X" if isinstance(options, set) and letter in options else " "
            for options in progress
        )
        print(f"{letter} |{"|".join(chars)}|")
    print("-----------")
    print(f"Possible words ({len(remaining)} options)")
    for word in remaining:
        chars = (str(letter) for letter in word)
        print(f"  |{'|'.join(chars)}|")
    print("-----------")


def is_valid_word(text: str) -> bool:
    try:
        Word.from_string(text)
    except Exception:
        return False

    return True


def main() -> None:
    print("Welcome to wordle-helper! Made for mum.")
    print(
        "When entering information, [square brackets] represents the default if you leave it blank."
    )
    progress = GameProgress()
    remaining_options = [Word.from_string(guess) for guess in ALLOWED_GUESSES]
    for nguesses in itertools.count(1):
        while not Word.is_valid_text(guess_txt := input("Enter your next guess: ")):
            print("Invalid word. Please try again.")
        guess = Word.from_string(guess_txt)
        while (
            guess_correct := (
                input(f'Was your guess "{guess}" correct? (Y: Yes, N: No) [N]: ') or "N"
            ).upper()
        ) not in {"Y", "N"}:
            print("Invalid input. Please enter Y or N.")
        if guess_correct == "Y":
            print(f"Congratulations, you solved the wordle in {nguesses} guesses!")
            break

        print("Bummer. Alright, let's try again.")
        print("Confirm the letters that you guessed right:")
        results = []
        for position, letter in zip(Position, guess):
            while (
                result := (
                    input(
                        f'- {position.value} letter "{letter}" (A: Incorrect, B: Wrong spot, C: Correct) [A]: '
                    )
                    or "A"
                ).upper()
            ) not in {"A", "B", "C"}:
                print("Invalid input. Please enter A, B, or C.")
            results.append(map_text_to_result(result))

        guess_result = WordGuess.from_word_and_guesses(guess, results)
        progress.update(guess_result)

        print("Crunching the letters...")
        remaining_options = list(get_matching_words(progress, remaining_options))
        print_info(progress, remaining_options)

    input()  # To keep console open


if __name__ == "__main__":
    main()
