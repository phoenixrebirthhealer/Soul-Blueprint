"""
Sabian Symbols lookup table and calculation functions.
Source: Original Marc Edmund Jones / Elsie Wheeler images (1925) — public domain.
Symbols numbered 1-30 per sign. See SABIAN_SYMBOLS_SPEC.md for rounding rule.

ROUNDING RULE (non-negotiable):
  0 minutes exactly = use that degree symbol
  ANY minutes past the degree = round UP to next symbol
  Example: 5°00' = symbol 5 | 5°01' = symbol 6 | 18°57' = symbol 19
"""

from flask import request, jsonify

SABIAN_SYMBOLS = {
    "Aries": {
        1:  "A woman has risen out of the ocean, a seal is embracing her",
        2:  "A comedian entertains a group",
        3:  "A cameo profile of a man in the outline of his country",
        4:  "Two lovers are strolling on a secluded walk",
        5:  "A triangle with wings",
        6:  "A square brightly lighted on one side",
        7:  "A man succeeds in expressing himself in two realms at once",
        8:  "A woman's hat with streamers blown by the east wind",
        9:  "A crystal gazer",
        10: "A teacher gives new symbolic forms to traditional images",
        11: "The president of the country",
        12: "A flock of wild geese",
        13: "A bomb which failed to explode is now safely deactivated",
        14: "A serpent coiling near a man and a woman",
        15: "An Indian weaving a blanket in the peaceful shadow of a wigwam",
        16: "Brownies dancing in the setting sun",
        17: "Two prim spinsters sitting together in silence",
        18: "An empty hammock hung between two trees",
        19: "The magic carpet of Oriental imagery",
        20: "A young girl feeding birds in winter",
        21: "A boxer is entering the ring",
        22: "The gate to the garden of all fulfilled desires",
        23: "A woman in pastel colors carrying a heavy and sacred bag",
        24: "An open window and a net curtain blowing into a cornucopia",
        25: "A double promise reveals its inner and outer working",
        26: "A person possessed of more gifts than she can hold",
        27: "Through imagination a lost opportunity is regained",
        28: "A large disappointed audience",
        29: "The music of the spheres",
        30: "A duck pond and its reflection",
    },
    "Taurus": {
        1:  "A clear mountain stream",
        2:  "An electrical storm",
        3:  "Steps up to a lawn blooming with clover",
        4:  "The rainbow's pot of gold",
        5:  "A widow at an open grave",
        6:  "A cantilever bridge across a deep gorge",
        7:  "The woman of Samaria at the ancestral well",
        8:  "A sleigh without snow",
        9:  "A Christmas tree decorated",
        10: "A Red Cross nurse",
        11: "A woman sprinkling flowers",
        12: "Window shoppers",
        13: "A man handling a mountain full of explosives",
        14: "Shellfish groping and coveting",
        15: "A man muffled up with a scarf",
        16: "An old man attempting vainly to reveal the mysteries",
        17: "A symbolical battle between swords and torches",
        18: "A woman holding a bag out of a window",
        19: "A newly formed continent",
        20: "Wisps of clouds like wings are streaming across the sky",
        21: "A finger pointing to a line in an open book",
        22: "A white dove over troubled waters",
        23: "A jewelry shop",
        24: "An Indian warrior riding fiercely, human scalps hanging at his belt",
        25: "A large well-kept public park",
        26: "A Spaniard serenading his senorita",
        27: "A squaw selling beads",
        28: "A woman past her prime worries lest she be left on the shelf",
        29: "Two cobblers working at a street corner shop",
        30: "A peacock parading on an ancient lawn",
    },
    "Gemini": {
        1:  "A glass-bottomed boat reveals undersea wonders",
        2:  "Santa Claus filling stockings furtively",
        3:  "The garden of the Tuileries",
        4:  "Holly and mistletoe reawaken old memories of Christmas",
        5:  "A radical newspaper",
        6:  "A well with bucket and rope under the shade of majestic trees",
        7:  "An old-fashioned well",
        8:  "Aroused strikers surround a factory",
        9:  "A medieval archer stands with the ease of one wholly sure of himself",
        10: "An aeroplane performing a nosedive",
        11: "Newly opened lands offer the pioneer new possibilities",
        12: "A black double-headed eagle, the seal of a world power",
        13: "Two newlyweds are tying a love knot, two moons glow above the community",
        14: "A telephone conversation carries important news",
        15: "Two Dutch children talking to each other, exchanging their knowledge",
        16: "A woman suffragist orating",
        17: "The head of a youth changes into that of a mature thinker",
        18: "Two Chinese men talking Chinese in a western crowd",
        19: "A large archaic volume reveals a long-forgotten lore",
        20: "A modern cafeteria displays an abundance of food, products of various regions",
        21: "A labor demonstration",
        22: "A barn dance",
        23: "Three fledglings in a nest high in a tree",
        24: "Children skating on ice",
        25: "A man trimming palms",
        26: "Frost-covered trees against winter skies",
        27: "A gypsy coming out of the forest where she had gathered wild herbs",
        28: "A woman pursued by bears",
        29: "The first mocking bird of spring",
        30: "A parade of bathing beauties before large beach crowds",
    },
    "Cancer": {
        1:  "On a ship the sailors lower an old flag and raise a new one",
        2:  "A man alone in a primitive jungle",
        3:  "An arctic explorer leads a reindeer through icy canyons",
        4:  "A cat arguing with a mouse",
        5:  "At a railroad crossing an automobile is wrecked by a train",
        6:  "Game birds feathering their nests",
        7:  "Two fairies on a moonlit night",
        8:  "Rabbits dressed in human clothes walk as a parade",
        9:  "A small naked girl bends over a pond trying to catch a fish",
        10: "A large diamond in the first stages of the cutting process",
        11: "A clown making grimaces",
        12: "A Chinese woman nursing a baby whose aura reveals him to be the reincarnation of a great teacher",
        13: "A hand with a prominent thumb is held out for study",
        14: "A very old man facing a vast dark space to the northeast",
        15: "In a sumptuous dining room guests relax after partaking of a large banquet",
        16: "A man before a square with a manuscript scroll before him",
        17: "The germ grows into knowledge and life",
        18: "A hen scratching the ground to find nutrition for her chicks",
        19: "A priest performing a marriage ceremony",
        20: "Gondoliers in a serenade",
        21: "A prima donna singing",
        22: "A woman awaiting a sailboat",
        23: "The meeting of a literary society",
        24: "A woman and two men castaways on a small island of the south seas",
        25: "A dark shadow or mantle thrown suddenly over the right shoulder",
        26: "Contentment and happiness in luxury, people reading on comfortable hammocks",
        27: "A furious storm in a canyon filled with expensive homes",
        28: "A modern Pocahontas proudly has her photograph taken",
        29: "A Muse weighing twins",
        30: "A daughter of the American Revolution",
    },
    "Leo": {
        1:  "Blood rushes to a man's head as his vital energies are mobilized under the spur of ambition",
        2:  "An epidemic of mumps",
        3:  "A middle-aged woman, her long hair flowing over her shoulders and in a braless youthful garment",
        4:  "A man's formal coat hangs in an empty room",
        5:  "Rock formations tower over a deep canyon",
        6:  "A conservative old-fashioned lady is confronted by a hippie girl",
        7:  "The constellations of stars shine brilliantly in the night sky",
        8:  "A Bolshevik propagandist",
        9:  "Glass blowers shape beautiful vases with their controlled breathing",
        10: "Early morning dew sparkles as sunlight floods the field",
        11: "Children play on a swing hanging from the branches of a huge oak tree",
        12: "An evening lawn party of adults",
        13: "An old sea captain rocking himself on the porch of his cottage",
        14: "The human soul in its eagerness for new experiences seeks embodiment",
        15: "A pageant",
        16: "The storm ended, all nature rejoices in brilliant sunshine",
        17: "A volunteer church choir makes a social event of a rehearsal",
        18: "A chemist conducts an experiment before his students",
        19: "A houseboat party",
        20: "The zeal of youth",
        21: "Chickens intoxicated",
        22: "A carrier pigeon fulfilling its mission",
        23: "A bareback rider",
        24: "Totally concentrated upon inner spiritual attainment, a man sits in complete neglect of bodily appearance and cleanliness",
        25: "A large camel is seen crossing a vast and forbidding desert",
        26: "After the heavy storm, a rainbow",
        27: "Daybreak, the luminescence of dawn in the eastern sky",
        28: "Many little birds on a limb of a large tree",
        29: "A mermaid emerges from the ocean waves ready for rebirth in human form",
        30: "An unsealed letter",
    },
    "Virgo": {
        1:  "In a portrait the best of a man's features and traits are idealized",
        2:  "A large white cross dominates the landscape",
        3:  "Two angels bringing protection",
        4:  "Black and white children play together happily",
        5:  "A man becoming aware of nature spirits and normally unseen spiritual agencies",
        6:  "A merry-go-round",
        7:  "A Ouija board",
        8:  "First dancing instruction",
        9:  "A man making a futurist drawing",
        10: "Two heads looking out and beyond the shadows",
        11: "A boy molded in his mother's aspirations for him",
        12: "A bride with her veil snatched away",
        13: "A strong hand supplanting political hysteria",
        14: "A family tree",
        15: "A fine lace ornamental handkerchief",
        16: "In the zoo children are brought face to face with an orangutan",
        17: "A volcanic eruption",
        18: "Two young people talking quietly and intently, their bodies half submerged in water",
        19: "A swimming race",
        20: "A caravan of cars headed to the west coast",
        21: "A girls' basketball team",
        22: "A royal coat of arms",
        23: "A lion tamer rushes fearlessly into the circus arena",
        24: "Mary and her white lamb",
        25: "A flag at half-mast in front of a public building",
        26: "A boy with a censer serves the priest near the altar",
        27: "Grande dames at a formal party",
        28: "A bald-headed man who has seized power",
        29: "A man is gaining secret knowledge from an ancient scroll he is reading",
        30: "Having an urgent task to complete, a man doesn't look to outward appearances",
    },
    "Libra": {
        1:  "A butterfly made perfect by a dart through it",
        2:  "The transmutation of the fruits of past experiences into the golden gifts of self-expression",
        3:  "The dawn of a new day reveals everything changed",
        4:  "Around a campfire a group of young people sit in spiritual communion",
        5:  "A man teaching the true inner knowledge of the new world to his students",
        6:  "A man watching his ideals taking concrete form before his inner vision",
        7:  "A woman feeding chickens and protecting them from the hawks",
        8:  "A blazing fireplace in a deserted home",
        9:  "Three old masters hanging in a special room of an art gallery",
        10: "A canoe approaching safety through dangerous waters",
        11: "A professor peering over his glasses at his students",
        12: "Miners are emerging from a mine",
        13: "Children blowing soap bubbles",
        14: "A noon siesta",
        15: "Circular paths",
        16: "After a storm a boat landing stands in need of reconstruction",
        17: "A retired sea captain watches ships entering and leaving the harbor",
        18: "Two men placed under arrest",
        19: "A gang of robbers in hiding",
        20: "A rabbi performing his duties",
        21: "A Sunday crowd enjoying the beach",
        22: "A child giving birds a drink at a fountain",
        23: "Chanticleer's voice heralds the rising sun with exuberant tones",
        24: "A third wing on the left side of a butterfly",
        25: "The sight of an autumn leaf brings to a pilgrim the sudden revelation of the mystery of life and death",
        26: "An eagle and a large white dove turning one into the other",
        27: "An airplane sails high in the clear sky",
        28: "A man in the midst of brightening influences",
        29: "Mankind's vast enduring effort to reach for knowledge transferable from generation to generation",
        30: "Three mounds of knowledge on a philosopher's head",
    },
    "Scorpio": {
        1:  "A sightseeing bus",
        2:  "A broken bottle and spilled perfume",
        3:  "A house-raising",
        4:  "A youth carrying a lighted candle",
        5:  "A massive rocky shore",
        6:  "A gold rush",
        7:  "Divers with many trinkets",
        8:  "The moon shining across a lake",
        9:  "Dental work is being done",
        10: "A fellowship supper",
        11: "A drowning man is being rescued",
        12: "An embassy ball",
        13: "An inventor performs a laboratory experiment",
        14: "Telephone linemen at work installing new connections",
        15: "Children playing around five mounds of sand",
        16: "A girl's face breaking into a smile",
        17: "A woman the father of her own child",
        18: "A woods rich with autumn coloring",
        19: "A parrot repeats a conversation he has overheard",
        20: "A woman drawing two dark curtains aside",
        21: "Obeying his conscience a soldier resists orders",
        22: "Hunters starting out for ducks",
        23: "A rabbit metamorphoses into a nature spirit",
        24: "Crowds coming down the mountain to listen to one man",
        25: "An x-ray photograph",
        26: "American Indians making camp after moving into a new territory",
        27: "A military band marches noisily through the city streets",
        28: "The pursuit of happiness in luxurious surroundings",
        29: "An Indian squaw pleading to the chief for the lives of her children",
        30: "The Halloween jester",
    },
    "Sagittarius": {
        1:  "Retired army veterans gather to reawaken old memories",
        2:  "The ocean covered with whitecaps",
        3:  "Two men playing chess",
        4:  "A little child learning to walk with the encouragement of his parents",
        5:  "An old owl up in a tree",
        6:  "A game of cricket",
        7:  "Cupid knocking at the door",
        8:  "Within the depths of the earth new elements are being formed",
        9:  "A mother with her children on stairs",
        10: "A theatrical representation of a golden-haired goddess of opportunity",
        11: "In the left section of an archaic temple, a lamp burns in a container shaped like a human body",
        12: "A flag that turns into an eagle that crows",
        13: "A widow's past is brought to light",
        14: "The pyramids and the sphinx",
        15: "The ground hog looking for its shadow",
        16: "Seagulls fly around a ship in expectation of food",
        17: "An Easter sunrise service draws a large crowd",
        18: "Tiny children in sunbonnets",
        19: "Pelicans moving their habitat",
        20: "In an old-fashioned northern village men cut the ice of a frozen pond for use during the summer",
        21: "A child and a dog wearing borrowed eyeglasses",
        22: "A Chinese laundry",
        23: "Immigrants entering a new country",
        24: "A bluebird standing at the door of the house",
        25: "A chubby boy on a hobby-horse",
        26: "A flag bearer in a battle",
        27: "A sculptor at his work",
        28: "An old bridge over a beautiful stream is still in constant use",
        29: "A fat boy mowing the lawn",
        30: "The Pope blessing the faithful",
    },
    "Capricorn": {
        1:  "An Indian chief claims power from the assembled tribe",
        2:  "Three stained-glass windows in a gothic church, one damaged by war",
        3:  "The human soul receptive to growth and understanding",
        4:  "A group of people outfitting a large canoe at the start of a journey by water",
        5:  "Indians rowing a canoe and dancing a war dance",
        6:  "Ten logs lie under an archway leading to darker woods",
        7:  "A veiled prophet speaks seized by the power of a god",
        8:  "Birds in the house singing happily",
        9:  "An angel carrying a harp",
        10: "An albatross feeding from the hand of a sailor",
        11: "Pheasants display their brilliant plumage on a private estate",
        12: "A student of nature lecturing, revealing little-known aspects of life",
        13: "A fire worshipper meditates on the ultimate realities of existence",
        14: "An ancient bas-relief carved in granite remains a witness to a long-forgotten culture",
        15: "Many toys in the children's ward of a hospital",
        16: "School grounds filled with boys and girls in gymnasium suits",
        17: "A repressed woman finds a psychological release in nudism",
        18: "The Union Jack flag flies from a British warship",
        19: "A child of about five with a huge shopping bag",
        20: "A hidden choir is singing during a religious service",
        21: "A relay race",
        22: "A general accepting defeat gracefully",
        23: "A soldier receiving two awards for bravery in combat",
        24: "A woman entering a convent",
        25: "An oriental rug dealer in a store filled with precious ornamental rugs",
        26: "A nature spirit dancing in the mist of a waterfall",
        27: "A mountain pilgrimage",
        28: "A large aviary",
        29: "A woman reading tea leaves",
        30: "A secret business conference",
    },
    "Aquarius": {
        1:  "An old adobe mission in California",
        2:  "An unexpected thunderstorm",
        3:  "A deserter from the navy",
        4:  "A Hindu pundit reveals his wisdom to a group of disciples",
        5:  "A council of ancestors is seen implementing the efforts of a young leader",
        6:  "A performer of a mystery play",
        7:  "A child born of an egghead parents is aided in his development by a guide",
        8:  "Beautifully gowned wax figures on display",
        9:  "A flag is seen turning into an eagle",
        10: "A popularity that proves ephemeral",
        11: "During a silent hour, a man receives a new inspiration which may change his life",
        12: "People on stairs graduating upwards",
        13: "A barometer",
        14: "A train entering a tunnel",
        15: "Two lovebirds sitting on a fence and singing happily",
        16: "A big businessman at his desk",
        17: "A watchman stands guard, protecting the interests of a large corporation",
        18: "A man unmasked",
        19: "A forest fire is being subdued by the use of water, chemicals and the collective efforts of many people",
        20: "A large white dove bearing a message",
        21: "A woman disappointed and disillusioned, courageously faces a seemingly empty life",
        22: "A rug placed on a floor for children to play",
        23: "A big bear sitting down and waving all its paws",
        24: "A man turning his back on his passions, teaches from his experience",
        25: "A butterfly with the right wing more perfectly formed",
        26: "A garage man testing a car's battery with a hydrometer",
        27: "An ancient pottery bowl filled with fresh violets",
        28: "A tree felled and sawed to ensure a supply of wood for the winter",
        29: "Butterfly emerging from a chrysalis",
        30: "Deeply rooted in the past of a very ancient culture, a spiritual brotherhood in which many individual minds are merged into the glowing light of a common ideal",
    },
    "Pisces": {
        1:  "In a crowded marketplace farmers and middlemen display a great variety of products",
        2:  "A squirrel hiding from hunters",
        3:  "A petrified forest",
        4:  "Heavy traffic on a narrow isthmus",
        5:  "A church bazaar",
        6:  "A parade of army officers in full dress",
        7:  "Illumined by a shaft of light, a large cross lies on rocks surrounded by sea and mist",
        8:  "A girl blowing a bugle",
        9:  "A jockey",
        10: "An aviator in the clouds",
        11: "Men traveling a narrow path, seeking illumination",
        12: "In the sanctuary of an occult brotherhood, newly initiated members are being examined and their character tested",
        13: "A sword in a museum",
        14: "A lady in fox fur",
        15: "An officer preparing men for a long journey by airplane",
        16: "In the quiet of his study a creative individual experiences a flow of inspiration",
        17: "An Easter promenade",
        18: "In a gigantic tent villagers witness a spectacular performance",
        19: "A master instructing his disciple",
        20: "A table set for an evening meal",
        21: "Under the watchful and kind eyes of a Chinese servant, a girl fondles a little white lamb",
        22: "A man bringing down the new law from Sinai",
        23: "Spiritist phenomena",
        24: "An inhabited island",
        25: "The purging of the priesthood",
        26: "Watching the very thin moon crescent appearing at sunset, different people realize that the time has come to go ahead with their different projects",
        27: "The harvest moon illuminates a clear autumnal sky",
        28: "A fertile garden under the full moon",
        29: "Light breaking into many colors as it passes through a prism",
        30: "The great stone face",
    },
}


def get_symbol_number(degree_within_sign_float):
    """
    Convert a float degree position within a sign (0.0 to 29.999...) to
    the Sabian Symbol number (1-30).

    Rounding rule: 0 minutes exactly = use that degree.
                   ANY minutes past the degree = round up.
    """
    whole = int(degree_within_sign_float)
    minutes = (degree_within_sign_float - whole) * 60
    if minutes < 0.001:
        symbol_num = whole if whole > 0 else 1
    else:
        symbol_num = whole + 1
    return min(max(symbol_num, 1), 30)


def get_sabian_symbol(sign, degree_within_sign_float):
    """
    Return the Sabian Symbol image text for a given sign and degree.

    Args:
        sign: Sign name string e.g. "Aries", "Taurus"
        degree_within_sign_float: Decimal degrees within the sign (0.0 to 29.999)

    Returns:
        dict with keys: symbol_number, image, sign, degree_label
    """
    sign_key = sign.strip().capitalize()
    if sign_key not in SABIAN_SYMBOLS:
        return {"error": f"Unknown sign: {sign}"}

    num = get_symbol_number(degree_within_sign_float)
    image = SABIAN_SYMBOLS[sign_key].get(num, "Symbol not found")
    degree_int = int(degree_within_sign_float)
    minutes = int(round((degree_within_sign_float - degree_int) * 60))

    return {
        "symbol_number": num,
        "image": image,
        "sign": sign_key,
        "degree_label": f"{sign_key} {degree_int}°{minutes:02d}'",
    }


def parse_planet_position(position_str):
    """
    Parse a position string like 'Pisces 2.92 House 2' or 'Gemini 27.85 Rx'.
    Returns (sign, degree_within_sign_float) or None if unparseable.
    """
    if not position_str:
        return None
    parts = position_str.strip().split()
    if len(parts) < 2:
        return None
    sign = parts[0]
    try:
        degree = float(parts[1].replace('°', ''))
        return sign, degree
    except (ValueError, IndexError):
        return None


def get_sabian_for_chart(planets):
    """
    Get Sabian Symbols for a dict of planets.

    Args:
        planets: dict of {planet_name: position_string}
                 e.g. {"sun": "Aries 18.95", "moon": "Pisces 2.92 House 2"}

    Returns:
        dict of {planet_name: sabian_result}
    """
    results = {}
    for planet, pos_str in planets.items():
        parsed = parse_planet_position(pos_str)
        if parsed:
            sign, degree = parsed
            results[planet] = get_sabian_symbol(sign, degree)
        else:
            results[planet] = {"error": f"Could not parse position: {pos_str}"}
    return results


def register_sabian_route(app):
    @app.route('/sabian-symbols', methods=['POST'])
    def sabian_symbols():
        """
        POST body: { "planets": { "sun": "Aries 18.95", "moon": "Pisces 2.92 House 2", ... } }
        Returns: { "sun": { "symbol_number": 19, "image": "...", "sign": "Aries", "degree_label": "Aries 18°57'" }, ... }
        """
        data = request.get_json(force=True, silent=True) or {}
        planets = data.get('planets', {})
        if not planets:
            return jsonify({"error": "No planets provided"}), 400
        results = get_sabian_for_chart(planets)
        return jsonify(results)
