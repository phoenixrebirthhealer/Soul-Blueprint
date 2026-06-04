<?php
// Phoenix Rebirth | Hebrew Metatron's Cube Frequency System
// Proprietary — Christina Stevens
// Hebrew letter values are COMPLETELY SEPARATE from numerology values. Never mix them.

const HEBREW_SINGLE = [
    'A'=>1,  'B'=>2,  'C'=>11, 'D'=>4,  'E'=>5,  'F'=>17, 'G'=>3,  'H'=>5,
    'I'=>10, 'J'=>10, 'K'=>19, 'L'=>12, 'M'=>13, 'N'=>14, 'O'=>6,  'P'=>17,
    'Q'=>19, 'R'=>20, 'S'=>15, 'T'=>9,  'U'=>6,  'V'=>6,  'W'=>6,  'X'=>15,
    'Y'=>16, 'Z'=>7,
];

// Combination letters always take precedence over two singles
const HEBREW_COMBO = [
    'AH'=>5, 'CH'=>8, 'WH'=>16, 'TZ'=>18, 'SH'=>21, 'TA'=>22, 'TH'=>22,
];

// Final letter values: only when M or P appear at the end of the last word in the full legal name
const HEBREW_FINAL = ['M'=>12, 'P'=>12];

const FIBONACCI_POS = [1, 2, 3, 5, 8, 13, 21];

const HEBREW_ELEMENT_MAP = [
    'Void'  => [0],
    'Fire'  => [3, 10, 11, 15, 21],
    'Water' => [8, 13, 14, 18],
    'Earth' => [2, 4, 6, 9, 16, 19, 22],
    'Air'   => [1, 5, 7, 12, 17, 20],
];

const HEBREW_LETTER_REF = [
    0  => ['name' => 'The Fool', 'element' => 'Void',  'meaning' => 'Pure potential. Anticipation. The soul that has leaped before and KNOWS. The center from which all journeys begin.'],
    1  => ['name' => 'Aleph',   'element' => 'Air',   'meaning' => 'The silent breath. The threshold. The void before sound.'],
    2  => ['name' => 'Bet',     'element' => 'Earth', 'meaning' => 'The sacred container. The house that holds what is created.'],
    3  => ['name' => 'Gimel',   'element' => 'Fire',  'meaning' => 'The camel. Bridge between worlds. Movement across wilderness.'],
    4  => ['name' => 'Dalet',   'element' => 'Earth', 'meaning' => 'The door. The threshold. The passage between what was and what is.'],
    5  => ['name' => 'Heh',     'element' => 'Air',   'meaning' => 'The divine breath. The window of revelation. Presence.'],
    6  => ['name' => 'Vav',     'element' => 'Earth', 'meaning' => 'The nail. The connector between heaven and earth.'],
    7  => ['name' => 'Zayin',   'element' => 'Air',   'meaning' => 'The sword of discernment. Divinity as protection.'],
    8  => ['name' => 'Chet',    'element' => 'Water', 'meaning' => 'CHAI. Life itself. The sacred container where life grows.'],
    9  => ['name' => 'Tet',     'element' => 'Earth', 'meaning' => 'The serpent. The hidden goodness coiled and waiting to rise.'],
    10 => ['name' => 'Yod',     'element' => 'Fire',  'meaning' => 'The divine spark. Smallest letter containing greatest power.'],
    11 => ['name' => 'Kaf',     'element' => 'Fire',  'meaning' => 'The open palm. Power received and held.'],
    12 => ['name' => 'Lamed',   'element' => 'Air',   'meaning' => 'The teacher reaching toward heaven.'],
    13 => ['name' => 'Mem',     'element' => 'Water', 'meaning' => 'The primordial waters. The unconscious depths.'],
    14 => ['name' => 'Nun',     'element' => 'Water', 'meaning' => 'The fish. Faithful movement through the deep.'],
    15 => ['name' => 'Samech',  'element' => 'Fire',  'meaning' => 'The perfect circle. Divine support. Grace.'],
    16 => ['name' => 'Ayin',    'element' => 'Earth', 'meaning' => 'The eye. The spring. Clear seeing beyond the physical.'],
    17 => ['name' => 'Peh',     'element' => 'Air',   'meaning' => 'The mouth. The voice. The breath of authentic expression.'],
    18 => ['name' => 'Tzadi',   'element' => 'Water', 'meaning' => 'The fish hook. The tzaddik. Pulling wisdom from the deep.'],
    19 => ['name' => 'Qof',     'element' => 'Earth', 'meaning' => 'The horizon. The cycle that always returns.'],
    20 => ['name' => 'Resh',    'element' => 'Air',   'meaning' => 'The head. The beginning. The face turned toward what is next.'],
    21 => ['name' => 'Shin',    'element' => 'Fire',  'meaning' => 'The divine fire. Love. The letter with which God signed creation.'],
    22 => ['name' => 'Tav',     'element' => 'Earth', 'meaning' => 'The seal. The divine signature. The completion.'],
];

function hebrew_get_element($pos) {
    foreach (HEBREW_ELEMENT_MAP as $element => $positions) {
        if (in_array($pos, $positions, true)) return $element;
    }
    return null;
}

function hebrew_apply_overflow($n) {
    if ($n <= 22) return ['position' => $n, 'is_bridge' => false];
    if ($n % 9 === 0) return ['position' => intdiv($n, 9), 'is_bridge' => false];
    $result = $n / 9;
    return [
        'position'  => $n,
        'bridge'    => [(int)floor($result), (int)ceil($result)],
        'is_bridge' => true,
    ];
}

function hebrew_parse_name($name, $is_final_name = false) {
    $upper = strtoupper(preg_replace('/[^A-Za-z]/', '', $name));
    $units = [];
    $i = 0;
    $len = strlen($upper);
    while ($i < $len) {
        $two = substr($upper, $i, 2);
        if (strlen($two) === 2 && isset(HEBREW_COMBO[$two])) {
            $units[] = ['letters' => $two, 'value' => HEBREW_COMBO[$two], 'is_combo' => true, 'is_final_letter' => false];
            $i += 2;
        } else {
            $ch = $upper[$i];
            $is_last = $is_final_name && ($i === $len - 1);
            $value = ($is_last && isset(HEBREW_FINAL[$ch])) ? HEBREW_FINAL[$ch] : (HEBREW_SINGLE[$ch] ?? 0);
            $units[] = ['letters' => $ch, 'value' => $value, 'is_combo' => false, 'is_final_letter' => $is_last];
            $i++;
        }
    }
    return $units;
}

function hebrew_calc_layer1($first, $middle, $last) {
    $names = array_values(array_filter([$first, $middle, $last], 'strlen'));
    $activations = [];
    foreach ($names as $name_idx => $name) {
        $is_final = ($name_idx === count($names) - 1);
        $units = hebrew_parse_name($name, $is_final);
        foreach ($units as $pos_idx => $unit) {
            $position = $pos_idx + 1;
            $sum = $unit['value'] + $position;
            $overflow = hebrew_apply_overflow($sum);
            $activations[] = array_merge([
                'name'            => $name,
                'letters'         => $unit['letters'],
                'letter_value'    => $unit['value'],
                'position'        => $position,
                'sum'             => $sum,
                'is_combo'        => $unit['is_combo'],
                'is_final_letter' => $unit['is_final_letter'],
            ], $overflow);
        }
    }
    return $activations;
}

function hebrew_calc_layer2($day, $month, $year) {
    $year_sum = array_sum(array_map('intval', str_split((string)$year)));
    return [
        array_merge(['unit' => 'Day',   'raw' => $day],      hebrew_apply_overflow($day)),
        array_merge(['unit' => 'Month', 'raw' => $month],    hebrew_apply_overflow($month)),
        array_merge(['unit' => 'Year',  'raw' => $year_sum], hebrew_apply_overflow($year_sum)),
    ];
}

function run_hebrew_calculation($first, $middle, $last, $day, $month, $year) {
    $layer1 = hebrew_calc_layer1($first, $middle, $last);
    $layer2 = hebrew_calc_layer2($day, $month, $year);

    $l1_pos = [];
    foreach ($layer1 as $a) {
        if (!$a['is_bridge'] && $a['position'] <= 22) $l1_pos[] = $a['position'];
    }
    $l2_pos = [];
    foreach ($layer2 as $a) {
        if (!$a['is_bridge'] && $a['position'] <= 22) $l2_pos[] = $a['position'];
    }
    $all_pos = array_merge($l1_pos, $l2_pos);

    $convergence = array_values(array_intersect($l1_pos, $l2_pos));

    $element_counts = ['Fire' => 0, 'Water' => 0, 'Earth' => 0, 'Air' => 0];
    foreach ($all_pos as $pos) {
        $el = hebrew_get_element($pos);
        if ($el && $el !== 'Void' && isset($element_counts[$el])) $element_counts[$el]++;
    }

    $elemental_wounds = [];
    foreach ($element_counts as $el => $cnt) {
        if ($cnt === 0) $elemental_wounds[] = $el;
    }

    $dominant_element = null;
    $max_count = -1;
    foreach ($element_counts as $el => $cnt) {
        if ($cnt > $max_count) { $max_count = $cnt; $dominant_element = $el; }
    }

    $activation_count = array_count_values($all_pos);

    $enrich = function(array $positions) use ($activation_count) {
        return array_map(function($pos) use ($activation_count) {
            $ref = HEBREW_LETTER_REF[$pos] ?? [];
            return array_merge($ref, [
                'position'         => $pos,
                'is_fibonacci'     => in_array($pos, FIBONACCI_POS, true),
                'element'          => hebrew_get_element($pos),
                'activation_count' => $activation_count[$pos] ?? 1,
            ]);
        }, $positions);
    };

    return [
        'first_name'            => $first,
        'middle_name'           => $middle,
        'last_name'             => $last,
        'date_of_birth'         => ['day' => $day, 'month' => $month, 'year' => $year],
        'layer1'                => $layer1,
        'layer2'                => $layer2,
        'convergence_points'    => $convergence,
        'convergence_details'   => $enrich($convergence),
        'layer1_positions'      => $enrich($l1_pos),
        'layer2_positions'      => $enrich($l2_pos),
        'element_counts'        => $element_counts,
        'elemental_wounds'      => array_values($elemental_wounds),
        'dominant_element'      => $dominant_element,
        'fibonacci_activations' => array_values(array_filter($all_pos, function($p) { return in_array($p, FIBONACCI_POS, true); })),
        'activation_count'      => $activation_count,
    ];
}
