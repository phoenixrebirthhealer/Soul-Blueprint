from flask import request, jsonify


def parse_sign(planet_str):
    """Extract sign name from 'Pisces 2.92° House 2' format."""
    if not planet_str:
        return ''
    return planet_str.strip().split()[0]


def hd_type_content(hd_type):
    t = (hd_type or '').strip().lower()
    if 'manifestor' in t and 'manifesting' not in t:
        return (
            "As a Manifestor, your nervous system is wired to initiate and when survival mode "
            "sets in, that initiating energy turns inward. You may feel an urgency to force outcomes, "
            "to push through walls that were never yours to break. Your Rebirth path here is not to "
            "stop initiating. It is to learn which initiations come from peace, and which come from fear. "
            "Survival mode for a Manifestor often looks like control, isolation, or burning it all down "
            "before anyone else can. You were not built to do this alone, and your design confirms it: "
            "informing others before you act is not a weakness. It is the circuit breaker for the survival loop."
        )
    elif 'manifesting generator' in t or ('generator' in t and 'manifesting' in t):
        return (
            "As a Manifesting Generator, your energy is built for multi-directional momentum and in "
            "survival mode, that momentum becomes scattered urgency. You may take on too much, burn out, "
            "pivot without grounding, or feel like you are always behind. Your Rebirth path is not to slow "
            "down your energy. It is to let your body, not your mind, choose what gets your power. "
            "Survival mode for a Manifesting Generator often looks like doing everything for everyone except "
            "yourself. The data in this reading exists to show you where your sacred 'yes' actually lives."
        )
    elif 'generator' in t:
        return (
            "As a Generator, your life force is the most sustainable on the planet and survival mode "
            "hijacks it. Instead of responding from genuine resonance, you start saying yes from fear, "
            "obligation, or the belief that your worth lives in your output. Your Rebirth path is not to "
            "produce less. It is to restore the sacred circuit between what lights up your body and what "
            "receives your energy. Survival mode for a Generator often looks like exhaustion that makes "
            "no sense on paper, or a life that looks full from the outside but feels hollow within."
        )
    elif 'projector' in t:
        return (
            "As a Projector, you were designed to see deeply and guide efficiently and survival mode "
            "distorts that gift into bitterness or over-giving to earn recognition. You may push yourself "
            "into spaces that were never meant to invite you, trying to prove your value through effort "
            "rather than waiting for the invitation that honors your sight. Your Rebirth path is not to "
            "become smaller. It is to trust that the right invitations appear when you are rested and "
            "visible as yourself. Survival mode for a Projector often looks like chronic fatigue from "
            "doing what Generators do, and an ache of not being truly seen."
        )
    elif 'reflector' in t:
        return (
            "As a Reflector, you are the rarest design, built to sample and reflect the health of your "
            "environment. In survival mode, you lose the boundary between what is yours and what you have "
            "absorbed from others. You may feel like you do not know who you are without the people around "
            "you, or like the world's pain has become indistinguishable from your own. Your Rebirth path "
            "is not to stop feeling. It is to restore the sacred space between you and what you reflect. "
            "Survival mode for a Reflector often looks like shapeshifting to survive, with no felt sense "
            "of a stable core self underneath."
        )
    return (
        "Your Human Design type carries a specific geometry for how your energy moves through the world "
        "and survival mode interrupts that geometry. The patterns in this reading are designed to show you "
        "where your original wiring was rerouted by survival, and how to begin restoring the authentic flow "
        "your design was built for."
    )


def hd_authority_content(hd_authority):
    a = (hd_authority or '').strip().lower()
    if 'emotional' in a:
        return (
            "Your Emotional Authority means your clarity arrives in waves, not in a single moment. "
            "Survival mode collapses that wave into urgency, forcing decisions before the emotional "
            "cycle has moved through. You may recognize this as choices made in the height of pain or "
            "the height of hope, both of which tend to create regret. Your Rebirth here is to restore "
            "trust in the wave itself. You do not need to decide right now. Clarity is coming."
        )
    elif 'sacral' in a:
        return (
            "Your Sacral Authority speaks in gut sounds and body responses, not in words. Survival mode "
            "silences the body and amplifies the mind, teaching you to override your gut with logic, "
            "fear, or others' expectations. You may have spent years doing things your sacral never "
            "actually said yes to. Your Rebirth here is to slow down enough to hear the body again. "
            "The gut knows before the mind catches up, and it always has."
        )
    elif 'splenic' in a:
        return (
            "Your Splenic Authority speaks once, quietly, in the present moment. Survival mode teaches "
            "you to distrust that quiet knowing, to second-guess the instinct, wait for more data, or "
            "talk yourself out of what your body already knew. You may recognize this as a pattern of "
            "ignoring the first signal and paying for it later. Your Rebirth here is to practice "
            "honoring the first knowing before the noise of survival drowns it out."
        )
    elif 'ego' in a or 'heart' in a:
        return (
            "Your Ego Authority is rooted in your heart's willpower and survival mode depletes that "
            "resource by spending it on what you do not actually want. You may find yourself making "
            "promises your heart was never behind, or pushing through when every part of you is "
            "signaling stop. Your Rebirth here is to restore the sacred 'no' that protects what you "
            "actually have the heart to build."
        )
    elif 'self' in a or 'identity' in a or 'g center' in a:
        return (
            "Your Self-Projected Authority speaks through your own voice. You find your truth by "
            "talking it out with trusted others. Survival mode isolates you, cutting off the very "
            "process through which your clarity emerges. You may find yourself stuck in loops that "
            "resolve the moment you speak them aloud to someone safe. Your Rebirth here is to restore "
            "the trusted circle your design actually requires."
        )
    elif 'mental' in a or 'outer' in a or 'environment' in a:
        return (
            "Your Mental/Environmental Authority means your clarity comes from being in the right "
            "environment and talking through decisions with trusted others. Survival mode contracts "
            "your world, limiting both environment and connection. You may feel chronically confused "
            "or unable to decide because you have been trying to find clarity in isolation. Your "
            "Rebirth here is to notice which environments and which people genuinely help you think."
        )
    elif 'lunar' in a or 'moon' in a:
        return (
            "Your Lunar Authority means you need a full lunar cycle, approximately 28 days, to "
            "reach clarity on significant decisions. Survival mode is incompatible with this design: "
            "it demands immediate answers, immediate action, immediate certainty. You may have spent "
            "years forcing decisions at a speed your design was never built to sustain. Your Rebirth "
            "here is to give yourself time as an act of self-respect, not avoidance."
        )
    return (
        "Your inner authority is the decision-making mechanism your design was built around and "
        "survival mode systematically overrides it. Part of your Rebirth path is learning to "
        "distinguish between the voice of your design and the voice of survival. They are not the same."
    )


def moon_content(moon_sign):
    sign = parse_sign(moon_sign)
    s = sign.lower()
    elements = {
        'aries': 'fire', 'leo': 'fire', 'sagittarius': 'fire',
        'taurus': 'earth', 'virgo': 'earth', 'capricorn': 'earth',
        'gemini': 'air', 'libra': 'air', 'aquarius': 'air',
        'cancer': 'water', 'scorpio': 'water', 'pisces': 'water',
    }
    elem = elements.get(s, '')

    sign_map = {
        'aries': (
            "Your Moon in Aries carries an emotional body built for boldness and in survival mode, "
            "that boldness becomes reactivity. You may move fast through feelings before they have "
            "been processed, or anger may show up as the surface emotion protecting deeper hurt. "
            "Your emotional Rebirth is not to slow your fire. It is to let the fire burn through "
            "the wound rather than away from it."
        ),
        'taurus': (
            "Your Moon in Taurus needs safety, stability, and physical comfort to feel emotionally "
            "resourced and survival mode strips all three. You may have learned to emotionally "
            "shut down when those needs cannot be met, creating a numbness that feels like strength "
            "but is actually protection. Your emotional Rebirth is restoring the body's right to "
            "feel safe before it can open."
        ),
        'gemini': (
            "Your Moon in Gemini processes emotion through language and thought and survival mode "
            "turns that into anxiety loops, overthinking, or speaking before feeling. You may "
            "recognize this as talking about your emotions without ever quite landing in them. "
            "Your emotional Rebirth is learning to let the feeling arrive before you name it."
        ),
        'cancer': (
            "Your Moon in Cancer places you in the sign it rules, emotionally deep, intuitive, and "
            "deeply attuned to others. Survival mode amplifies that attunement into hypervigilance, "
            "reading every room for emotional safety before you allow yourself to be present. "
            "Your emotional Rebirth is learning to feel the difference between genuine intuition "
            "and fear-based scanning."
        ),
        'leo': (
            "Your Moon in Leo needs to feel seen and loved, genuinely, not performatively. Survival "
            "mode may have taught you that love is conditional, requiring performance to be maintained. "
            "You may give more than you receive in order to keep love in place. Your emotional Rebirth "
            "is learning to receive love that does not require you to earn it in real time."
        ),
        'virgo': (
            "Your Moon in Virgo processes emotion through analysis and survival mode turns that into "
            "self-criticism, hypervigilance about what is wrong, or a constant sense that you are not "
            "doing enough. You may struggle to feel emotionally settled unless everything around you "
            "is in order. Your emotional Rebirth is learning that your inner world is not a problem "
            "to be solved."
        ),
        'libra': (
            "Your Moon in Libra needs harmony and fairness to feel emotionally safe and survival mode "
            "may have taught you to suppress your own needs to maintain that harmony. You may be "
            "exceptionally skilled at managing others' feelings while privately feeling unseen. "
            "Your emotional Rebirth is learning that your peace does not require others' approval."
        ),
        'scorpio': (
            "Your Moon in Scorpio carries emotional depth that most people never touch and survival "
            "mode either seals that depth behind walls or pulls you into emotional intensity without "
            "a way out. You may cycle between complete emotional shutdown and overwhelming feeling. "
            "Your emotional Rebirth is learning to trust the descent, knowing you are built to "
            "survive what you feel."
        ),
        'sagittarius': (
            "Your Moon in Sagittarius needs freedom, meaning, and expansion to feel emotionally alive "
            "and survival mode contracts all three. You may cope by moving, seeking, or escaping into "
            "philosophy or adventure rather than landing in what is actually hurting. Your emotional "
            "Rebirth is learning that stillness is not a cage. It is where the truth you are looking "
            "for has been waiting."
        ),
        'capricorn': (
            "Your Moon in Capricorn was shaped by a belief that emotional needs are either a burden "
            "or a liability. Survival mode reinforces this by demanding productivity and composure "
            "above all. You may not know how to ask for emotional support without it feeling like "
            "weakness. Your emotional Rebirth is learning that needing is not failing. It is the "
            "most honest thing a human can do."
        ),
        'aquarius': (
            "Your Moon in Aquarius processes emotion with detachment, a gift that in survival mode "
            "becomes dissociation. You may observe your feelings from a distance, intellectualizing "
            "what should be felt. You may feel most emotionally comfortable in groups but profoundly "
            "lonely one-to-one. Your emotional Rebirth is learning to let yourself be moved rather "
            "than managed."
        ),
        'pisces': (
            "Your Moon in Pisces is one of the most empathically porous placements in the chart. "
            "Survival mode turns that porousness into dissolution. You absorb others' pain as your "
            "own, lose yourself in relationships, or escape into fantasy to survive what feels too "
            "large. Your emotional Rebirth is learning where you end and another begins, and that "
            "the boundary does not make you less loving."
        ),
    }

    sign_text = sign_map.get(s)
    if sign_text:
        return sign_text

    elem_map = {
        'fire': (
            "Your Moon in a fire sign carries emotional energy that moves fast and burns bright and "
            "survival mode either extinguishes that fire or lets it burn without direction. "
            "Your emotional Rebirth involves reclaiming the warmth of your emotional life without "
            "letting it consume you or the people you love."
        ),
        'earth': (
            "Your Moon in an earth sign grounds emotion in the body and in the material world and "
            "survival mode may have taught you that slowing down to feel is a luxury you cannot "
            "afford. Your emotional Rebirth is learning that your body was always trying to tell you "
            "what your mind had learned to override."
        ),
        'air': (
            "Your Moon in an air sign processes emotion through thought and communication and "
            "survival mode turns that into chronic mental loops that substitute for actually feeling. "
            "Your emotional Rebirth is learning to move from analysis of the feeling into the "
            "feeling itself."
        ),
        'water': (
            "Your Moon in a water sign means your emotional body is deep, intuitive, and highly "
            "permeable and survival mode likely taught you that this depth was too much, for you "
            "or for others. Your emotional Rebirth is learning to trust the depth as data rather "
            "than as danger."
        ),
    }
    return elem_map.get(elem, (
        "Your Moon sign carries the emotional blueprint of how you learned to feel and survive. "
        "What emerges in this reading is a map back to your emotional body as it was designed to "
        "function, before survival rewired the circuit."
    ))


def nodes_content(north_sign, south_sign):
    n = (north_sign or '').strip().lower()
    s_node = (south_sign or '').strip().lower()

    node_themes = {
        'aries': 'self-sovereignty and courageous initiation',
        'taurus': 'embodied safety and self-worth',
        'gemini': 'curiosity, communication, and present-moment connection',
        'cancer': 'emotional safety, nurturing, and belonging',
        'leo': 'authentic self-expression and creative courage',
        'virgo': 'discernment, integration, and sacred service',
        'libra': 'partnership, reciprocity, and relational harmony',
        'scorpio': 'depth, transformation, and emotional truth',
        'sagittarius': 'expansion, meaning, and philosophical freedom',
        'capricorn': 'mastery, integrity, and earned authority',
        'aquarius': 'collective vision, authenticity, and innovation',
        'pisces': 'surrender, compassion, and spiritual trust',
    }

    north_theme = node_themes.get(n, 'your evolutionary edge')
    south_theme = node_themes.get(s_node, 'your comfort zone of origin')

    return (
        f"Your North Node in {north_sign.capitalize() if north_sign else 'its sign'} points toward "
        f"{north_theme} as your soul's evolutionary direction in this lifetime. "
        f"Your South Node in {south_sign.capitalize() if south_sign else 'its sign'} shows the pattern of "
        f"{south_theme}, the familiar territory your nervous system returns to under stress. "
        "Survival mode is almost always a South Node story: you retreat to what is known because the "
        "North Node path requires a courage your nervous system has not yet learned to trust. "
        "This reading exists to show you that the direction your soul came here to grow into is not "
        "reckless. It is the most stabilizing move available to you."
    )


def attachment_content(attachment_style):
    style_map = {
        'pure avoidant': (
            "Your attachment pattern shows a Pure Avoidant design, meaning your nervous system "
            "learned that closeness was a threat. You may have become extraordinarily self-sufficient "
            "as a survival strategy, building walls that look like independence but feel like isolation. "
            "Vulnerability may trigger a physiological alarm that reads as danger even when the person "
            "in front of you is safe. Your Rebirth here is not to dismantle your self-sufficiency. "
            "It is to learn that closeness and safety can exist in the same space, something your "
            "nervous system has not yet had enough evidence of."
        ),
        'pure anxious': (
            "Your attachment pattern shows a Pure Anxious design, meaning your nervous system learned "
            "that love was inconsistent, and hypervigilance became the strategy for holding onto it. "
            "You may monitor connection for signs of abandonment, over-give to ensure you are not left, "
            "or feel a chronic low hum of 'not enough' regardless of how much reassurance you receive. "
            "Your Rebirth here is not to need less. It is to learn that stability can be real, that "
            "you do not have to earn your place in love every day."
        ),
        'pure disorganized': (
            "Your attachment pattern shows a Pure Disorganized design, meaning the people who were "
            "meant to be safe were also a source of fear. Your nervous system learned to want closeness "
            "and fear it simultaneously, creating an internal conflict that no relationship strategy "
            "can fully resolve from the outside. You may feel safest alone while aching for connection. "
            "Your Rebirth here is not to choose one over the other. It is to slowly, carefully teach "
            "your body that it is possible to be both connected and safe at the same time."
        ),
        'disorganized anxious leaning': (
            "Your attachment pattern carries a Disorganized foundation with an Anxious lean, meaning "
            "your nervous system both fears closeness and pursues it intensely, often in the same moment. "
            "You may find yourself drawn to people who are inconsistent, mistaking the familiar tension "
            "for chemistry or depth. Your Rebirth here is not about finding the right person. "
            "It is about interrupting the pattern long enough to recognize what safety actually feels "
            "like in a body that has never fully known it."
        ),
        'disorganized avoidant leaning': (
            "Your attachment pattern carries a Disorganized foundation with an Avoidant lean, meaning "
            "your nervous system protects itself most often through withdrawal, while underneath there "
            "is a deep hunger for real connection. You may have learned that the safest version of "
            "love is the kind you never fully let in. Your Rebirth here is not to force open what "
            "learned to close for good reason. It is to slowly widen the window of what your body "
            "will allow to matter."
        ),
        'true disorganized equal split': (
            "Your attachment pattern shows a True Disorganized Equal Split, meaning your nervous "
            "system is equally activated by both the pull toward and the retreat from connection. "
            "You may feel like you are in constant contradiction with yourself: wanting to be seen "
            "and terrified of what that costs, reaching for love and pulling back before it can reach "
            "you. Your Rebirth here is not to resolve the contradiction by choosing a side. "
            "It is to hold both truths with compassion and let them coexist while the nervous system "
            "slowly learns a new story."
        ),
    }
    key = (attachment_style or '').strip().lower()
    return style_map.get(key, (
        "Your attachment pattern reflects a specific way your nervous system learned to relate to "
        "love, safety, and connection under conditions that required adaptation. Survival mode and "
        "attachment wiring are deeply intertwined and this reading is one part of the larger "
        "Rebirth work of teaching your nervous system that it is safe to show up differently now."
    ))


def life_path_content(life_path):
    lp_map = {
        1: (
            "Your Life Path 1 carries the frequency of the pioneer and survival mode turns that "
            "pioneering energy into isolation, the belief that you must do everything yourself because "
            "no one else will do it right, or won't be there when it matters. You may have learned "
            "that depending on others leads to disappointment. Your Rebirth is not to stop leading. "
            "It is to learn that genuine leaders can receive support without losing their authority."
        ),
        2: (
            "Your Life Path 2 carries the frequency of sacred partnership and sensitivity and "
            "survival mode turns that sensitivity into self-erasure, giving yourself away to maintain "
            "peace or connection. You may have learned that your needs are secondary, or that harmony "
            "requires your silence. Your Rebirth is learning that your presence, not your compliance, "
            "is what creates the connection your soul came here for."
        ),
        3: (
            "Your Life Path 3 carries the frequency of creative expression and joy and survival "
            "mode suppresses the voice, silences the art, or turns creativity into performance rather "
            "than truth. You may have learned that full expression is unsafe, that your joy is too "
            "much, or that being seen comes with a cost. Your Rebirth is reclaiming the creative "
            "channel as the sacred portal it was always meant to be."
        ),
        4: (
            "Your Life Path 4 carries the frequency of foundational stability and survival mode "
            "turns that into rigidity, control, or working harder than is sustainable to create "
            "security from the outside in. You may have learned that safety must be built by hand "
            "and held tightly. Your Rebirth is discovering that inner stability is not constructed "
            "through effort alone. It is cultivated through trust."
        ),
        5: (
            "Your Life Path 5 carries the frequency of freedom and direct experience and survival "
            "mode turns that freedom-seeking into escape, constant motion, or avoiding depth to "
            "prevent feeling trapped. You may have learned that commitment equals confinement. "
            "Your Rebirth is discovering that true freedom includes the freedom to stay, to deepen, "
            "to build something that cannot be dismantled by fear."
        ),
        6: (
            "Your Life Path 6 carries the frequency of responsibility, beauty, and care and "
            "survival mode turns that into perfectionism, over-responsibility for others, or the "
            "belief that your worth is tied to how well you serve. You may have difficulty receiving "
            "care without it feeling uncomfortable or unearned. Your Rebirth is learning that you "
            "were not put here to be everyone's solution. You were put here to be whole."
        ),
        7: (
            "Your Life Path 7 carries the frequency of the seeker, internal, analytical, and "
            "spiritually attuned. Survival mode turns that seeking inward into isolation, the "
            "belief that no one truly understands you, or an intellectual fortress built to keep "
            "vulnerability out. You may process pain alone and call it self-sufficiency. "
            "Your Rebirth is discovering that being truly known by even one person is not a threat "
            "to your interior world. It is Rebirth for it."
        ),
        8: (
            "Your Life Path 8 carries the frequency of power, abundance, and mastery and survival "
            "mode either amplifies that into controlling behavior or collapses it into powerlessness "
            "and lack. You may have a complex relationship with authority: drawn to it, afraid of it, "
            "or fighting it in yourself and others. Your Rebirth is learning that genuine power is "
            "not taken or defended. It is embodied, from the inside out."
        ),
        9: (
            "Your Life Path 9 carries the frequency of completion, wisdom, and universal compassion "
            "and survival mode turns that compassion outward so relentlessly that the self goes "
            "unattended. You may have the capacity to hold space for everyone else's transformation "
            "while quietly suffering in your own. Your Rebirth is turning the same depth of "
            "compassion you give to the world back toward yourself, without it feeling like betrayal."
        ),
        11: (
            "Your Life Path 11 is a Master Number, never reduced, carrying the frequency of the "
            "illuminated channel, the one whose sensitivity is itself the gift. Survival mode in an "
            "11 can look like chronic overwhelm, shutting down the very channel through which your "
            "highest work flows, or being pulled between spiritual clarity and human doubt. "
            "Your Rebirth is learning to hold both the human and the illuminated without collapsing "
            "one to survive the other."
        ),
        22: (
            "Your Life Path 22 is a Master Number, never reduced, carrying the frequency of the "
            "master builder, the one who incarnated to make something real and lasting from vision. "
            "Survival mode in a 22 often manifests as paralysis: the weight of what you sense you "
            "are here to build becomes a pressure so large that nothing moves. Your Rebirth is "
            "learning that the architecture of your purpose can only be built one brick at a time, "
            "and that beginning is not betrayal of the scale of the vision."
        ),
        33: (
            "Your Life Path 33 is a Master Number, never reduced, carrying the frequency of the "
            "master teacher, the one whose love is both the lesson and the transmission. Survival "
            "mode in a 33 often manifests as martyrdom: giving everything to others as a way of "
            "avoiding the terrifying intimacy of receiving. Your Rebirth is learning that you cannot "
            "teach what you have not allowed yourself to embody, and that your own wholeness is "
            "not a detour from your purpose. It is the purpose."
        ),
    }
    try:
        lp_int = int(life_path)
    except (TypeError, ValueError):
        lp_int = None
    return lp_map.get(lp_int, (
        "Your Life Path number carries the primary frequency your soul chose for this incarnation "
        "and survival mode is always in tension with that frequency, pulling you toward what is "
        "known and away from what you came here to become. This reading is one activation point "
        "in the longer arc of returning to your original design."
    ))


def self_love_range_content(score, result):
    r = (result or '').strip().lower()
    try:
        score_int = int(score)
    except (TypeError, ValueError):
        score_int = None

    if score_int is not None and score_int <= 33:
        return (
            "Your Self-Love score places you in the Low range and that is not a verdict, it is a "
            "starting point. What this score reflects is a nervous system that has been running on "
            "survival for long enough that self-care, self-compassion, and self-regard have become "
            "unfamiliar, unsafe, or simply inaccessible. This is not a character flaw. It is a "
            "pattern, and patterns can be interrupted. The work ahead is not about being harder on "
            "yourself about how much you have neglected yourself. It is about beginning, one small "
            "act at a time, to become someone your own nervous system trusts."
        )
    elif r == 'emerging' or (score_int is not None and 34 <= score_int <= 50):
        return (
            "Your Self-Love score is in the Emerging range, meaning the foundation exists, but it "
            "is not yet stable enough to hold you through the harder moments. You may have moments "
            "of genuine self-regard followed by collapse back into old patterns when stress arrives. "
            "This is not inconsistency. It is the natural rhythm of emergence. Your Rebirth here "
            "is not to rush the growth. It is to notice what conditions allow self-love to be "
            "present, and to deliberately return to those conditions more often."
        )
    elif r == 'developing' or (score_int is not None and 51 <= score_int <= 67):
        return (
            "Your Self-Love score is in the Developing range, meaning you have built real capacity "
            "here, but there are still places where survival patterns override your own knowing. "
            "You may notice the difference between how you treat yourself in good periods versus "
            "under pressure. Your Rebirth here is not to work harder at self-love. It is to close "
            "the gap between what you know about yourself and how you actually act on your own behalf "
            "when it costs something."
        )
    return (
        "Your Self-Love score reflects where your capacity for self-regard, self-trust, and "
        "self-compassion currently lives and that score exists within a system that was designed, "
        "often unconsciously, to route resources toward survival rather than toward thriving. "
        "This reading exists to begin interrupting that design."
    )


def generate_survival_mode_html(
    client_name,
    hd_type,
    hd_authority,
    moon,
    north_node,
    south_node,
    life_path,
    attachment_style,
    self_love_score,
    self_love_result,
):
    north_sign = parse_sign(north_node)
    south_sign = parse_sign(south_node)
    display_name = (client_name or '').strip() or 'Beloved'

    section_hd_type = hd_type_content(hd_type)
    section_authority = hd_authority_content(hd_authority)
    section_moon = moon_content(moon)
    section_nodes = nodes_content(north_sign, south_sign)
    section_attachment = attachment_content(attachment_style)
    section_life_path = life_path_content(life_path)
    section_self_love = self_love_range_content(self_love_score, self_love_result)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Overcoming Survival Mode - {display_name}</title>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet" />
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #ffffff;
      color: #2d1054;
      font-family: 'Lora', Georgia, serif;
      font-size: 15px;
      line-height: 1.85;
      padding: 48px 40px;
      max-width: 820px;
      margin: 0 auto;
    }}
    h1 {{
      font-family: 'Cinzel', serif;
      font-size: 28px;
      font-weight: 700;
      color: #2d1054;
      text-align: center;
      letter-spacing: 0.06em;
      margin-bottom: 6px;
    }}
    h2 {{
      font-family: 'Cinzel', serif;
      font-size: 15px;
      font-weight: 400;
      color: #c2185b;
      text-align: center;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      margin-bottom: 32px;
    }}
    .divider {{
      border: none;
      border-top: 1px solid #d4af37;
      margin: 28px 0;
    }}
    .opening {{
      font-style: italic;
      font-size: 16px;
      color: #2d1054;
      text-align: center;
      line-height: 1.9;
      margin-bottom: 36px;
      padding: 0 24px;
    }}
    .section {{
      margin-bottom: 36px;
    }}
    .section-label {{
      font-family: 'Cinzel', serif;
      font-size: 11px;
      font-weight: 600;
      color: #d4af37;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      margin-bottom: 8px;
    }}
    .section-title {{
      font-family: 'Cinzel', serif;
      font-size: 17px;
      font-weight: 600;
      color: #2d1054;
      margin-bottom: 12px;
    }}
    .section-body {{
      color: #2d1054;
      font-size: 15px;
      line-height: 1.85;
    }}
    .closing {{
      background: #fdf8ff;
      border: 1px solid #d4af37;
      border-radius: 4px;
      padding: 28px 32px;
      margin-top: 40px;
    }}
    .closing-title {{
      font-family: 'Cinzel', serif;
      font-size: 14px;
      font-weight: 600;
      color: #c2185b;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      margin-bottom: 12px;
    }}
    .closing-body {{
      font-style: italic;
      color: #2d1054;
      font-size: 15px;
      line-height: 1.9;
    }}
    .footer {{
      text-align: center;
      font-family: 'Cinzel', serif;
      font-size: 11px;
      color: #c2185b;
      letter-spacing: 0.14em;
      margin-top: 48px;
      padding-top: 20px;
      border-top: 1px solid #d4af37;
    }}
  </style>
</head>
<body>

  <h1>Overcoming Survival Mode</h1>
  <h2>A Personalized Rebirth Activation for {display_name}</h2>

  <hr class="divider" />

  <div class="opening">
    In case you have ever felt like you are running on survival mode,<br />
    this was created specifically for you based on your data.<br /><br />
    What follows is not advice. It is activation.<br />
    Seven reflections drawn directly from your Soul Blueprint,<br />
    each one a point of entry back to the life your design was built for.
  </div>

  <hr class="divider" />

  <div class="section">
    <div class="section-label">Human Design</div>
    <div class="section-title">Your Energy Type in Survival</div>
    <div class="section-body">{section_hd_type}</div>
  </div>

  <hr class="divider" />

  <div class="section">
    <div class="section-label">Human Design</div>
    <div class="section-title">Your Inner Authority in Survival</div>
    <div class="section-body">{section_authority}</div>
  </div>

  <hr class="divider" />

  <div class="section">
    <div class="section-label">Astrology</div>
    <div class="section-title">Your Moon in Survival</div>
    <div class="section-body">{section_moon}</div>
  </div>

  <hr class="divider" />

  <div class="section">
    <div class="section-label">Astrology</div>
    <div class="section-title">Your Nodal Axis in Survival</div>
    <div class="section-body">{section_nodes}</div>
  </div>

  <hr class="divider" />

  <div class="section">
    <div class="section-label">Attachment Wiring</div>
    <div class="section-title">Your Attachment Pattern in Survival</div>
    <div class="section-body">{section_attachment}</div>
  </div>

  <hr class="divider" />

  <div class="section">
    <div class="section-label">Numerology</div>
    <div class="section-title">Your Life Path in Survival</div>
    <div class="section-body">{section_life_path}</div>
  </div>

  <hr class="divider" />

  <div class="section">
    <div class="section-label">Self-Love Assessment</div>
    <div class="section-title">Where You Are Right Now</div>
    <div class="section-body">{section_self_love}</div>
  </div>

  <hr class="divider" />

  <div class="closing">
    <div class="closing-title">Closing Activation</div>
    <div class="closing-body">
      Survival mode is not a character flaw. It is a nervous system response that learned, at some
      point, that it had to. The data above does not tell you what is wrong with you. It tells you
      the shape of what learned to protect you, and where those same protections are now costing you
      the life your Soul Blueprint was designed to create.<br /><br />
      The Soul Blueprint system does not give advice. It activates Rebirths.<br /><br />
      This document is one.<br /><br />
      You are not behind. You are not broken. You are at a beginning that your data has been
      pointing toward for longer than you know.<br /><br />
      Welcome to your Rebirth.
    </div>
  </div>

  <div class="footer">
    Phoenix Rebirth &nbsp;|&nbsp; soulReady &nbsp;|&nbsp; Soul Blueprint System
  </div>

</body>
</html>"""
    return html


def register_survival_mode_pdf_route(app):
    @app.route('/generate-survival-mode-pdf', methods=['POST'])
    def generate_survival_mode_pdf():
        data = request.get_json(force=True, silent=True) or {}
        pdf_html = generate_survival_mode_html(
            client_name=data.get('client_name', ''),
            hd_type=data.get('hd_type', ''),
            hd_authority=data.get('hd_authority', ''),
            moon=data.get('moon', ''),
            north_node=data.get('north_node', ''),
            south_node=data.get('south_node', ''),
            life_path=data.get('life_path', ''),
            attachment_style=data.get('attachment_style', ''),
            self_love_score=data.get('self_love_score', 0),
            self_love_result=data.get('self_love_result', ''),
        )
        return jsonify({'pdf_html': pdf_html})
