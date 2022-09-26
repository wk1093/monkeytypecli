import curses
import time
import random


class ColorString:
    def __init__(self, string, color):
        self.string = string
        self.color = color

    def draw(self, stdscr, y, x):
        stdscr.addstr(y, x, self.string, self.color)


class MonkeyTypeString:
    def __init__(self, start_string, colors):
        self.start = start_string
        self.typed = ""
        self.cUntyped = colors[0]
        self.cTyped = colors[1]
        self.cBad = colors[2]
        self.cExtend = colors[3]
        self.cSkip = colors[4]

    def type(self, char: str) -> bool:
        if char in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ ':
            if len(self.typed) > 0:
                if char == ' ' and self.typed[-1] == ' ':
                    return False
            elif char == ' ':
                return False

            self.typed += char
            return True
        else:
            if ord(char) == 8 or ord(char) == curses.KEY_BACKSPACE:
                self.typed = self.typed[:-1]
            return False

    def render_string(self) -> list[ColorString]:
        out = []
        twords = self.typed.split(' ')
        swords = self.start.split(' ')
        for i in range(len(swords)):
            w1 = swords[i]
            if len(twords) > i:
                w2 = twords[i]
            else:
                w2 = '\0'
            if w1 == w2:
                out.append(ColorString(w1 + ' ', self.cTyped))
            else:
                out += self.render_word(w1, w2, i)
        return out

    def render_word(self, w1, w2, word_i) -> list[ColorString]:
        out = []
        if len(w2) > len(w1):
            for i in range(len(w2)):
                ch2 = w2[i]
                if len(w1) > i:
                    ch1 = w1[i]
                else:
                    ch1 = '\0'
                if ch1 == ch2:
                    out.append(ColorString(ch1, self.cTyped))
                elif ch1 == '\0':
                    out.append(ColorString(ch2, self.cExtend))
                else:
                    out.append(ColorString(ch1, self.cBad))
        else:
            for i in range(len(w1)):
                ch1 = w1[i]
                if len(w2) > i:
                    ch2 = w2[i]
                else:
                    ch2 = '\0'
                if ch1 == ch2:
                    out.append(ColorString(ch1, self.cTyped))
                else:
                    if ch2 != '\0':
                        out.append(ColorString(ch1, self.cBad))
                    elif len(self.typed.split(' ')) > word_i + 1:
                        out.append(ColorString(ch1, self.cSkip))
                    else:
                        out.append(ColorString(ch1, self.cUntyped))
        out.append(ColorString(' ', self.cTyped))

        return out

    def len_render(self) -> int:
        st = self.render_string()
        out = 0
        for s in st:
            out += len(s.string)
        return out

    # def done(self) -> bool:  # done typing
    #     if self.typed == self.start:
    #         return True
    #     if self.cursor_pos() >= self.len_render()-1:
    #         return True
    def done(self) -> bool:
        if self.typed == self.start:
            return True
        if self.typed.split(' ')[-1] == self.start.split(' ')[-1]:
            return True
        return False

    def words(self) -> float:  # characters/5
        return len(self.typed) / 5.0

    def find_offset_string(self) -> int:
        off = 0
        twords = self.typed.split(' ')
        swords = self.start.split(' ')
        for i in range(len(swords)):
            w1 = swords[i]
            if len(twords) > i:
                w2 = twords[i]
            else:
                w2 = '\0'
            if w1 != w2:
                off += self.find_offset_word(w1, w2, i)
        return off

    def find_offset_word(self, w1, w2, word_i) -> int:
        off = 0
        if not len(w2) > len(w1):
            for i in range(len(w1)):
                ch1 = w1[i]
                if len(w2) > i:
                    ch2 = w2[i]
                else:
                    ch2 = '\0'
                if ch1 != ch2 and ch2 == '\0' and len(self.typed.split(' ')) > word_i + 1:
                    off += 1
        # off += 1
        return off

    def cursor_pos(self) -> int:
        offset = self.find_offset_string()
        return len(self.typed) + offset


def main(stdscr, strinp):
    # Init colors and stuff
    stdscr.clear()
    stdscr.refresh()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    color_untyped = curses.color_pair(1) + curses.A_BOLD
    color_typed = curses.color_pair(2)
    color_bad = curses.color_pair(3) + curses.A_BOLD
    color_bad_ext = curses.color_pair(3)
    color_skip = curses.color_pair(1) + curses.A_BOLD + curses.A_UNDERLINE
    color_title = curses.color_pair(2) + curses.A_BOLD

    # init state variables
    k = 0
    mts = MonkeyTypeString(strinp, [color_untyped, color_typed, color_bad, color_bad_ext, color_skip])
    starttime = 0
    donetime = 0
    started = False
    done = False

    while k != 27:  # ESC
        stdscr.clear()
        stdscr.addstr(0, 0, "MonkeyType CLI v1.0 (Not associated with monkeytype.com)", color_title)

        # RESET
        if k == curses.KEY_ENTER or k == ord("\n") or k == ord("\t"):
            return True

        # Type and Start
        if mts.type(chr(k)) and not started:
            starttime = time.time()
            started = True

        # Done
        if mts.done():
            done = True

        # Render
        i = 0
        for cs in mts.render_string():
            cs.draw(stdscr, 2, i)
            i += len(cs.string)

        # Timing
        if started and not done:
            donetime = float(time.time())

        # Display WPM and done message
        if done:
            timespent = ((donetime - starttime) / 60.0)
            if timespent == 0:
                timespent = 0.000001
            rawwpm = mts.words() / timespent
            stdscr.addstr(6, 0,
                          f"Raw WPM: {rawwpm}          ")
            stdscr.addstr(9, 0, "Press ESC to exit, or press ENTER/TAB to retry")

        # Loop stuff
        stdscr.move(2, mts.cursor_pos())
        stdscr.refresh()
        k = stdscr.getch()

    return False


def generate_words(amount: 10):
    words = ["the", "be", "of", "and", "a", "to", "in", "he", "have", "it", "that", "for", "they", "I", "with", "as",
             "not", "on", "she", "at", "by", "this", "we", "you", "do", "but", "from", "or", "which", "one", "would",
             "all", "will", "there", "say", "who", "make", "when", "can", "more", "if", "no", "man", "out", "other",
             "so", "what", "time", "up", "go", "about", "than", "into", "could", "state", "only", "new", "year", "some",
             "take", "come", "these", "know", "see", "use", "get", "like", "then", "first", "any", "work", "now", "may",
             "such", "give", "over", "think", "most", "even", "find", "day", "also", "after", "way", "many", "must",
             "look", "before", "great", "back", "through", "long", "where", "much", "should", "well", "people", "down",
             "own", "just", "because", "good", "each", "those", "feel", "seem", "how", "high", "too", "place", "little",
             "world", "very", "still", "nation", "hand", "old", "life", "tell", "write", "become", "here", "show",
             "house", "both", "between", "need", "mean", "call", "develop", "under", "last", "right", "move", "thing",
             "general", "school", "never", "same", "another", "begin", "while", "number", "part", "turn", "real",
             "leave", "might", "want", "point", "form", "off", "child", "few", "small", "since", "against", "ask",
             "late", "home", "interest", "large", "person", "end", "open", "public", "follow", "during", "present",
             "without", "again", "hold", "govern", "around", "possible", "head", "consider", "word", "program",
             "problem", "however", "lead", "system", "set", "order", "eye", "plan", "run", "keep", "face", "fact",
             "group", "play", "stand", "increase", "early", "course", "change", "help", "line"]
    return [random.choice(words) for _ in range(amount)]


if __name__ == "__main__":
    while True:
        if not curses.wrapper(main, " ".join(generate_words(10))):
            break
