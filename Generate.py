import secrets

class Generate:
    def __init__(self, length):
        self.alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
            'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        self.special = ['!', '@', '#', '$', '%', '&', '+', '=', '?', '(', ')', '[', ']', '<', '>', '/']
        # self.special = ['!', '@', '#', '$', '?', '(', ')', '[', ']', '<', '>']
        self.password = []
        self.length = length
        self.base_count = length // 4
        self.remainder = length % 4

    def upper(self):
        for x in range(self.base_count):
            self.password.append(secrets.choice(self.alphabet))

    def lower(self):
        for x in range(self.base_count):
            self.password.append(secrets.choice(self.alphabet).lower())

    def characters(self):
        for x in range(self.base_count + self.remainder):
            self.password.append(secrets.choice(self.special))
        
    def numbers(self):
        for x in range(self.base_count):
            self.password.append(str(secrets.randbelow(10)))

    def shuffle_and_combine(self):
        # secrets doesn't have shuffle, so we use a Fisher-Yates shuffle with secrets.randbelow
        for i in range(len(self.password) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            self.password[i], self.password[j] = self.password[j], self.password[i]
        return "".join(self.password)

    def main(self):
        self.upper()
        self.lower()
        self.characters()
        self.numbers()
        return self.shuffle_and_combine()