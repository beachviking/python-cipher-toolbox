from cmd import Cmd
from dataclasses import dataclass
from prettytable import PrettyTable

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
ENGLISH_LETTER_FREQ = [
    0.08167,
    0.01492,
    0.02782,
    0.04253,
    0.12702,
    0.02228,
    0.02015,
    0.06094,
    0.06966,
    0.00153,
    0.00772,
    0.04025,
    0.02406,
    0.06749,
    0.07507,
    0.01929,
    0.00095,
    0.05987,
    0.06327,
    0.09056,
    0.02758,
    0.00978,
    0.02360,
    0.00150,
    0.01974,
    0.00074,
]

DEFAULT_PLAIN_TEXT = "greetingsstrangerthisisfuckingshitewemissedawholemotherlodeoffun"
DEFAULT_KEY = "hello"


@dataclass
class CryptoToolData:
    key: str = ""
    cipher_text: str = ""
    plain_text: str = ""
    keyperiod: int = 5


def vigenere(text: str, key: str, alphabet=ALPHABET, encrypt=True) -> str:
    text = text.lower()
    key = key.lower()

    result = ""
    for i in range(len(text)):
        # placeholder logic for unsupported characters...
        # if not text[i] in alphabet:
        #     result += text[i]
        #     continue

        letter_n = alphabet.find(text[i])
        key_n = alphabet.find(key[i % len(key)])
        value = (letter_n + key_n) if encrypt else (letter_n - key_n)
        value %= len(alphabet)
        result += alphabet[value]

    return result


def vigenere_encrypt(text: str, key: str) -> str:
    return vigenere(text=text, key=key, encrypt=True)


def vigenere_decrypt(text: str, key: str) -> str:
    return vigenere(text=text, key=key, encrypt=False)


def caesar_encrypt(text: str, key: str) -> str:
    return vigenere(text=text, key=key[0], encrypt=True)


def caesar_decrypt(text: str, key: str) -> str:
    return vigenere(text=text, key=key[0], encrypt=False)


def get_index_of_coincidence(text: str, alphabet=ALPHABET) -> float:
    counts = [0] * 26
    text = text.lower()

    for idx, char in enumerate(alphabet):
        counts[idx] = text.count(char)

    ioc = 0
    text_len = sum(counts)

    if text_len == 0:
        return 0

    for i in range(len(alphabet)):
        numerator = counts[i] * (counts[i] - 1)
        denominator = text_len * (text_len - 1)
        if not denominator == 0:
            ioc += numerator / denominator

    return ioc


def get_string_slices(text: str, period: int) -> list:
    """
    Returns a list with strings which are slices of the text for every period character
    ie
        get_string_slices('abcdefghijklmnopqrstuvwxyz', 2)
        result = ['aceg...', 'bdf...']
    """
    return [text[i::period] for i in range(period)]


def get_index_of_coincidence_for_period(text: str, period: int) -> float:
    sum = 0
    slices = get_string_slices(text, period)
    # get total ioc for all slices for this period
    for i in range(len(slices)):
        sum += get_index_of_coincidence(slices[i])

    return sum / period


def get_indexes_of_coincidence(text: str, max_period: int) -> list:
    results = []

    # calculate ioc per period
    for period in range(2, max_period + 1):
        ioc = get_index_of_coincidence_for_period(text, period)
        results.append(ioc)
        # print(f'period = {period}, ioc = {ioc}')

    return results


def chi_squared(
    text: str, letter_freq_dist=ENGLISH_LETTER_FREQ, alphabet=ALPHABET
) -> float:
    # calculate counts of letters
    counts = [0] * 26
    text = text.lower()
    chi_sq = 0.0

    for idx, char in enumerate(alphabet):
        counts[idx] = text.count(char)

    num_letters = sum(counts)

    for i in range(len(alphabet)):
        expected = letter_freq_dist[i] * num_letters
        if not expected == 0:
            chi_sq += (counts[i] - expected) ** 2 / expected

    return chi_sq


def guess_caesarian_key(ciphertext: str, alphabet=ALPHABET) -> tuple[list, list]:
    chi_sq_results = []

    for i in range(len(alphabet)):
        decoded = vigenere_decrypt(ciphertext, alphabet[i])
        chi_sq_results.append(chi_squared(decoded))

    letters = []
    scores = []

    sort_index = [i for i, x in sorted(enumerate(chi_sq_results), key=lambda x: x[1])]

    # add result with best score
    letters.append(alphabet[sort_index[0]])
    scores.append(chi_sq_results[sort_index[0]])

    # check to see if we should add second best score
    if chi_sq_results[sort_index[1]] < chi_sq_results[int(sort_index[0])] * 1.5:
        letters.append(alphabet[sort_index[1]])
        scores.append(chi_sq_results[sort_index[1]])

    return letters, scores


def guess_vigenere_key(ciphertext: str, keyperiod: int):
    # extract string slices, each slice representing a Caesarian cipher to break
    slices = get_string_slices(ciphertext, keyperiod)
    results = []

    # do a Caesarian guess for each slice
    for i in range(len(slices)):
        results.append(guess_caesarian_key(slices[i]))

    return results


class MyPrompt(Cmd):
    def __init__(self) -> None:
        super().__init__()
        self.cryptodata = CryptoToolData

    def print_vguess(self, results: tuple[list, list]):
        x = PrettyTable()
        x.field_names = ["Key Position #", "Possible Characters", "Chi-Sq Score"]

        for idx, result in enumerate(results):
            for j in range(len(result[0])):
                x.add_row([idx + 1 if j == 0 else "", result[0][j], result[1][j]])

            x._dividers[-1] = True

        print(x)

    def print_cguess(self, results: tuple[list, list]):
        x = PrettyTable()
        x.field_names = ["Key Position #", "Possible Characters", "Chi-Sq Score"]

        for j in range(len(results[0])):
            x.add_row(["1" if j == 0 else "", results[0][j], results[1][j]])

        print(x)

    def print_crypto_data(self):
        print(f"Plain text  : {self.cryptodata.plain_text}")
        print(f"Cipher text : {self.cryptodata.cipher_text}")
        print(f"Key text    : {self.cryptodata.key}")

    def do_hello(self, args):
        """Says hello. If you provide a name, it will greet you with it."""
        if len(args) == 0:
            name = "stranger"
        else:
            name = args
        print(f"Hello, {name}")

    def do_setkey(self, args):
        """Sets the cipher key to use."""
        self.cryptodata.key = args
        print(f"Setting key to '{self.cryptodata.key}'")

    def do_view(self, args):
        """Shows current key, plain and cipher texts."""
        self.print_crypto_data()

    def do_key(self, args=None):
        """Prints the current key."""
        print(self.cryptodata.key)

    def do_setplain(self, args):
        """Sets the current plain text."""
        self.cryptodata.plain_text = args
        print(f"Setting plain text to '{self.cryptodata.plain_text}'")

    def do_plain(self, args=None):
        """Prints the current plain text."""
        print(self.cryptodata.plain_text)

    def do_setcipher(self, args):
        """Sets the current cipher text."""
        self.cryptodata.cipher_text = args
        print(f"Setting cipher text to '{self.cryptodata.cipher_text}'")

    def do_cipher(self, args=None):
        """Prints the current cipher text."""
        print(self.cryptodata.cipher_text)

    def do_setkeyperiod(self, args):
        """Sets the key period."""
        self.cryptodata.keyperiod = int(args)
        print(f"Setting key period to {self.cryptodata.keyperiod}")

    def do_keyperiod(self, args=None):
        """Prints the current key period."""
        print(self.cryptodata.keyperiod)

    def do_vencrypt(self, args=None):
        """Encrypts the stored plain text with the set key using the Vigenere cipher."""
        print("Encrypting current data with Vigenere...")
        self.cryptodata.cipher_text = vigenere_encrypt(
            self.cryptodata.plain_text, self.cryptodata.key
        )
        self.print_crypto_data()

    def do_vdecrypt(self, args=None):
        """Decrypts the stored cipher text with the set key using the Vigenere cipher."""
        print("Decrypting current data with Vigenere...")
        self.cryptodata.plain_text = vigenere_decrypt(
            self.cryptodata.cipher_text, self.cryptodata.key
        )
        self.print_crypto_data()

    def do_cencrypt(self, args=None):
        """Encrypts the stored plain text with the set key using the Caesarian cipher."""
        print("Encrypting current data with Caesarian...")
        self.cryptodata.key = self.cryptodata.key[0]
        self.cryptodata.cipher_text = caesar_encrypt(
            self.cryptodata.plain_text, self.cryptodata.key
        )
        self.print_crypto_data()

    def do_cdecrypt(self, args=None):
        """Decrypts the stored cipher text with the set key using the Caesarian cipher."""
        print("Decrypting current data with Caesarian...")
        self.cryptodata.key = self.cryptodata.key[0]
        self.cryptodata.plain_text = caesar_decrypt(
            self.cryptodata.cipher_text, self.cryptodata.key
        )
        self.print_crypto_data()

    def do_getiocs(self, args=None):
        """Calculates and returns a formatted table of incidences of coincidence for a range of periods for cipher text. Default range of periods is from 2 to 15."""
        print("Calculating the incidences of coincidence for cipher text...")
        max_period = 10
        if args.isnumeric():
            max_period = int(args)

        x = PrettyTable()
        x.field_names = ["Period", "Incidence of Coincidence"]
        iocs = get_indexes_of_coincidence(self.cryptodata.cipher_text, max_period)

        for idx, item in enumerate(iocs):
            x.add_row([idx + 2, item])

        print(x)

    def do_vguess(self, args):
        """Performs a key guess on the current cipher text using a Vigenere cipher."""
        print("Guessing the Vigenere key for current cipher text and keyperiod...")
        self.print_vguess(
            guess_vigenere_key(self.cryptodata.cipher_text, self.cryptodata.keyperiod)
        )

    def do_cguess(self, args):
        """Performs a key guess on the current cipher text using a Caesarian cipher."""
        print("Guessing the Caesarian key for current cipher text...")
        self.print_cguess(guess_caesarian_key(self.cryptodata.cipher_text))

    def do_vtest(self, args):
        """Sets default plain and cipher texts and runs through Vigenere encrypt and decrypt processes."""
        self.do_setkey(DEFAULT_KEY)
        self.do_setplain(DEFAULT_PLAIN_TEXT)
        self.do_vencrypt()
        self.do_vdecrypt()

    def do_quit(self, args):
        """Quits the program."""
        print("Quitting.")
        raise SystemExit


def main():
    prompt = MyPrompt()
    prompt.prompt = "> "
    prompt.cmdloop("Simple cipher playground command application, have fun!")


if __name__ == "__main__":
    main()
