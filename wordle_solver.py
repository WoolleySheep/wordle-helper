import contextlib
import itertools
from collections.abc import Generator, Iterable
from typing import Final

import requests

DATAMUSE_API_BASE_URL: Final = "https://api.datamuse.com"
WORD_PATTERN_ENDPOINT: Final = f"{DATAMUSE_API_BASE_URL}/words"


class Letter:
    def __init__(self, text: str) -> None:
        if len(text) != 1 or not text.isalpha():
            raise ValueError("Invalid text")

        self._text = text

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


class FiveLetterWord:
    @classmethod
    def from_string(cls, text: str) -> "FiveLetterWord":
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
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FiveLetterWord):
            raise NotImplementedError

        return (
            self.first == other.first
            and self.second == other.second
            and self.third == other.third
            and self.fourth == other.fourth
            and self.fifth == other.fifth
        )

    def __repr__(self) -> str:
        return f"five_letter_word({self})"


class FiveLetterWordQuery:
    def __init__(
        self,
        first: Letter | None = None,
        second: Letter | None = None,
        third: Letter | None = None,
        fourth: Letter | None = None,
        fifth: Letter | None = None,
    ) -> None:
        self.first = first
        self.second = second
        self.third = third
        self.fourth = fourth
        self.fifth = fifth

    def __str__(self) -> str:
        return f"{self.first or "?"}{self.second or "?"}{self.third or "?"}{self.fourth or "?"}{self.fifth or "?"}"

    def formatted(self) -> str:
        return f"{self.first or "_"} {self.second or "_"} {self.third or "_"} {self.fourth or "_"} {self.fifth or "_"}"


class FiveLetterWordProgress:
    class Outcome:
        def __init__(
            self,
            first_correct: bool = False,
            second_correct: bool = False,
            third_correct: bool = False,
            fourth_correct: bool = False,
            fifth_correct: bool = False,
        ) -> None:
            self.first_correct = first_correct
            self.second_correct = second_correct
            self.third_correct = third_correct
            self.fourth_correct = fourth_correct
            self.fifth_correct = fifth_correct

    def __init__(self) -> None:
        self.first: set[Letter] | Letter = set[Letter]()
        self.second: set[Letter] | Letter = set[Letter]()
        self.third: set[Letter] | Letter = set[Letter]()
        self.fourth: set[Letter] | Letter = set[Letter]()
        self.fifth: set[Letter] | Letter = set[Letter]()

    def current_outcome(self) -> Outcome:
        return self.Outcome(
            first_correct=isinstance(self.first, Letter),
            second_correct=isinstance(self.second, Letter),
            third_correct=isinstance(self.third, Letter),
            fourth_correct=isinstance(self.fourth, Letter),
            fifth_correct=isinstance(self.fifth, Letter),
        )

    def record_guess_outcome(self, guess: FiveLetterWord, outcome: Outcome) -> None:
        if isinstance(self.first, set):
            if outcome.first_correct:
                self.first = guess.first
            else:
                self.first.add(guess.first)

        if isinstance(self.second, set):
            if outcome.second_correct:
                self.second = guess.second
            else:
                self.second.add(guess.second)

        if isinstance(self.third, set):
            if outcome.third_correct:
                self.third = guess.third
            else:
                self.third.add(guess.third)

        if isinstance(self.fourth, set):
            if outcome.fourth_correct:
                self.fourth = guess.fourth
            else:
                self.fourth.add(guess.fourth)

        if isinstance(self.fifth, set):
            if outcome.fifth_correct:
                self.fifth = guess.fifth
            else:
                self.fifth.add(guess.fifth)

    def is_possible_match(self, word: FiveLetterWord) -> bool:
        if isinstance(self.first, Letter):
            if word.first != self.first:
                return False
        elif word.first in self.first:
            return False

        if isinstance(self.second, Letter):
            if word.second != self.second:
                return False
        elif word.second in self.second:
            return False

        if isinstance(self.third, Letter):
            if word.third != self.third:
                return False
        elif word.third in self.third:
            return False

        if isinstance(self.fourth, Letter):
            if word.fourth != self.fourth:
                return False
        elif word.fourth in self.fourth:
            return False

        if isinstance(self.fifth, Letter):
            if word.fifth != self.fifth:
                return False
        elif word.fifth in self.fifth:
            return False

        return True

    def generate_query(self) -> FiveLetterWordQuery:
        return FiveLetterWordQuery(
            first=self.first if isinstance(self.first, Letter) else None,
            second=self.second if isinstance(self.second, Letter) else None,
            third=self.third if isinstance(self.third, Letter) else None,
            fourth=self.fourth if isinstance(self.fourth, Letter) else None,
            fifth=self.fifth if isinstance(self.fifth, Letter) else None,
        )

    def __str__(self) -> str:
        def format_letter(letter: Letter | set[Letter]) -> str:
            def format_correct_letter(letter: Letter) -> str:
                def underline(letter: Letter) -> str:
                    return f"{letter}\u0332"

                return underline(letter)

            def format_incorrect_letter_options(
                letter_options: Iterable[Letter],
            ) -> str:
                def strikethrough(letter: Letter) -> str:
                    return f"\u0336{letter}"

                formatted_letters = (strikethrough(letter) for letter in letter_options)

                return f"{{{", ".join(formatted_letters)}}}"

            if isinstance(letter, Letter):
                return format_correct_letter(letter)

            return format_incorrect_letter_options(letter)

        return f"{format_letter(self.first)} {format_letter(self.second)} {format_letter(self.third)} {format_letter(self.fourth)} {format_letter(self.fifth)}"


def get_ranked_words_matching_query(
    query: FiveLetterWordQuery,
) -> Generator[FiveLetterWord, None, None]:
    response = requests.get(f"{WORD_PATTERN_ENDPOINT}?sp={query}")
    for word_dict in response.json():
        with contextlib.suppress(ValueError):
            yield FiveLetterWord.from_string(word_dict["word"])


def get_best_word(
    ranked_words: Iterable[FiveLetterWord], progress: FiveLetterWordProgress
) -> FiveLetterWord:
    for word in ranked_words:
        if progress.is_possible_match(word):
            return word

    raise ValueError


def main() -> None:
    print("Welcome to wordle solver! [made for Cathie]")
    guess = FiveLetterWord.from_string(input("Enter your first guess into this app: "))
    print(f'Enter your first guess "{guess}" into the wordle app.')
    progress = FiveLetterWordProgress()
    for nguesses in itertools.count(1):
        if input(f'Was your guess "{guess}" correct? [yes/NO]: ') == "yes":
            print(f"Congratulations, you solved the wordle in {nguesses} guesses!")
            break

        print("Bummer. Alright, let's try again.")
        print("Confirm the letters that you guessed right:")
        guess_outcome = progress.current_outcome()

        if guess_outcome.first_correct:
            print(f'- First letter "{guess.first}" known')
        elif input(f'- First letter "{guess.first}" correct? [yes/NO]: ') == "yes":
            guess_outcome.first_correct = True

        if guess_outcome.second_correct:
            print(f'- Second letter "{guess.second}" known')
        elif input(f'- Second letter "{guess.second}" correct? [yes/NO]: ') == "yes":
            guess_outcome.second_correct = True

        if guess_outcome.third_correct:
            print(f'- Third letter "{guess.third}" known')
        elif input(f'- Third letter "{guess.third}" correct? [yes/NO]: ') == "yes":
            guess_outcome.third_correct = True

        if guess_outcome.fourth_correct:
            print(f'- Fourth letter "{guess.fourth}" known')
        elif input(f'- Fourth letter "{guess.fourth}" correct? [yes/NO]: ') == "yes":
            guess_outcome.fourth_correct = True

        if guess_outcome.fifth_correct:
            print(f'- Fifth letter "{guess.fifth}" known')
        elif input(f'- Fifth letter "{guess.fifth}" correct? [yes/NO]: ') == "yes":
            guess_outcome.fifth_correct = True

        progress.record_guess_outcome(guess=guess, outcome=guess_outcome)

        print(f'Determining the best next guess based on "{progress}".')

        ranked_words = get_ranked_words_matching_query(query=progress.generate_query())
        guess = get_best_word(ranked_words=ranked_words, progress=progress)
        print(f'Your next guess should be "{guess}".')

        print(f'Enter your next guess "{guess}" into the wordle app.')

    input()  # To keep console open


if __name__ == "__main__":
    main()
