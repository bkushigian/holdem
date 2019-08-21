# README

## Requirements
Beano is written in Python 3.6 though any Python 3.4+ should work (we hope!)

## Connecting to a Game
Beano needs to be running on a server (either local or remote) to play.

### Connecting to Remote Games

There is a default server running which the `run.sh` script connects to
automatically:

```
./run.sh        # Connect to the default server
```

If you want to connect to a specific server then you will need to know its
address and the port the server is listening on. You can connect to this
by running:

```
./run.sh address port    # Connect to a specific server!
```

For instance, the default server is at IP address `167.71.182.40` and listens on
port `65432`, and running `./run.sh 167.71.182.40 65432` is equivalent to running
`./run.sh`.

### Local Games
If you want to play on a single computer you will have to run your own local
server.  To set up the server, open a terminal, change directory to the root
of the Beano project and run:

```
./run_server.sh        # Run the server
```

You can optionally specify the port you would like to listen on (default is
65432).

The Beano server is now running and is waiting for clients! To set up the first
player, open another terminal, change directory to the root of the Beano
project, and run

```
./run.sh local        # Connect a client to a local game
```

Do the same thing for the second client, and you're ready to play!

### Choosing a Username

You can select your own username, or we can create one for you. To select one of
your own, go ahead and type it into the prompt and hit Enter. If this name is
available you will be placed in a waiting area to wait for a worthy opponent.
If the name is already taken you'll be prompted to enter a new name.

To have Beano select a name for you, hit Enter (without entering any text) and
you'll have your very own auto-generated name! Neat, huh?

## Playing the game
To get a feel for gameplay, let's take a look at a game between Puzzled Aye-Aye
and Massive Salamander:

```

                       Puzzled Aye-Aye's View (Player 1)
                                -+- PHASE 1 -+-


Other Players:
  * Massive Salamander: 4 Cards || $0 (3) || 2x Soy  4x Chili  Fallow

  Status:         Good
  Current Player: Massive Salamander (Player 2)
  Discard:        [Blue,Blue,Blue]
  Deck:           109 Cards

+----------++----------++----------+        +----------++----------++----------+
|   Wax    ||  Stink   ||          |        |  Coffee  ||  Chili   ||  Stink   |
|   22x    ||   16x    ||          |        |   24x    ||   18x    ||   16x    |
|  4x: $1  ||  3x: $1  ||   Empty  |        |  4x: $1  ||  3x: $1  ||  3x: $1  |
|  7x: $2  ||  5x: $2  ||          |        |  7x: $2  ||  6x: $2  ||  5x: $2  |
|  9x: $3  ||  7x: $3  ||          |        | 10x: $3  ||  8x: $3  ||  7x: $3  |
| 11x: $4  ||  8x: $4  ||          |        | 12x: $4  ||  9x: $4  ||  8x: $4  |
+----------++----------++----------+        +----------++----------++----------+
     1x          2x          0x        $1        1x          5x          2x     
             Offerings                 $2                  Fields               

+----------++----------++----------+
|  Coffee  ||  Chili   ||  Stink   |
|   24x    ||   18x    ||   16x    |
|  4x: $1  ||  3x: $1  ||  3x: $1  |
|  7x: $2  ||  6x: $2  ||  5x: $2  |
| 10x: $3  ||  8x: $3  ||  7x: $3  |
| 12x: $4  ||  9x: $4  ||  8x: $4  |
+----------++----------++----------+

Available Actions: (h)arvest, (p)lant from offering <1..3>, (n)ext

```

Puzzled Aye-Aye's hand comprises the three cards at the bottom of the screen, and
there are three offerings and three bean fields. The first two offerings are
populated, one with a single Wax Bean, and one with two Stink Beans, and Puzzled
Aye-Aye's bean fields are currently growing a single Coffee Bean, five Chili
Beans, and two Stink Beans. Between the offerings and the bean fields is Puzzled
Aye-Aye's coin total, who currently has $1 in the bank but would have $2 if she
harvested all of the beans in her fields.

Massive Salamander has no money in the bank at the moment but if he harvested
all of the beans in his fields right now he would have $3. He has 4 cards in
his hand, and his bean fields contain 2x Soy Beans, 4x Chili Beans, and 5x Wax
Beans.

### Harvesting Beans
To earn coins the bean farmer has to _harvest_ beans.  A farmer can harvest
beans at any time on your turn by entering `harvest idx`, where `idx` is the
index of the field they want to harvest. For example, if Puzzled Aye-Aye wanted
to harvest the five Chili Beans planted in her field they would enter `harvest
5`, or `h 5` for short. Likewise, `h 1` would harvest her Coffee Beans and `h 3`
would harvest her two Stink Beans.

To tell how much money would be harvested, look up the dollar amount in the
table on the card associating the number of beans you have. If the number of
beans you have isn't listed, choose the largest number less than the quantity
you have.


For instance, harvesting 9x Coffee Beans from your field will give you $2, but
harvesting 10x Coffee Beans will give you $3.
```
+----------+
|  Coffee  |
|   24x    |
|  4x: $1  |
|  7x: $2  |
| 10x: $3  |
| 12x: $4  |
+----------+
```

Cards that are harvested are sent to the _discard pile_, minus one for each coin
you collect; so harvesting 9x Coffee Beans would send 7x cards to the discard
pile and two coins to your pocket!

### Bean Cards
There are several kinds of beans, each occurring with a certain frequency in the
deck. You can harvest beans to get money. For instance, here is a Wax bean:

```
+----------+
|   Wax    | <-----   Name of the Bean
|   22x    | <-----   Quantity of the Bean
|  4x: $1  | <-----\
|  7x: $2  |        \ Prices of
|  9x: $3  |        / the Bean
| 11x: $4  | <-----/
+----------+
```

There are __22__ Wax Beans in the deck, and you can harvest __4__ Wax beans to get 1
coin, __7__ Wax beans to get 2 coins, __9__ Wax beans to get 3 coins, and __11__
Wax beans to get 4 coins. Simple, no?

Here is a listing of all beans and their associated frequency, as well as the
number you need to harvest to get 1, 2, 3, and 4 coins respectively.

|        Bean         | Count | $1 | $2 | $3 | $4 |
|---------------------|-------|----|----|----|----|
| **Coffee Bean**     | 24    |  4 |  7 | 10 | 12 |
| **Wax Bean**        | 22    |  4 |  7 |  9 | 11 |
| **Blue Bean**       | 20    |  4 |  6 |  8 | 10 |
| **Chili Bean**      | 18    |  3 |  6 |  8 |  9 |
| **Stink Bean**      | 16    |  3 |  5 |  7 |  8 |
| **Green Bean**      | 14    |  3 |  5 |  6 |  7 |
| **Soy Bean**        | 12    |  2 |  4 |  6 |  7 |
| **Black-eyed Bean** | 10    |  2 |  4 |  5 |  6 |
| **Red Bean**        | 8     |  2 |  3 |  4 |  5 |
| **Garden Bean**     | 6     |  - |  2 |  3 |  - |
| **Cocoa Bean**      | 4     |  - |  2 |  3 |  4 |



### Gameplay
Players take turns one after another until the entire deck has run out. Each
player starts with five cards in hand and three empty bean fields. Additionally
there is an Offering which starts out as three empty slots. The goal of the game
is to plant beans in your bean field and harvest them for ridiculous amounts of
money.


#### Phase I: Plant from Offering
In Phase III of the previous turn your opponent flipped over some cards in the
offering and may not have planted them. If not, you now have a chance to plant
them yourself!

##### Example
Say your opponent neglected a Wax bean and you would like to plant this to match
a Wax bean already in your field:

```
+----------++----------++----------+        +----------++----------++----------+
|          ||   Wax    ||          |        |   Wax    ||  Chili   ||  Stink   |
|          ||   22x    ||          |        |   22x    ||   18x    ||   16x    |
|   Empty  ||  4x: $1  ||   Empty  |        |  4x: $1  ||  3x: $1  ||  3x: $1  |
|          ||  7x: $2  ||          |        |  7x: $2  ||  6x: $2  ||  5x: $2  |
|          ||  9x: $3  ||          |        |  9x: $3  ||  8x: $3  ||  7x: $3  |
|          || 11x: $4  ||          |        | 11x: $4  ||  9x: $4  ||  8x: $4  |
+----------++----------++----------+        +----------++----------++----------+
     0x          1x          0x        $1        1x          5x          2x
             Offerings                 $2                  Fields

```

You can plant this Wax bean by entering `p 2`, planting the bean in the second
offering slot.

If you do not want anything in the offering, simply enter `n` to go to the next
phase.

#### Phase II: Plant from Hand
In the second phase you _must_ plant the first card in your hand. You may
additionally plant the second card in your hand, and finally you can discard a
card from your hand. To signal the end of phase, enter 'n'.

#### Phase III: Flipping the Offering
Phase III starts with three cards being revealed form the top of the deck and
being placed in the offering. Additionally, any cards on top of the discard pile
that match cards from the offering will be placed on top of the matching card in
the offering. This continues until the top card of the discard pile doesn't
match any card in the offering (or until the discard pile is empty). You may
then choose which cards you want to plant via `p [1,2,3]`, finally entering `n`
to go to the next phase.

#### Phase IV: Draw
In the final phase you draw two cards and your turn passes


