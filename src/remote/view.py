import curses

from view import ViewClientMixin, ViewGameState, ViewServerMixin


class CursesView(ViewClientMixin):
    def __init__(self):
        self.stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

    def close(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def render(self):
        pass


class ClientViewCLI(ViewClientMixin):
    """
        A simple test view through a CLI. There is only a single CLI built for
        all players.
    """
    """
    def __init__(self, owner, formatter=None):  # added owner (not sure)
        self.game_state = ViewGameState(owner)   # why no owner arg?
        self.formatter = formatter
        if formatter is None:
            self.formatter = Formatter(self)
    """

    def __init__(self, game_state, formatter=None):  # added owner (not sure). need owner?
        self.game_state: ViewGameState = game_state  # why no owner arg?
        self.formatter = formatter
        if formatter is None:
            self.formatter = Formatter(self)

    def setup(self, phase, players, current_player, hand, deck_size, offering, discard):    # what is this for? needs to be updated
        gs = self.game_state
        gs.phase = phase        # want?
        gs.players = players
        gs.current_player = current_player
        gs.hand = hand
        gs.deck_size = deck_size
        gs.offering = offering
        gs.discard = discard

    def update(self, game_state):
        self.game_state.update(game_state)
        pass

    def render(self):
        print(str(self.formatter))


class Formatter:
    def __init__(self, view):                   # view is a ViewCLI?
        self.view = view
        self.game_state = view.game_state
        self.player_colors = ["32", "34", "31", "96"]

    def error_string(self):
        if self.game_state.error is not None:
            return "ERROR: {}".format(self.game_state.error)
        else:
            return ""

    def phase_string(self):
        return "{:^80}".format("-+- PHASE {} -+-".format(self.game_state.phase))

    def other_player_string(self, player):
        """
        Print a string representation of the player without any private info,
        such as cards in hand.
        """
        return """  * \033[1m{}\033[0m: \033[32;1m{} Cards\033[0m || \033[32;1m${}\033[0m || \033[32;1m[{}]\033[0m""".format(
            player.name,
            player.hand_size,
            player.coins,
            ', '.join([str(c) if c else 'Fallow' for c in player.fields ]))

    def discard_string(self):
        d = self.game_state.discard
        if len(d) <= 3:
            return "[{}]".format(','.join([str(x) for x in d]))
        return "[{}]".format(','.join([str(x) for x in d[-3:]]))

    def deck_string(self):
        return "{} Cards".format(self.game_state.deck_size)

    def owner_string(self):
        return "{}\n{}".format(
            self.offering_and_field_string(),
            self.hand_string())

    def hand_string(self):
        lines = ['', '', '', '', '', '', '', '']
        for card in self.game_state.hand:
            p = card.pretty()
            for i, line in enumerate(p.split('\n')):
                lines[i] += line
        return '\n'.join(lines)

    empty = '+----------+\n|{:^10}|\n|{:^10}|\n|{}|\n|{:^10}|\n|{:^10}|\n|{:^10}|\n+----------+'.format(
        '', '', '   \033[1;3mEmpty\033[0m  ', '', '', '')

    def offering_and_field_string(self):
        os = self.offering_string().split('\n')
        fs = self.field_string().split('\n')

        footer = '\033[1;34;7m{:^36}\033[0m\033[1;32m{:^8}\033[0m\033[1;34;7m{:^36}\033[0m\n'.format("Offerings", "${}".format(
            self.game_state.players[self.game_state.owner].coins), "Fields")
        return '\n'.join([o + '        ' + f for (o, f) in zip(os, fs)]) + '\n' + footer

    def offering_string(self):
        lines = ['', '', '', '', '', '', '', '', '']
        offering = self.game_state.offering
        for card in offering:
            quantity = '0x'
            if card is None:
                p = self.empty
            else:
                card, quantity = card
                quantity = '{}x'.format(quantity)
                p = card.pretty()
            for i, line in enumerate(p.split('\n')):
                lines[i] += line
            lines[-1] += '\033[1;3;7;34m{:^12}\033[0m'.format('{}'.format(quantity))
        return '\n'.join(lines)

    def field_string(self):
        lines = ['', '', '', '', '', '', '', '', '']
        fields = self.game_state.players[self.game_state.owner].fields
        for card in fields:
            quantity = '0x'
            if card is None:
                p = self.empty
            else:
                card, quantity = card
                quantity = '{}x'.format(quantity)
                p = card.pretty()
            for i, line in enumerate(p.split('\n')):
                lines[i] += line
            lines[-1] += '\033[1;3;7;34m{:^12}\033[0m'.format('{}'.format(quantity))
        return '\n'.join(lines)

    def __str__(self):
        def decorate_first_letter(s):
            if not s:
                return ''
            c = s[0]
            s = s[1:]
            return "\033[1;32m({})\033[0m{}".format(c, s)
        gs = self.game_state

        cp = "{}'s View (Player {})".format(gs.players[gs.owner].name, gs.owner + 1)
        status_str = "Good"
        if self.error_string() != "":                 # MESSY
            status_str = self.error_string()

        other_players = '\n'.join([self.other_player_string(p) for (i, p) in enumerate(gs.players) if i != gs.owner])

        color = self.player_colors[gs.current_player]
        return """
        
        
        
        
        
        
        
\033[1;7;{}m                                                                                \033[0m
\033[1;7;{}m{:^80}\033[0m
\033[1;7;{}m{}\033[0m
\033[1;7;{}m                                                                                \033[0m

\033[94;1mOther Players:\033[0m
{}

  \033[1;94mStatus:        \033[0m {}
  \033[1;94mCurrent Player:\033[0m {} (Player {})
  \033[1;94mDiscard:       \033[0m {}
  \033[1;94mDeck:          \033[0m {}

{}

\033[34;1mAvailable Actions:\033[0m {}
""".format(color,
           color,
           cp,
           color,
           self.phase_string(),
           color,
           other_players,
           status_str,
           gs.players[gs.current_player].name,
           gs.current_player + 1,
           self.discard_string(),
           self.deck_string(),
           self.owner_string(),
           ', '.join([decorate_first_letter(str(x)) for x in gs.available_actions]))


class ServerView(ViewServerMixin):
    def __init__(self, sid, network_manager):
        self.nm = network_manager
        self.sid = sid

    def update(self, game_state: ViewGameState):
        """Send the game state to the view"""
        msg = {'type': 'game-state-update', 'data': {'game-state': game_state}}
        self.nm.get_session(self.sid).outb += self.nm.pack(msg)
